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
from agent.publishers.facebook import delete_post, is_facebook_configured, publish_post

logger = logging.getLogger(__name__)


def _check_daily_budget() -> Optional[Dict]:
    count = db_commander_get_daily_actions()
    if count >= DAILY_ACTION_BUDGET_DEFAULT:
        return {"status": "error", "message": "Daily human action budget exceeded"}
    return None


def publish_calendar_entry(
    entry_id: str,
    auth_payload: Optional[Dict],
    expected_version: Optional[int] = None,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
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
    if row.get("status") != "approved":
        return {"status": "error", "message": f"Entry must be approved, not {row.get('status')}"}

    if not is_facebook_configured():
        return {"status": "error", "message": "Facebook not configured"}

    actor_id, actor_role = actor_from_payload(auth_payload)
    result = publish_post(row["body_nl"])
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


def bulk_approve_guardrail(count: int, reason: Optional[str]) -> Optional[Dict]:
    if count > BULK_APPROVE_LIMIT and not reason:
        return {
            "status": "error",
            "message": f"Bulk approve >{BULK_APPROVE_LIMIT} requires reason",
        }
    return _check_daily_budget()
