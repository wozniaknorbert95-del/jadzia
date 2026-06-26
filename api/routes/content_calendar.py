"""Content calendar API routes — INT-010."""

from __future__ import annotations

import logging
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import verify_jwt
from core.models import (
    ContentCalendarCreateRequest,
    ContentCalendarCreateResponse,
    ContentCalendarEntry,
    ContentCalendarListResponse,
    ContentCalendarUpdateRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["content-calendar"])


@router.get("/api/v1/content-calendar", response_model=ContentCalendarListResponse)
async def get_content_calendar(
    status: Optional[
        Literal["draft", "pending_approval", "approved", "published", "cancelled"]
    ] = Query(default=None),
    platform: Optional[Literal["facebook", "tiktok"]] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    _auth=Depends(verify_jwt),
) -> ContentCalendarListResponse:
    """List social calendar entries (INT-010)."""
    from agent.nodes.content_calendar_node import list_calendar_entries

    return list_calendar_entries(status=status, platform=platform, limit=limit)


@router.post("/api/v1/content-calendar", response_model=ContentCalendarCreateResponse)
async def post_content_calendar(
    request: ContentCalendarCreateRequest,
    _auth=Depends(verify_jwt),
) -> ContentCalendarCreateResponse:
    """Create calendar draft entry (INT-010)."""
    from agent.nodes.content_calendar_node import create_calendar_entry

    return create_calendar_entry(request)


@router.patch("/api/v1/content-calendar/{entry_id}", response_model=ContentCalendarEntry)
async def patch_content_calendar(
    entry_id: str,
    request: ContentCalendarUpdateRequest,
    _auth=Depends(verify_jwt),
) -> ContentCalendarEntry:
    """Update calendar entry status or copy (INT-010)."""
    from agent.nodes.content_calendar_node import update_calendar_entry

    result = update_calendar_entry(entry_id, request)
    if not result:
        raise HTTPException(status_code=404, detail="Calendar entry not found")
    return result


@router.get("/api/v1/content-calendar/suggestions/orders")
async def get_case_study_suggestions(
    limit: int = Query(default=10, ge=1, le=50),
    _auth=Depends(verify_jwt),
) -> dict:
    """Recent completed orders for case-study post ideas."""
    from agent.nodes.content_calendar_node import suggest_case_study_orders

    orders = suggest_case_study_orders(limit=limit)
    return {"orders": orders, "total": len(orders)}
