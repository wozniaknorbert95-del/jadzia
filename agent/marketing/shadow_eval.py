"""Shadow Evaluation Pack — Dowódca accuracy review (≥70% gate to propose)."""

from __future__ import annotations

import csv
import io
import json
from typing import Any, Dict, List, Optional

from agent.db import db_list_marketing_shadow

# Scoring rubric (SoT) — Agree / Partial / Disagree
EVAL_RUBRIC = {
    "target_accuracy_pct": 70.0,
    "scores": {
        "agree": "Decision matches what Dowódca would do",
        "partial": "Direction OK, wrong severity/timing/channel",
        "disagree": "Wrong or harmful vs Dowódca judgment",
    },
    "formula": "accuracy = (agree + 0.5*partial) / scored * 100; gate ≥70%",
    "window_days": 14,
}


def build_eval_pack(limit: int = 50) -> Dict[str, Any]:
    rows = db_list_marketing_shadow(limit=limit)
    items: List[Dict[str, Any]] = []
    for row in rows:
        payload = row.get("payload") or {}
        items.append(
            {
                "action_id": row.get("action_id"),
                "heuristic_rule_id": row.get("heuristic_rule_id"),
                "proposed_action": row.get("proposed_action"),
                "severity": payload.get("severity"),
                "rationale_nl": row.get("llm_rationale_nl"),
                "hitl_status": row.get("hitl_status"),
                "governance_result": row.get("governance_result"),
                "mb_mode": row.get("mb_mode"),
                "created_at": row.get("created_at"),
                "score_blank": "",  # agree|partial|disagree — fill by Dowódca
            }
        )
    return {
        "ok": True,
        "rubric": EVAL_RUBRIC,
        "count": len(items),
        "items": items,
        "mb_mode": (rows[0].get("mb_mode") if rows else "shadow"),
    }


def eval_pack_to_csv(pack: Optional[Dict[str, Any]] = None, limit: int = 50) -> str:
    pack = pack or build_eval_pack(limit=limit)
    buf = io.StringIO()
    fields = [
        "action_id",
        "heuristic_rule_id",
        "proposed_action",
        "severity",
        "rationale_nl",
        "hitl_status",
        "governance_result",
        "mb_mode",
        "created_at",
        "score_blank",
    ]
    w = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    for item in pack.get("items") or []:
        w.writerow(item)
    return buf.getvalue()


def eval_pack_to_json(pack: Optional[Dict[str, Any]] = None, limit: int = 50) -> str:
    pack = pack or build_eval_pack(limit=limit)
    return json.dumps(pack, ensure_ascii=False, indent=2)
