"""Commander settings (delegation, escalation)."""

from __future__ import annotations

import json
from typing import Any, Dict

from agent.db import db_commander_get_setting, db_commander_set_setting

DEFAULTS = {
    "delegat_email": "",
    "ui_language": "pl",
    "daily_action_budget": 200,
    "dowodca_last_active_at": None,
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
    return out


def update_settings(updates: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in updates.items():
        if key in DEFAULTS:
            db_commander_set_setting(key, json.dumps(value))
    return get_settings()
