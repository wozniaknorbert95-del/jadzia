"""Telegram automated push (alerts / brain / SLA) kill-switch.

Command replies (/commander, /status, …) go through the webhook reply path
and are NOT gated here. Only unsolicited autopush is controlled.
"""

from __future__ import annotations

import os


def telegram_autopush_enabled() -> bool:
    """
    Default OFF (0/false/empty).

    Set TELEGRAM_AUTOPUSH_ENABLED=1 to re-enable automated Telegram alerts
    (hot leads, MB shadow, SLA escalations, health alerts, etc.).
    """
    raw = (os.getenv("TELEGRAM_AUTOPUSH_ENABLED") or "0").strip().lower()
    return raw in ("1", "true", "yes", "on")
