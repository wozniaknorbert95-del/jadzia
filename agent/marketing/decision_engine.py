"""Marketing Brain decision engine — facts → Decision → shadow + events."""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from agent.db import (
    db_enqueue_brain_event,
    db_insert_marketing_hypothesis,
    db_insert_marketing_shadow,
    db_list_active_quality_flags,
    db_list_marketing_facts,
    db_rolling_net_margin_pct,
)
from agent.marketing.heuristics import Decision, evaluate

logger = logging.getLogger(__name__)


def get_mb_mode() -> str:
    """shadow (default) | propose | act — F1 stays shadow unless overridden."""
    return (os.getenv("MB_MODE") or "shadow").strip().lower()


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _fact_value(metric_key: str, channel: str = "all") -> Optional[float]:
    rows = db_list_marketing_facts(metric_key=metric_key, limit=20)
    for row in rows:
        if channel == "all" or row.get("channel") == channel:
            return float(row["value"])
    return None


def _organic_candidates_from_facts() -> List[Dict[str, Any]]:
    """
    Organic winner candidates from DTL facts when present.
    Expects metric organic_er_lift_pct / organic_link_clicks_lift_pct per post channel.
    Empty until organic metrics ingest lands — heuristics then skip O2P.
    """
    candidates: List[Dict[str, Any]] = []
    for metric in ("organic_er_lift_pct", "organic_link_clicks_lift_pct"):
        for row in db_list_marketing_facts(metric_key=metric, limit=30):
            lift = float(row.get("value") or 0)
            dims = row.get("dims") or {}
            candidates.append(
                {
                    "post_id": dims.get("post_id") or row.get("channel"),
                    "channel": row.get("channel"),
                    "lift_pct": lift,
                    "metric": metric,
                    "quality_clean": True,
                }
            )
    return candidates


def build_facts_bundle() -> Dict[str, Any]:
    flags = db_list_active_quality_flags(limit=50)
    return {
        "quality_flags": flags,
        "margin_avg_pct": db_rolling_net_margin_pct(limit=50),
        "attribution_coverage_pct": _fact_value("attribution_coverage_pct", "all"),
        "organic_candidates": _organic_candidates_from_facts(),
        "as_of": _utc_now(),
    }


def _new_action_id() -> str:
    return f"mb_{uuid.uuid4().hex[:16]}"


def persist_decision(decision: Decision, facts_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Write shadow log + hypothesis + brain_event. Returns action record."""
    from agent.marketing.campaign_memory import enrich_decision_with_memory, upsert_decision

    mode = get_mb_mode()
    action_id = _new_action_id()
    # Shadow mode: never allow external side-effects even if would_execute
    would = bool(decision.would_execute) and mode != "shadow"
    gov = decision.governance_result
    if mode == "shadow":
        gov = "deny" if decision.proposed_action in ("block_scale",) else "review"

    mem = enrich_decision_with_memory(decision)
    rationale = decision.rationale_nl + (mem.get("memory_warning") or "")
    dims = dict(decision.dims or {})
    dims["memory_source"] = mem.get("memory_source")
    dims["memory_hits"] = mem.get("memory_hits")
    dims["memory_negative_hits"] = mem.get("memory_negative_hits")

    db_insert_marketing_shadow(
        {
            "action_id": action_id,
            "observed_facts_ref": facts_bundle.get("as_of"),
            "proposed_action": decision.proposed_action,
            "heuristic_rule_id": decision.heuristic_rule_id,
            "llm_rationale_nl": rationale,
            "would_execute": would,
            "governance_result": gov,
            "mb_mode": mode,
            "hitl_status": "pending",
            "payload": {
                "severity": decision.severity,
                "dims": dims,
                "memory": {
                    "source": mem.get("memory_source"),
                    "hits": mem.get("hits") or [],
                    "negative_hits": mem.get("memory_negative_hits"),
                },
                "facts_summary": {
                    "margin_avg_pct": facts_bundle.get("margin_avg_pct"),
                    "attribution_coverage_pct": facts_bundle.get("attribution_coverage_pct"),
                    "red_flags": len(
                        [
                            f
                            for f in (facts_bundle.get("quality_flags") or [])
                            if f.get("severity") in ("critical", "red")
                        ]
                    ),
                },
            },
        }
    )

    upsert_decision(
        {
            "action_id": action_id,
            "heuristic_rule_id": decision.heuristic_rule_id,
            "proposed_action": decision.proposed_action,
            "llm_rationale_nl": rationale,
            "governance_result": gov,
            "hitl_status": "pending",
            "payload": {"severity": decision.severity},
        }
    )

    hyp_id = f"hyp_{uuid.uuid4().hex[:12]}"
    review_at = (
        datetime.now(timezone.utc) + timedelta(days=3)
    ).replace(microsecond=0).isoformat()
    db_insert_marketing_hypothesis(
        {
            "hypothesis_id": hyp_id,
            "statement": (
                f"If we act on {decision.heuristic_rule_id} "
                f"({decision.proposed_action}), North Star improves."
            ),
            "proposed_action_ref": action_id,
            "status": "open",
            "review_at": review_at,
        }
    )

    db_enqueue_brain_event(
        {
            "event_type": "campaign.decision.proposed",
            "source_brain": "mb",
            "correlation_id": action_id,
            "payload": {
                "action_id": action_id,
                "hypothesis_id": hyp_id,
                "proposed_action": decision.proposed_action,
                "heuristic_rule_id": decision.heuristic_rule_id,
                "severity": decision.severity,
                "mb_mode": mode,
            },
        }
    )

    return {
        "action_id": action_id,
        "hypothesis_id": hyp_id,
        "decision": decision,
        "mb_mode": mode,
        "would_execute": would,
        "memory_source": mem.get("memory_source"),
        "memory_hits": mem.get("memory_hits"),
        "memory_negative_hits": mem.get("memory_negative_hits"),
    }


def run_decision_cycle() -> Dict[str, Any]:
    """Full evaluate → persist. Does not send Telegram (caller/runtime)."""
    bundle = build_facts_bundle()
    decisions = evaluate(bundle)
    # Persist actionable / non-noise decisions; always keep first
    to_persist = [
        d
        for d in decisions
        if d.heuristic_rule_id != "HEU_NO_SIGNAL" or len(decisions) == 1
    ]
    records = []
    for d in to_persist:
        # Skip pure INFO hold noise when other decisions exist
        if d.heuristic_rule_id == "HEU_NO_SIGNAL" and len(to_persist) > 1:
            continue
        records.append(persist_decision(d, bundle))

    mem_sources = {r.get("memory_source") for r in records if r.get("memory_source")}
    logger.info(
        "[mb.decision] mode=%s persisted=%s flags=%s memory_sources=%s",
        get_mb_mode(),
        len(records),
        len(bundle.get("quality_flags") or []),
        sorted(mem_sources),
    )
    return {
        "mb_mode": get_mb_mode(),
        "facts_as_of": bundle.get("as_of"),
        "decisions_evaluated": len(decisions),
        "records": records,
        "memory_sources": sorted(mem_sources),
    }
