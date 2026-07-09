"""HITL→HOTL graduation logic."""

from __future__ import annotations

import json
from typing import Dict, Optional

from agent.commander.constants import GRADUATION_DEFAULTS
from agent.db import db_commander_feedback_stats, db_commander_insert_feedback


def record_feedback(
    action_type: str,
    feedback_type: str,
    payload: Dict | None,
    actor_id: str | None,
) -> Dict:
    confidence = None
    if payload and "confidence" in payload:
        confidence = float(payload["confidence"])
    db_commander_insert_feedback(
        action_type=action_type,
        feedback_type=feedback_type,
        payload_json=json.dumps(payload) if payload else None,
        actor_id=actor_id,
        confidence=confidence,
    )
    _maybe_revert_on_spike(action_type)
    return graduation_status(action_type)


def _maybe_revert_on_spike(action_type: str) -> None:
    stats = db_commander_feedback_stats(action_type, days=7)
    spike_threshold = GRADUATION_DEFAULTS["max_override_rate_pct"] * 2
    if stats["override_rate_pct"] >= spike_threshold and stats["total"] >= 5:
        from agent.db import db_commander_set_setting

        db_commander_set_setting(
            f"graduation:reverted:{action_type}",
            json.dumps({"reason": "override_spike", "rate": stats["override_rate_pct"]}),
        )


def is_hotl_mode(action_type: str) -> bool:
    from agent.db import db_commander_get_setting

    if db_commander_get_setting(f"graduation:reverted:{action_type}"):
        return False
    return graduation_status(action_type)["mode"] == "HOTL"


def graduation_status(action_type: str) -> Dict:
    stats = db_commander_feedback_stats(action_type)
    min_approvals = GRADUATION_DEFAULTS["min_approvals"]
    max_override = GRADUATION_DEFAULTS["max_override_rate_pct"]
    min_confidence = GRADUATION_DEFAULTS.get("min_confidence_avg", 0.7)
    mode = "HITL"
    if (
        stats["approved_without_edit"] >= min_approvals
        and stats["override_rate_pct"] < max_override
        and stats.get("confidence_avg", 1.0) >= min_confidence
    ):
        mode = "HOTL"
    return {
        "action_type": action_type,
        "mode": mode,
        "stats": stats,
        "thresholds": GRADUATION_DEFAULTS,
    }
