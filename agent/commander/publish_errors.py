"""Publish failure notifications (COI Marketing Phase B)."""

from __future__ import annotations

import logging
from threading import Thread
from typing import Any, Dict

from agent.publishers.facebook import parse_publish_error

logger = logging.getLogger(__name__)


def notify_publish_failure(row: Dict[str, Any], result: Dict[str, Any]) -> None:
    """Alert Dowódca when calendar publish fails."""
    from agent.customer_agent import _send_telegram_alert_sync

    human = parse_publish_error(result)
    msg = (
        "📛 <b>MARKETING — publikacja nieudana</b>\n"
        f"<b>Tytuł:</b> {row.get('title')}\n"
        f"<b>Entry ID:</b> {row.get('entry_id')}\n"
        f"<b>Typ:</b> {row.get('content_type') or 'text'}\n"
        f"<b>Przyczyna:</b> {human}"
    )
    Thread(target=_send_telegram_alert_sync, args=(msg,), daemon=True).start()
    logger.info(
        "[CommanderPublish] Failure alert entry_id=%s reason=%s",
        row.get("entry_id"),
        human,
    )
