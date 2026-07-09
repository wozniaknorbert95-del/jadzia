"""Content calendar node — INT-010 social schedule, INT-011 Facebook publish."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import List, Optional

from agent.db import (
    db_create_calendar_entry,
    db_get_calendar_entry,
    db_get_completed_orders_for_calendar,
    db_list_calendar_entries,
    db_update_calendar_entry,
)
from agent.publishers.facebook import is_facebook_configured, publish_post
from core.models import (
    ContentCalendarCreateRequest,
    ContentCalendarCreateResponse,
    ContentCalendarEntry,
    ContentCalendarListResponse,
    ContentCalendarUpdateRequest,
)

logger = logging.getLogger(__name__)


def list_calendar_entries(
    status: Optional[str] = None,
    platform: Optional[str] = None,
    limit: int = 50,
) -> ContentCalendarListResponse:
    """Return scheduled social posts from jadzia.db."""
    rows = db_list_calendar_entries(status=status, platform=platform, limit=limit)
    entries = [_row_to_entry(row) for row in rows]
    return ContentCalendarListResponse(entries=entries, total=len(entries))


def create_calendar_entry(
    payload: ContentCalendarCreateRequest,
) -> ContentCalendarCreateResponse:
    """Persist new calendar draft."""
    entry_data = {
        "platform": payload.platform,
        "title": payload.title,
        "body_nl": payload.body_nl,
        "scheduled_at": payload.scheduled_at,
        "status": "draft",
        "source_order_id": payload.source_order_id,
    }
    entry_id, sync_status = db_create_calendar_entry(entry_data)

    if sync_status == "fail" or not entry_id:
        logger.error("[ContentCalendarNode] Persist failed platform=%s", payload.platform)
        return ContentCalendarCreateResponse(entry_id="", sync_status="fail")

    logger.info(
        "[ContentCalendarNode] Entry created entry_id=%s platform=%s",
        entry_id,
        payload.platform,
    )
    return ContentCalendarCreateResponse(entry_id=entry_id, sync_status="success")


def update_calendar_entry(
    entry_id: str,
    payload: ContentCalendarUpdateRequest,
) -> Optional[ContentCalendarEntry]:
    """Update existing calendar entry."""
    try:
        internal_id = int(entry_id)
    except ValueError:
        return None

    updates = payload.model_dump(exclude_none=True)
    if not updates:
        row = db_get_calendar_entry(internal_id)
        return _row_to_entry(row) if row else None

    row_before = db_get_calendar_entry(internal_id)
    if not row_before:
        return None

    if not db_update_calendar_entry(internal_id, updates):
        logger.error("[ContentCalendarNode] Update failed entry_id=%s", entry_id)
        return None

    row = db_get_calendar_entry(internal_id)
    if not row:
        return None

    if updates.get("status") == "approved" and row_before.get("status") != "approved":
        from agent.commander.undo import register_internal_undo

        register_internal_undo(str(entry_id), row_before.get("status") or "draft")

    if updates.get("status") == "pending_approval":
        _notify_pending_approval(row)

    logger.info("[ContentCalendarNode] Entry updated entry_id=%s", entry_id)
    return _row_to_entry(row)


def _notify_pending_approval(row: dict) -> None:
    """Alert Dowódca when calendar entry needs approval (P2-02)."""
    from threading import Thread

    from agent.customer_agent import _send_telegram_alert_sync

    msg = (
        f"📅 <b>CONTENT CALENDAR — approval</b>\n"
        f"<b>Platform:</b> {row.get('platform')}\n"
        f"<b>Title:</b> {row.get('title')}\n"
        f"<b>Scheduled:</b> {row.get('scheduled_at')}\n"
        f"<b>Entry ID:</b> {row.get('entry_id')}"
    )
    Thread(target=_send_telegram_alert_sync, args=(msg,), daemon=True).start()
    logger.info("[ContentCalendarNode] Pending approval alert entry_id=%s", row.get("entry_id"))


def suggest_case_study_orders(limit: int = 10) -> List[dict]:
    """Pull recent orders for Dowódca case-study post ideas."""
    orders = db_get_completed_orders_for_calendar(limit=limit)
    logger.info("[ContentCalendarNode] Case study suggestions count=%s", len(orders))
    return orders


def publish_entry(entry_id: str) -> dict:
    """Publish an approved Facebook calendar entry via Graph API (INT-011)."""
    try:
        internal_id = int(entry_id)
    except ValueError:
        return {"status": "error", "message": "Invalid entry_id"}

    row = db_get_calendar_entry(internal_id)
    if not row:
        return {"status": "error", "message": "Entry not found"}

    if row.get("platform") != "facebook":
        return {
            "status": "error",
            "message": f"Publish supported for facebook only, not {row.get('platform')}",
        }

    if row.get("status") != "approved":
        return {
            "status": "error",
            "message": f"Entry must be approved, not {row.get('status')}",
        }

    if not is_facebook_configured():
        return {
            "status": "error",
            "message": "FB_PAGE_ID and FB_ACCESS_TOKEN not configured",
        }

    result = publish_post(row["body_nl"])
    updates = {
        "publish_result": json.dumps(result),
        "fb_post_id": result.get("post_id"),
    }
    if result.get("status") == "success":
        updates["status"] = "published"
    else:
        updates["status"] = "failed"

    db_update_calendar_entry(internal_id, updates)
    logger.info(
        "[ContentCalendarNode] Publish entry_id=%s fb_status=%s",
        entry_id,
        result.get("status"),
    )
    return result


def publish_due_scheduled_entries(limit: int = 20) -> int:
    """Publish approved entries whose scheduled_publish_at is due (worker hook)."""
    if not is_facebook_configured():
        return 0

    entries = db_list_calendar_entries(status="approved", platform="facebook", limit=limit)
    now = datetime.now(timezone.utc)
    published_count = 0

    for entry in entries:
        sched_raw = entry.get("scheduled_publish_at") or entry.get("scheduled_at")
        if not sched_raw:
            continue
        if entry.get("status") == "held":
            continue
        try:
            sched_dt = datetime.fromisoformat(str(sched_raw).replace("Z", "+00:00"))
            if sched_dt.tzinfo is None:
                sched_dt = sched_dt.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue
        if sched_dt <= now:
            from agent.commander.publish import publish_calendar_entry_system

            result = publish_calendar_entry_system(
                str(entry["entry_id"]),
                expected_version=entry.get("version"),
            )
            if result.get("status") == "success":
                published_count += 1

    if published_count:
        logger.info("[ContentCalendarNode] Scheduled publish count=%s", published_count)
    return published_count


def _row_to_entry(row: dict) -> ContentCalendarEntry:
    return ContentCalendarEntry(
        entry_id=row["entry_id"],
        platform=row["platform"],
        title=row["title"],
        body_nl=row["body_nl"],
        scheduled_at=row["scheduled_at"],
        status=row["status"],
        source_order_id=row.get("source_order_id"),
        fb_post_id=row.get("fb_post_id"),
        publish_result=row.get("publish_result"),
        media_url=row.get("media_url"),
        scheduled_publish_at=row.get("scheduled_publish_at"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
