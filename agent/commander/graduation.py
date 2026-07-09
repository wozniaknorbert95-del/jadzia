"""HITL→HOTL graduation logic."""

from __future__ import annotations

import json
from typing import Dict

from agent.commander.constants import GRADUATION_DEFAULTS
from agent.db import db_commander_feedback_stats, db_commander_insert_feedback


def record_feedback(
    action_type: str,
    feedback_type: str,
    payload: Dict | None,
    actor_id: str | None,
) -> Dict:
    db_commander_insert_feedback(
        action_type=action_type,
        feedback_type=feedback_type,
        payload_json=json.dumps(payload) if payload else None,
        actor_id=actor_id,
    )
    return graduation_status(action_type)


def graduation_status(action_type: str) -> Dict:
    stats = db_commander_feedback_stats(action_type)
    min_approvals = GRADUATION_DEFAULTS["min_approvals"]
    max_override = GRADUATION_DEFAULTS["max_override_rate_pct"]
    mode = "HITL"
    if (
        stats["approved_without_edit"] >= min_approvals
        and stats["override_rate_pct"] < max_override
    ):
        mode = "HOTL"
    return {
        "action_type": action_type,
        "mode": mode,
        "stats": stats,
        "thresholds": GRADUATION_DEFAULTS,
    }
