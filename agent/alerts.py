"""
Discord webhook alerts for critical events.
When DISCORD_WEBHOOK_URL is not set, alerts are disabled (no errors).
"""

import logging
import os
import threading
from datetime import datetime, timezone
from typing import Optional

import httpx

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
_log = logging.getLogger(__name__)


def _send_alert_sync(alert_type: str, task_id: Optional[str], details: str) -> None:
    if not DISCORD_WEBHOOK_URL:
        return
    time_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    task_display = task_id if task_id else "N/A"
    content = (
        "🚨 **Jadzia Alert**\n"
        f"**Type:** {alert_type}\n"
        f"**Task:** {task_display}\n"
        f"**Time:** {time_str}\n"
        f"**Details:** {details}"
    )
    try:
        with httpx.Client(timeout=10.0) as client:
            client.post(DISCORD_WEBHOOK_URL, json={"content": content})
    except Exception:
        _log.exception("Discord alert failed: %s", alert_type)


def send_alert(
    alert_type: str,
    task_id: Optional[str] = None,
    details: str = "",
) -> None:
    """
    Fire-and-forget: send alert to Discord webhook in a daemon thread.
    Does not block; exceptions inside the thread are logged only.
    """
    thread = threading.Thread(
        target=_send_alert_sync,
        args=(alert_type, task_id, details),
        daemon=True,
    )
    thread.start()
