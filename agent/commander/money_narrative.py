"""Honest money/risk narrative for Mission Control (DI-S6).

Counts + blockers only. Never emit vanity € / green revenue totals on L1.
Order Desk remains PARKED (EV-W2-010) until S7 SoT.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agent.commander.sla import freshness_status

CTA_SCORE_THRESHOLD = 40
HOT_LEAD_SCORE = 80
ORDER_DESK = {"status": "PARKED", "evidence": "EV-W2-010"}


def _utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _lead_counts(leads: List[Dict[str, Any]]) -> Dict[str, int]:
    open_n = hot_n = cta_n = 0
    for lead in leads:
        if lead.get("is_test") is True:
            continue
        disposition = (lead.get("disposition") or "open").lower()
        if disposition in ("closed", "snoozed"):
            continue
        open_n += 1
        score = int(lead.get("game_score") or 0)
        if score >= HOT_LEAD_SCORE:
            hot_n += 1
        if score >= CTA_SCORE_THRESHOLD:
            cta_n += 1
    return {"open_leads": open_n, "hot_leads": hot_n, "cta_band_leads": cta_n}


def _ga4_honesty(snap: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    generated_at = (snap or {}).get("generated_at")
    fresh = freshness_status("ga4", generated_at)
    # Wizard funnel fields: expose only as null placeholders — never invent sessions.
    # purchase_revenue intentionally omitted from L1 narrative.
    return {
        "freshness": fresh.get("status"),
        "generated_at": generated_at,
        "sync_status": (snap or {}).get("sync_status"),
        "wizard_sessions": None,
        "wizard_conversions": None,
        "usable_for_money": False,
        "note": "GA4 money/funnel not claimed on L1 — freshness chip only; no vanity euro",
    }


def _top_risk_from_brief(brief: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    nba = brief.get("nba")
    if not nba:
        return None
    return {
        "title": nba.get("title"),
        "owner": nba.get("owner") or "Dowódca",
        "queue_type": nba.get("queue_type"),
        "severity": nba.get("severity"),
        "evidence_ts": nba.get("evidence_ts") or nba.get("created_at"),
        "approval_class": nba.get("approval_class"),
        "why_now": nba.get("why_now"),
    }


def build_money_risk_narrative(
    *,
    leads: Optional[List[Dict[str, Any]]] = None,
    analytics_snap: Optional[Dict[str, Any]] = None,
    brief: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build read-only money/risk narrative. Inject deps for unit tests."""
    from agent.db import db_list_analytics_snapshots, db_list_leads

    if leads is None:
        leads = db_list_leads(limit=50)
    if analytics_snap is None:
        rows = db_list_analytics_snapshots(limit=1)
        analytics_snap = rows[0] if rows else None
    if brief is None:
        from agent.commander.queue import build_director_brief_from_queue

        brief = build_director_brief_from_queue(max_secondary=0)

    counts = _lead_counts(leads)
    ga4 = _ga4_honesty(analytics_snap)
    top_risk = _top_risk_from_brief(brief or {})

    has_lead_signal = (
        counts["open_leads"] > 0
        or counts["hot_leads"] > 0
        or counts["cta_band_leads"] > 0
    )
    if has_lead_signal or top_risk:
        status = "partial"
        q1 = (
            f"Pipeline signal: {counts['open_leads']} open lead(s), "
            f"{counts['hot_leads']} hot, {counts['cta_band_leads']} CTA-band. "
            "No live euro claimed — Order Desk PARKED."
        )
        cta = {
            "label": "Focus queue",
            "action": "focus_queue",
            "target": "queue",
        }
    else:
        status = "insufficient_data"
        q1 = (
            "Insufficient money/risk signal — no open leads and no ranked NBA. "
            "Verify Wizard/lead intake; do not invent revenue."
        )
        cta = {
            "label": "Open Wizard",
            "action": "open_wizard",
            "target": "https://zzpackage.flexgrafik.nl/wizard/",
        }

    event_ids = [ORDER_DESK["evidence"]]
    if top_risk and top_risk.get("queue_type"):
        event_ids.append(f"nba:{top_risk['queue_type']}")

    return {
        "status": status,
        "as_of": _utcnow(),
        "q1": q1,
        "pipeline": {
            **counts,
            "wizard_sessions": ga4["wizard_sessions"],
            "wizard_conversions": ga4["wizard_conversions"],
            "order_desk": dict(ORDER_DESK),
        },
        "top_risk": top_risk,
        "freshness": {
            "ga4": ga4["freshness"],
            "ga4_generated_at": ga4["generated_at"],
        },
        "ga4": ga4,
        "honesty": [
            "No vanity euro totals on Mission Control L1",
            "Order Desk PARKED · EV-W2-010",
            "GA4 purchase revenue not shown as money KPI",
        ],
        "cta": cta,
        "event_ids": event_ids,
        "policy_ref": "DI-S6",
    }
