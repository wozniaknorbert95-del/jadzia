"""Publish / unpublish with audit, version lock, cost guardrail."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from agent.commander.audit import append_audit
from agent.commander.authz import actor_from_payload
from agent.commander.constants import BULK_APPROVE_LIMIT, DAILY_ACTION_BUDGET_DEFAULT
from agent.db import (
    db_commander_get_daily_actions,
    db_commander_increment_daily_actions,
    db_get_calendar_entry,
    db_update_calendar_entry,
    db_update_calendar_entry_versioned,
)
from agent.publishers.calendar_publish import publish_calendar_content
from agent.publishers.facebook import delete_post, is_facebook_configured

logger = logging.getLogger(__name__)


def _check_daily_budget() -> Optional[Dict]:
    from agent.commander.settings import get_settings

    settings = get_settings()
    limit = int(settings.get("daily_action_budget") or DAILY_ACTION_BUDGET_DEFAULT)
    count = db_commander_get_daily_actions()
    if count >= limit:
        return {"status": "error", "message": "Daily human action budget exceeded"}
    return None


def publish_calendar_entry(
    entry_id: str,
    auth_payload: Optional[Dict],
    expected_version: Optional[int] = None,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    from agent.commander.graduation import is_hotl_mode

    budget_err = _check_daily_budget()
    if budget_err:
        return budget_err

    try:
        internal_id = int(entry_id)
    except ValueError:
        return {"status": "error", "message": "Invalid entry_id"}

    row = db_get_calendar_entry(internal_id)
    if not row:
        return {"status": "error", "message": "Entry not found"}

    version = expected_version or row.get("version") or 1
    if row.get("status") == "pending_approval" and is_hotl_mode("fb_post_approve"):
        db_update_calendar_entry(internal_id, {"status": "approved"})
        row = db_get_calendar_entry(internal_id) or row
    if row.get("status") != "approved":
        return {"status": "error", "message": f"Entry must be approved, not {row.get('status')}"}

    if not is_facebook_configured():
        return {"status": "error", "message": "Facebook not configured"}

    actor_id, actor_role = actor_from_payload(auth_payload)
    result = publish_calendar_content(row)
    updates = {
        "publish_result": json.dumps(result),
        "fb_post_id": result.get("post_id"),
    }
    if result.get("status") == "success":
        updates["status"] = "published"
    else:
        updates["status"] = "failed"

    ok, new_ver = db_update_calendar_entry_versioned(internal_id, updates, version)
    if not ok:
        return {"status": "error", "message": "Version conflict", "code": 409}

    db_commander_increment_daily_actions()
    append_audit(
        actor_id=actor_id,
        actor_role=actor_role,
        action="publish",
        source="commander",
        target_type="calendar_entry",
        target_id=entry_id,
        before={"status": row.get("status"), "version": version},
        after={"status": updates["status"], "version": new_ver, "fb_post_id": result.get("post_id")},
        reason=reason,
        risk_tier="sensitive",
    )
    result["version"] = new_ver
    return result


def unpublish_calendar_entry(
    entry_id: str,
    auth_payload: Optional[Dict],
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        internal_id = int(entry_id)
    except ValueError:
        return {"status": "error", "message": "Invalid entry_id"}

    row = db_get_calendar_entry(internal_id)
    if not row:
        return {"status": "error", "message": "Entry not found"}

    fb_post_id = row.get("fb_post_id")
    if not fb_post_id:
        return {"status": "error", "message": "No fb_post_id to unpublish"}

    actor_id, actor_role = actor_from_payload(auth_payload)
    result = delete_post(fb_post_id)
    updates = {
        "status": "cancelled",
        "publish_result": json.dumps({"unpublish": result}),
    }
    db_update_calendar_entry(internal_id, updates)
    append_audit(
        actor_id=actor_id,
        actor_role=actor_role,
        action="published_then_unpublished",
        source="commander",
        target_type="calendar_entry",
        target_id=entry_id,
        before={"status": row.get("status"), "fb_post_id": fb_post_id},
        after=updates,
        reason=reason or "operator_unpublish",
        risk_tier="high-impact",
    )
    return {"status": "success", "unpublish": result}


def publish_calendar_entry_system(
    entry_id: str,
    expected_version: Optional[int] = None,
    reason: str = "scheduled_worker",
) -> Dict[str, Any]:
    """Worker/system publish — version lock + audit (N13)."""
    return publish_calendar_entry(
        entry_id,
        {"sub": "worker", "role": "dowodca"},
        expected_version,
        reason,
    )


def bulk_approve_guardrail(count: int, reason: Optional[str]) -> Optional[Dict]:
    if count > BULK_APPROVE_LIMIT and not reason:
        return {
            "status": "error",
            "message": f"Bulk approve >{BULK_APPROVE_LIMIT} requires reason",
        }
    return _check_daily_budget()
