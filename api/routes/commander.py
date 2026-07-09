"""COI Commander API routes — control plane."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from api.dependencies import require_scope, verify_jwt
from agent.commander.agents_registry import list_agents, pause_agent, resume_agent
from agent.commander.audit import list_audit
from agent.commander.deeplink import mint_deeplink, verify_deeplink_token
from agent.commander.graduation import graduation_status, record_feedback
from agent.commander.publish import bulk_approve_guardrail, publish_calendar_entry, unpublish_calendar_entry
from agent.commander.queue import build_priorities_today, build_queue
from agent.commander.settings import get_settings, update_settings
from agent.commander.sla import freshness_status
from agent.commander.tickets import create_ticket_from_telegram, get_ticket
from agent.db import db_list_analytics_snapshots, db_list_leads, db_list_orders

logger = logging.getLogger(__name__)

router = APIRouter(tags=["commander"])


class FeedbackRequest(BaseModel):
    action_type: str
    feedback_type: Literal["approval", "rejection", "correction"]
    payload: Optional[Dict[str, Any]] = None


class SettingsUpdateRequest(BaseModel):
    delegat_email: Optional[str] = None
    ui_language: Optional[str] = None
    daily_action_budget: Optional[int] = None


class DeeplinkMintRequest(BaseModel):
    ticket_id: int
    base_url: str = "http://localhost:8000"


class PublishRequest(BaseModel):
    version: Optional[int] = None
    reason: Optional[str] = None


class UnpublishRequest(BaseModel):
    reason: Optional[str] = None


class BulkApproveRequest(BaseModel):
    entry_ids: List[str] = Field(min_length=1)
    reason: Optional[str] = None


@router.get("/api/v1/commander/queue")
async def get_commander_queue(
    severity: Optional[str] = Query(default=None),
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    items = build_queue(severity_filter=severity)
    return {"items": items, "total": len(items)}


@router.get("/api/v1/commander/priorities/today")
async def get_priorities_today(
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    items = build_priorities_today(max_items=3)
    return {"priorities": items, "total": len(items)}


@router.get("/api/v1/commander/audit-log")
async def get_audit_log(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    auth=Depends(require_scope("commander:read")),
) -> dict:
    from agent.commander.authz import resolve_role

    role = resolve_role(auth)
    if role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer cannot read audit log")
    rows = list_audit(limit=limit, offset=offset)
    return {"entries": rows, "total": len(rows)}


@router.post("/api/v1/commander/feedback")
async def post_feedback(
    body: FeedbackRequest,
    auth=Depends(require_scope("queue:act")),
) -> dict:
    from agent.commander.authz import actor_from_payload

    actor_id, _ = actor_from_payload(auth)
    return record_feedback(body.action_type, body.feedback_type, body.payload, actor_id)


@router.get("/api/v1/commander/graduation/{action_type}")
async def get_graduation(
    action_type: str,
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    return graduation_status(action_type)


@router.get("/api/v1/orders")
async def get_orders(
    limit: int = Query(default=50, ge=1, le=200),
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    orders = db_list_orders(limit=limit)
    fresh = freshness_status("orders", orders[0]["updated_at"] if orders else None)
    return {"orders": orders, "total": len(orders), "freshness": fresh}


@router.get("/api/v1/leads")
async def get_leads(
    limit: int = Query(default=50, ge=1, le=200),
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    leads = db_list_leads(limit=limit)
    fresh = freshness_status("leads", leads[0]["updated_at"] if leads else None)
    return {"leads": leads, "total": len(leads), "freshness": fresh}


@router.get("/api/v1/agents")
async def get_agents(
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    return {"agents": list_agents(), "total": len(list_agents())}


@router.post("/api/v1/agents/{agent_id}/pause")
async def post_pause_agent(
    agent_id: str,
    auth=Depends(require_scope("agents:pause")),
) -> dict:
    from agent.commander.audit import append_audit
    from agent.commander.authz import actor_from_payload

    actor_id, actor_role = actor_from_payload(auth)
    result = pause_agent(agent_id)
    append_audit(
        actor_id=actor_id,
        actor_role=actor_role,
        action="agent_pause",
        source="commander",
        target_type="agent",
        target_id=agent_id,
        after=result,
        risk_tier="high-impact",
    )
    return result


@router.post("/api/v1/agents/{agent_id}/resume")
async def post_resume_agent(
    agent_id: str,
    auth=Depends(require_scope("agents:pause")),
) -> dict:
    from agent.commander.audit import append_audit
    from agent.commander.authz import actor_from_payload

    actor_id, actor_role = actor_from_payload(auth)
    result = resume_agent(agent_id)
    append_audit(
        actor_id=actor_id,
        actor_role=actor_role,
        action="agent_resume",
        source="commander",
        target_type="agent",
        target_id=agent_id,
        after=result,
        risk_tier="sensitive",
    )
    return result


@router.get("/api/v1/commander/analytics/snapshot")
async def get_commander_analytics_snapshot(
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    rows = db_list_analytics_snapshots(limit=1)
    generated_at = None
    sources: Dict[str, Any] = {}
    if rows:
        generated_at = rows[0].get("generated_at")
        sources = json.loads(rows[0].get("sources_json") or "{}")
    freshness = {
        "ga4": freshness_status("ga4", generated_at),
        "orders": freshness_status("orders", datetime.now(timezone.utc).isoformat()),
        "leads": freshness_status("leads", datetime.now(timezone.utc).isoformat()),
    }
    return {
        "generated_at": generated_at,
        "sources": sources,
        "freshness": freshness,
    }


@router.post("/api/v1/content-calendar/{entry_id}/publish")
async def commander_publish_entry(
    entry_id: str,
    body: PublishRequest,
    auth=Depends(require_scope("marketing:publish")),
) -> dict:
    result = publish_calendar_entry(entry_id, auth, body.version, body.reason)
    if result.get("code") == 409:
        raise HTTPException(status_code=409, detail=result)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result)
    return result


@router.post("/api/v1/content-calendar/{entry_id}/unpublish")
async def commander_unpublish_entry(
    entry_id: str,
    body: UnpublishRequest,
    auth=Depends(require_scope("marketing:unpublish")),
) -> dict:
    result = unpublish_calendar_entry(entry_id, auth, body.reason)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result)
    return result


@router.post("/api/v1/commander/bulk-approve")
async def commander_bulk_approve(
    body: BulkApproveRequest,
    auth=Depends(require_scope("marketing:approve")),
) -> dict:
    guard = bulk_approve_guardrail(len(body.entry_ids), body.reason)
    if guard:
        raise HTTPException(status_code=400, detail=guard)
    from agent.nodes.content_calendar_node import update_calendar_entry
    from core.models import ContentCalendarUpdateRequest

    approved = []
    for eid in body.entry_ids:
        entry = update_calendar_entry(eid, ContentCalendarUpdateRequest(status="approved"))
        if entry:
            approved.append(eid)
    return {"approved": approved, "total": len(approved)}


@router.post("/api/v1/commander/deeplink")
async def post_deeplink(
    body: DeeplinkMintRequest,
    auth=Depends(require_scope("queue:act")),
) -> dict:
    if not get_ticket(body.ticket_id):
        raise HTTPException(status_code=404, detail="Ticket not found")
    return mint_deeplink(body.ticket_id, body.base_url)


@router.get("/api/v1/commander/tickets/{ticket_id}")
async def get_commander_ticket(
    ticket_id: int,
    token: Optional[str] = Query(default=None),
    _auth=Depends(verify_jwt),
) -> dict:
    if token:
        verified = verify_deeplink_token(token)
        if verified != ticket_id:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
    row = get_ticket(ticket_id)
    if not row:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return row


@router.get("/api/v1/commander/settings")
async def get_commander_settings(
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    return get_settings()


@router.patch("/api/v1/commander/settings")
async def patch_commander_settings(
    body: SettingsUpdateRequest,
    auth=Depends(require_scope("settings:roles")),
) -> dict:
    updates = body.model_dump(exclude_none=True)
    return update_settings(updates)


@router.post("/api/v1/commander/tickets")
async def post_commander_ticket(
    title: str,
    description: str,
    base_url: str = "http://localhost:8000",
    auth=Depends(require_scope("queue:act")),
) -> dict:
    from agent.db import db_commander_create_ticket

    ticket_id = db_commander_create_ticket(title=title, description=description, source="api")
    if not ticket_id:
        raise HTTPException(status_code=500, detail="Failed to create ticket")
    return {"ticket_id": ticket_id, "deeplink": mint_deeplink(ticket_id, base_url)}
