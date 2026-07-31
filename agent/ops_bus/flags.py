"""Ops Bus kill-switch via commander_settings."""

from __future__ import annotations

import json
import logging

logger = logging.getLogger(__name__)

SETTING_KEY = "ops_bus_enabled"


def is_ops_bus_enabled() -> bool:
    """Default ON when unset; explicit false/0/off disables emit + API list."""
    from agent.db import db_commander_get_setting

    row = db_commander_get_setting(SETTING_KEY)
    if not row:
        return True
    raw = row.get("value_json")
    if raw is None:
        return True
    try:
        value = json.loads(raw) if isinstance(raw, str) else raw
    except (TypeError, json.JSONDecodeError):
        logger.warning("[OpsBus] invalid ops_bus_enabled setting; default ON")
        return True
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() not in {"0", "false", "off", "no"}
    if isinstance(value, dict) and "enabled" in value:
        return bool(value["enabled"])
    return True


def set_ops_bus_enabled(enabled: bool) -> bool:
    from agent.db import db_commander_set_setting

    return db_commander_set_setting(SETTING_KEY, json.dumps(bool(enabled)))
