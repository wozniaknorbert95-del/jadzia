"""Lead API routes — INT-004 game lead sync."""

from __future__ import annotations

import logging
import os

from fastapi import APIRouter, Header, HTTPException

from core.models import LeadCreateRequest, LeadCreateResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["leads"])

LEADS_API_KEY = os.getenv("LEADS_API_KEY", "")


def _validate_leads_api_key(x_api_key: str | None) -> None:
    """Validate X-API-Key when LEADS_API_KEY is configured."""
    if not LEADS_API_KEY:
        logger.warning("LEADS_API_KEY not configured — lead API auth skipped")
        return

    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")

    if x_api_key != LEADS_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@router.post("/api/v1/leads", response_model=LeadCreateResponse)
async def create_lead(
    request: LeadCreateRequest,
    x_api_key: str | None = Header(None, alias="X-API-Key"),
) -> LeadCreateResponse:
    """Receive lead from app.flexgrafik.nl (INT-004)."""
    _validate_leads_api_key(x_api_key)

    from agent.nodes.lead_node import process_lead_sync

    return process_lead_sync(request)
