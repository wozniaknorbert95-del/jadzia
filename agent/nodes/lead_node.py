"""Lead ingestion node — INT-004 game lead sync."""

from __future__ import annotations

import logging

from agent.db import db_create_lead
from core.models import LeadCreateRequest, LeadCreateResponse

logger = logging.getLogger(__name__)


def process_lead_sync(payload: LeadCreateRequest) -> LeadCreateResponse:
    """
    Persist game/web lead to jadzia.db.

    Agent card output: lead_id, sync_status.
    """
    if not payload.consent_status:
        logger.warning("[LeadNode] Rejected lead without consent")
        return LeadCreateResponse(lead_id="", sync_status="fail")

    lead_data = {
        "email": str(payload.email),
        "name": payload.name or None,
        "source": payload.source,
        "consent_status": payload.consent_status,
        "game_score": payload.game_score,
        "reward_tier": payload.reward_tier,
    }

    lead_id, sync_status = db_create_lead(lead_data)

    if sync_status == "fail" or not lead_id:
        logger.error("[LeadNode] Persist failed source=%s", payload.source)
        return LeadCreateResponse(lead_id="", sync_status="fail")

    logger.info(
        "[LeadNode] Lead %s source=%s id=%s",
        sync_status,
        payload.source,
        lead_id,
    )
    return LeadCreateResponse(lead_id=lead_id, sync_status=sync_status)
