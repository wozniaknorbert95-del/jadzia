"""Customer Success follow-up tickets (COI-CS-01 thin slice)."""

from __future__ import annotations

import logging
from typing import Optional

from agent.db import db_commander_create_ticket

logger = logging.getLogger(__name__)


def spawn_cs_followup_ticket(
    *,
    order_id: str,
    customer_hint: str = "",
    note: str = "",
) -> Optional[int]:
    """Create an open Commander ticket sourced as cs_followup (manual/ops trigger)."""
    title = f"[CS] Follow-up order {order_id}"
    description = "\n".join(
        [
            f"order_id: {order_id}",
            f"customer: {customer_hint or '—'}",
            f"note: {note or 'Post-sale check-in'}",
            "source: cs_followup",
        ]
    )
    ticket_id = db_commander_create_ticket(
        title=title,
        description=description,
        source="cs_followup",
        severity="MEDIUM",
    )
    if ticket_id:
        logger.info("cs_followup ticket created id=%s order_id=%s", ticket_id, order_id)
    return ticket_id
