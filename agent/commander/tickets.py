"""WP / ops tickets from Telegram."""

from __future__ import annotations

import logging
from typing import Dict, Optional

from agent.commander.deeplink import mint_deeplink
from agent.db import db_commander_create_ticket, db_commander_get_ticket

logger = logging.getLogger(__name__)


def create_ticket_from_telegram(description: str, base_url: str) -> Dict:
    title = (description[:80] + "…") if len(description) > 80 else description or "Ticket bez tytułu"
    ticket_id = db_commander_create_ticket(title=title, description=description, source="telegram")
    if not ticket_id:
        return {"status": "error", "message": "Nie udało się utworzyć ticketu"}
    link = mint_deeplink(ticket_id, base_url)
    logger.info("[CommanderTicket] created id=%s", ticket_id)
    return {
        "status": "ok",
        "ticket_id": ticket_id,
        "deeplink": link,
    }


def get_ticket(ticket_id: int) -> Optional[Dict]:
    return db_commander_get_ticket(ticket_id)
