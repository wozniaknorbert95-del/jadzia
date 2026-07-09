"""Internal action soft-undo (CE-05 / N5)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Dict, Optional

from agent.commander.audit import append_audit
from agent.commander.authz import actor_from_payload
from agent.db import db_commander_get_setting, db_commander_set_setting, db_get_calendar_entry, db_update_calendar_entry

UNDO_WINDOW_SECONDS = 60


def register_internal_undo(entry_id: str, previous_status: str) -> None:
    key = f"undo:cal:{entry_id}"
    payload = {
        "previous_status": previous_status,
        "registered_at": datetime.now(timezone.utc).isoformat(),
    }
    db_commander_set_setting(key, json.dumps(payload))


def revert_internal_action(entry_id: str, auth_payload: Optional[Dict]) -> Dict:
    key = f"undo:cal:{entry_id}"
    row = db_commander_get_setting(key)
    if not row:
        return {"status": "error", "message": "No undo window for this action"}

    try:
        data = json.loads(row["value_json"])
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid undo record"}

    registered = datetime.fromisoformat(data["registered_at"].replace("Z", "+00:00"))
    if registered.tzinfo is None:
        registered = registered.replace(tzinfo=timezone.utc)
    elapsed = (datetime.now(timezone.utc) - registered).total_seconds()
    if elapsed > UNDO_WINDOW_SECONDS:
        return {"status": "error", "message": "Undo window expired"}

    try:
        internal_id = int(entry_id)
    except ValueError:
        return {"status": "error", "message": "Invalid entry_id"}

    cal = db_get_calendar_entry(internal_id)
    if not cal:
        return {"status": "error", "message": "Entry not found"}

    prev = data["previous_status"]
    db_update_calendar_entry(internal_id, {"status": prev})
    db_commander_set_setting(key, json.dumps({"used": True}))

    actor_id, actor_role = actor_from_payload(auth_payload)
    append_audit(
        actor_id=actor_id,
        actor_role=actor_role,
        action="internal_undo",
        source="commander",
        target_type="calendar_entry",
        target_id=entry_id,
        before={"status": cal.get("status")},
        after={"status": prev},
        reason="60s_soft_undo",
        risk_tier="low",
    )
    return {"status": "success", "reverted_to": prev}
