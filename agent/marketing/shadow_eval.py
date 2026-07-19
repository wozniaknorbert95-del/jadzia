"""
Shadow eval pack — trust test before MB_MODE=propose.

Canonical pack (v2, Telegram-first):
  - Stratified sample of shadow decisions (not dump-all)
  - Dowódca scores: agree=1.0 / partial=0.5 / disagree=0.0
  - Gate: accuracy ≥ 0.70 AND n_scored ≥ 20 over rolling 14d
  - Prefer 2 consecutive weeks green before GO propose
"""

from __future__ import annotations

import csv
import io
import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agent.db import (
    db_get_marketing_shadow,
    db_list_marketing_shadow,
    db_list_marketing_shadow_eval_joined,
    db_list_scored_evals,
    db_upsert_marketing_shadow_eval,
)

logger = logging.getLogger(__name__)

SCORE_WEIGHTS = {
    "agree": 1.0,
    "partial": 0.5,
    "disagree": 0.0,
}

# Skip pure "nothing happened" spam unless pack is thin
_SKIP_RULES_WHEN_RICH = frozenset({"HEU_NO_SIGNAL"})

# Prefer actionable / high-severity for Dowódca time
_ACTION_PRIORITY = {
    "CRITICAL": 0,
    "ACTION": 1,
    "WATCH": 2,
    "INFO": 3,
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def record_eval_score(
    action_id: str,
    eval_score: str,
    scorer: str = "dowodca",
) -> Dict[str, Any]:
    score = (eval_score or "").strip().lower()
    if score not in SCORE_WEIGHTS:
        return {
            "ok": False,
            "error": f"invalid score={eval_score}; use agree|partial|disagree",
        }
    if not db_get_marketing_shadow(action_id):
        return {"ok": False, "error": f"unknown action_id={action_id}"}
    ok = db_upsert_marketing_shadow_eval(action_id, score, scorer=scorer)
    return {"ok": ok, "action_id": action_id, "eval_score": score}


def compute_accuracy(window_days: int = 14) -> Dict[str, Any]:
    """
    Rolling accuracy from scored evals.
    Gate green: accuracy >= 0.70 AND n_scored >= 20.
    """
    rows = db_list_scored_evals(window_days=window_days)
    n = len(rows)
    if n == 0:
        return {
            "window_days": window_days,
            "n_scored": 0,
            "accuracy": None,
            "gate_ready": False,
            "gate_reason": "no_scores",
            "breakdown": {"agree": 0, "partial": 0, "disagree": 0},
            "by_rule": {},
            "formula": "avg(agree=1, partial=0.5, disagree=0)",
            "threshold": 0.70,
            "min_n": 20,
            "as_of": _utc_now_iso(),
        }

    breakdown = {"agree": 0, "partial": 0, "disagree": 0}
    by_rule: Dict[str, List[float]] = defaultdict(list)
    total = 0.0
    for r in rows:
        s = (r.get("eval_score") or "").lower()
        if s not in SCORE_WEIGHTS:
            continue
        w = SCORE_WEIGHTS[s]
        total += w
        breakdown[s] = breakdown.get(s, 0) + 1
        rid = r.get("heuristic_rule_id") or "?"
        by_rule[rid].append(w)

    accuracy = round(total / n, 4)
    gate_ready = accuracy >= 0.70 and n >= 20
    if not gate_ready:
        reason = "below_threshold" if accuracy < 0.70 else "n_scored_lt_20"
    else:
        reason = "ok"

    by_rule_avg = {
        k: round(sum(v) / len(v), 4) for k, v in sorted(by_rule.items()) if v
    }

    return {
        "window_days": window_days,
        "n_scored": n,
        "accuracy": accuracy,
        "gate_ready": gate_ready,
        "gate_reason": reason,
        "breakdown": breakdown,
        "by_rule": by_rule_avg,
        "formula": "avg(agree=1, partial=0.5, disagree=0)",
        "threshold": 0.70,
        "min_n": 20,
        "consecutive_weeks_note": (
            "Prefer 2 consecutive weeks gate_ready=true before GO propose"
        ),
        "as_of": _utc_now_iso(),
    }


def _severity_rank(row: Dict[str, Any]) -> int:
    payload = row.get("payload") or {}
    sev = (payload.get("severity") or "INFO").upper()
    return _ACTION_PRIORITY.get(sev, 9)


def select_stratified_pack(
    *,
    target_n: int = 12,
    window_days: int = 7,
    max_per_rule: int = 3,
) -> List[Dict[str, Any]]:
    """
    Weekly-ish sample: prefer unscored, actionable, diverse rules.
    Cap per heuristic_rule_id; deprioritize HEU_NO_SIGNAL when enough others.
    """
    pool = db_list_marketing_shadow_eval_joined(
        window_days=window_days,
        only_unscored=True,
        limit=300,
    )
    if not pool:
        # Fallback: recently scored-or-not from wider window
        pool = db_list_marketing_shadow_eval_joined(
            window_days=max(window_days, 14),
            only_unscored=False,
            limit=300,
        )
        pool = [r for r in pool if not r.get("eval_score")]

    rich = [r for r in pool if r.get("heuristic_rule_id") not in _SKIP_RULES_WHEN_RICH]
    use = rich if len(rich) >= max(4, target_n // 2) else pool

    use_sorted = sorted(
        use,
        key=lambda r: (
            _severity_rank(r),
            0 if r.get("would_execute") else 1,
            r.get("created_at") or "",
        ),
    )

    picked: List[Dict[str, Any]] = []
    per_rule: Dict[str, int] = defaultdict(int)
    for row in use_sorted:
        rid = row.get("heuristic_rule_id") or "?"
        if per_rule[rid] >= max_per_rule:
            continue
        picked.append(row)
        per_rule[rid] += 1
        if len(picked) >= target_n:
            break
    return picked


def build_eval_pack(
    *,
    limit: int = 12,
    window_days: int = 7,
    stratified: bool = True,
) -> Dict[str, Any]:
    """
    Build Dowódca scoring pack (Telegram cards / CSV / JSON).
    Default: stratified sample (v2). Set stratified=False for raw dump (v1).
    """
    if stratified:
        rows = select_stratified_pack(target_n=limit, window_days=window_days)
    else:
        rows = db_list_marketing_shadow(limit=limit)

    decisions = []
    for r in rows:
        decisions.append(
            {
                "action_id": r.get("action_id"),
                "created_at": r.get("created_at"),
                "heuristic_rule_id": r.get("heuristic_rule_id"),
                "proposed_action": r.get("proposed_action"),
                "governance_result": r.get("governance_result"),
                "would_execute": bool(r.get("would_execute")),
                "mb_mode": r.get("mb_mode"),
                "hitl_status": r.get("hitl_status"),
                "rationale_nl": (r.get("payload") or {}).get("rationale_nl")
                or (r.get("llm_rationale_nl") or ""),
                "severity": (r.get("payload") or {}).get("severity"),
                "eval_score": r.get("eval_score"),  # blank until scored
            }
        )

    accuracy = compute_accuracy(window_days=14)
    return {
        "generated_at": _utc_now_iso(),
        "n": len(decisions),
        "pack_version": "v2_stratified" if stratified else "v1_dump",
        "window_days": window_days,
        "scoring": {
            "agree": 1.0,
            "partial": 0.5,
            "disagree": 0.0,
            "gate": "accuracy>=0.70 AND n_scored>=20 over 14d",
            "channel": "telegram_/mb_eval_preferred",
        },
        "accuracy_snapshot": accuracy,
        "decisions": decisions,
        "score_blank": [
            {"action_id": d["action_id"], "eval_score": ""} for d in decisions
        ],
    }


def eval_pack_to_json(pack: Dict[str, Any]) -> str:
    import json

    return json.dumps(pack, ensure_ascii=False, indent=2)


def eval_pack_to_csv(pack: Dict[str, Any]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(
        buf,
        fieldnames=[
            "action_id",
            "created_at",
            "heuristic_rule_id",
            "proposed_action",
            "severity",
            "would_execute",
            "rationale_nl",
            "eval_score",
        ],
    )
    w.writeheader()
    for d in pack.get("decisions") or []:
        w.writerow(
            {
                "action_id": d.get("action_id"),
                "created_at": d.get("created_at"),
                "heuristic_rule_id": d.get("heuristic_rule_id"),
                "proposed_action": d.get("proposed_action"),
                "severity": d.get("severity"),
                "would_execute": d.get("would_execute"),
                "rationale_nl": (d.get("rationale_nl") or "")[:500],
                "eval_score": d.get("eval_score") or "",
            }
        )
    return buf.getvalue()


def format_eval_card(decision: Dict[str, Any], idx: int, total: int) -> str:
    return (
        f"📋 Eval {idx}/{total}\n"
        f"Rule: {decision.get('heuristic_rule_id')}\n"
        f"Action: {decision.get('proposed_action')}\n"
        f"Severity: {decision.get('severity') or '?'}\n"
        f"Would exec: {decision.get('would_execute')}\n"
        f"{(decision.get('rationale_nl') or '')[:400]}\n"
        f"action_id={decision.get('action_id')}\n"
        f"Oceń: zgadzam się / częściowo / nie"
    )
