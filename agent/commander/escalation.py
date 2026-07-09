"""SLA breach detection and escalation to 2nd recipient (N6)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from agent.commander.queue import build_queue
from agent.commander.settings import get_settings
from agent.db import db_commander_set_setting

logger = logging.getLogger(__name__)


def check_sla_escalations() -> int:
    """Return count of red items escalated. Called from worker loop."""
    settings = get_settings()
    delegat_email = settings.get("delegat_email") or ""
    escalated = 0
    for item in build_queue():
        if item.get("sla_status") != "red":
            continue
        key = f"escalated:{item['id']}"
        from agent.db import db_commander_get_setting

        if db_commander_get_setting(key):
            continue
        msg = (
            f"SLA BREACH [{item['severity']}] {item['title']}\n"
            f"Age: {item['age_hours']}h\n"
            f"Delegat: {delegat_email or 'nie skonfigurowany'}"
        )
        try:
            from threading import Thread

            from agent.customer_agent import _send_telegram_alert_sync

            Thread(target=_send_telegram_alert_sync, args=(msg,), daemon=True).start()
        except Exception as exc:
            logger.warning("[CommanderEscalation] notify failed: %s", exc)
        db_commander_set_setting(key, json.dumps({"at": datetime.now(timezone.utc).isoformat()}))
        escalated += 1
    return escalated
