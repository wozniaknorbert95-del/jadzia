"""Commander settings (delegation, escalation)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from agent.db import db_commander_get_setting, db_commander_set_setting

DEFAULTS = {
    "delegat_email": "",
    "delegat_telegram_chat_id": "",
    "ui_language": "pl",
    "daily_action_budget": 200,
    "dowodca_last_active_at": None,
    "commander_roles": {},
}


def get_settings() -> Dict[str, Any]:
    out = dict(DEFAULTS)
    for key in DEFAULTS:
        row = db_commander_get_setting(key)
        if row:
            try:
                out[key] = json.loads(row["value_json"])
            except json.JSONDecodeError:
                out[key] = row["value_json"]
    out["delegat_configured"] = bool(out.get("delegat_email"))
    return out


def update_settings(updates: Dict[str, Any]) -> Dict[str, Any]:
    allowed = set(DEFAULTS.keys())
    for key, value in updates.items():
        if key in allowed:
            db_commander_set_setting(key, json.dumps(value))
    return get_settings()


def touch_dowodca_activity(actor_id: Optional[str] = None) -> None:
    """Record Dowódca activity for N6 inactive detection."""
    if actor_id == "worker":
        return
    db_commander_set_setting(
        "dowodca_last_active_at",
        json.dumps(datetime.now(timezone.utc).isoformat()),
    )


def get_role_for_user(user_id: str) -> Optional[str]:
    settings = get_settings()
    roles = settings.get("commander_roles") or {}
    return roles.get(user_id)
