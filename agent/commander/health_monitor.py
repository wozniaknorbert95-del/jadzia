"""Dashboard-down health monitor (N16)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Optional

import urllib.request

from agent.db import db_commander_get_setting, db_commander_set_setting

logger = logging.getLogger(__name__)

DOWN_THRESHOLD_SECONDS = 300
HEALTH_URL = "http://127.0.0.1:8000/worker/health"
COMMANDER_URL = "http://127.0.0.1:8000/commander/"


def _http_ok(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def check_commander_health() -> Optional[str]:
    """Return alert message if dashboard was down >5min, else None."""
    now = datetime.now(timezone.utc)
    ok = _http_ok(HEALTH_URL) and _http_ok(COMMANDER_URL)
    last_ok_raw = db_commander_get_setting("health:last_ok")
    down_since_raw = db_commander_get_setting("health:down_since")
    alerted_raw = db_commander_get_setting("health:alert_sent")

    if ok:
        db_commander_set_setting("health:last_ok", json.dumps(now.isoformat()))
        db_commander_set_setting("health:down_since", json.dumps(None))
        db_commander_set_setting("health:alert_sent", json.dumps(False))
        return None

    if not down_since_raw:
        db_commander_set_setting("health:down_since", json.dumps(now.isoformat()))
        return None

    try:
        down_since = datetime.fromisoformat(json.loads(down_since_raw["value_json"]))
    except (json.JSONDecodeError, TypeError, KeyError):
        down_since = now

    elapsed = (now - down_since).total_seconds()
    if elapsed < DOWN_THRESHOLD_SECONDS:
        return None

    try:
        already = json.loads(alerted_raw["value_json"]) if alerted_raw else False
    except (json.JSONDecodeError, TypeError):
        already = False

    if already:
        return None

    db_commander_set_setting("health:alert_sent", json.dumps(True))
    msg = (
        "Commander unreachable >5 min\n"
        f"Health: {HEALTH_URL}\n"
        f"Dashboard: {COMMANDER_URL}\n"
        "TG notify-only fallback — open dashboard when back."
    )
    logger.warning("[CommanderHealth] %s", msg)
    return msg
