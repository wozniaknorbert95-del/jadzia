"""Content calendar API routes — INT-010."""

from __future__ import annotations

import logging
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import require_scope, verify_jwt
from core.models import (
    ContentCalendarCreateRequest,
    ContentCalendarCreateResponse,
    ContentCalendarEntry,
    ContentCalendarListResponse,
    ContentCalendarPublishStatusResponse,
    ContentCalendarUpdateRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["content-calendar"])


@router.get("/api/v1/content-calendar", response_model=ContentCalendarListResponse)
async def get_content_calendar(
    status: Optional[
        Literal["draft", "pending_approval", "approved", "published", "cancelled", "failed"]
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
    _auth=Depends(require_scope("marketing:approve")),
) -> ContentCalendarCreateResponse:
    """Create calendar draft entry (INT-010)."""
    from agent.nodes.content_calendar_node import create_calendar_entry

    return create_calendar_entry(request)


@router.patch("/api/v1/content-calendar/{entry_id}", response_model=ContentCalendarEntry)
async def patch_content_calendar(
    entry_id: str,
    request: ContentCalendarUpdateRequest,
    _auth=Depends(require_scope("marketing:approve")),
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



@router.get(
    "/api/v1/content-calendar/{entry_id}/publish-status",
    response_model=ContentCalendarPublishStatusResponse,
)
async def get_publish_status(
    entry_id: str,
    _auth=Depends(verify_jwt),
) -> ContentCalendarPublishStatusResponse:
    """Return publish state and FB post id for a calendar entry (INT-011)."""
    from agent.db import db_get_calendar_entry

    try:
        internal_id = int(entry_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid entry_id") from None

    row = db_get_calendar_entry(internal_id)
    if not row:
        raise HTTPException(status_code=404, detail="Calendar entry not found")

    return ContentCalendarPublishStatusResponse(
        entry_id=str(row["entry_id"]),
        status=row["status"],
        fb_post_id=row.get("fb_post_id"),
        publish_result=row.get("publish_result"),
        platform=row["platform"],
    )
