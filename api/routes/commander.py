"""COI Commander API routes — control plane."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
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
_bearer = HTTPBearer(auto_error=False)


class FeedbackRequest(BaseModel):
    action_type: str
    feedback_type: Literal["approval", "rejection", "correction"]
    payload: Optional[Dict[str, Any]] = None


class SettingsUpdateRequest(BaseModel):
    delegat_email: Optional[str] = None
    delegat_telegram_chat_id: Optional[str] = None
    ui_language: Optional[str] = None
    daily_action_budget: Optional[int] = None
    commander_roles: Optional[Dict[str, str]] = None


class DeeplinkMintRequest(BaseModel):
    ticket_id: int
    base_url: str = "http://localhost:8000"


class LoginExchangeRequest(BaseModel):
    code: str = Field(min_length=8, max_length=256)


class PublishRequest(BaseModel):
    version: Optional[int] = None
    reason: Optional[str] = None


class UnpublishRequest(BaseModel):
    reason: Optional[str] = None


class BulkApproveRequest(BaseModel):
    entry_ids: List[str] = Field(min_length=1)
    reason: Optional[str] = None


class CsFollowupRequest(BaseModel):
    order_id: str = Field(min_length=1, max_length=128)
    customer_hint: str = Field(default="", max_length=256)
    note: str = Field(default="", max_length=1000)


class TicketDispositionRequest(BaseModel):
    disposition: Literal["open", "acked", "closed", "snoozed"]


@router.post("/api/v1/commander/auth/exchange")
async def exchange_commander_login_code(body: LoginExchangeRequest) -> dict:
    """One-time login code → session JWT (MOBILE-02). No Bearer required."""
    from agent.commander.session_login import exchange_login_code

    result = exchange_login_code(body.code)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid or expired login code")
    return {
        "token": result["token"],
        "role": result["role"],
        "sub": result["sub"],
        "expires_at": result["expires_at"],
    }


@router.get("/api/v1/commander/queue")
async def get_commander_queue(
    severity: Optional[str] = Query(default=None),
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    items = build_queue(severity_filter=severity)
    return {
        "items": items,
        "total": len(items),
        "severity_policy_ref": "D0.8",
    }


@router.get("/api/v1/commander/priorities/today")
async def get_priorities_today(
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    items = build_priorities_today(max_items=3)
    return {"priorities": items, "total": len(items)}


@router.get("/api/v1/commander/audit-log/verify")
async def verify_audit_chain_endpoint(
    auth=Depends(require_scope("commander:read")),
) -> dict:
    from agent.commander.authz import resolve_role
    from agent.commander.audit import verify_audit_chain

    if resolve_role(auth) == "viewer":
        raise HTTPException(status_code=403, detail="Viewer cannot verify audit")
    return verify_audit_chain()


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


class LeadDispositionRequest(BaseModel):
    disposition: Literal["open", "acked", "closed", "snoozed"]


@router.get("/api/v1/leads")
async def get_leads(
    limit: int = Query(default=50, ge=1, le=200),
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    leads = db_list_leads(limit=limit)
    fresh = freshness_status("leads", leads[0]["updated_at"] if leads else None)
    return {"leads": leads, "total": len(leads), "freshness": fresh}


@router.post("/api/v1/commander/leads/{lead_id}/disposition")
async def post_lead_disposition(
    lead_id: int,
    body: LeadDispositionRequest,
    auth=Depends(require_scope("queue:act")),
) -> dict:
    """Sales HITL: ack / close / snooze a lead (removes closed/snoozed from hot queue)."""
    from agent.commander.audit import append_audit
    from agent.commander.authz import actor_from_payload
    from agent.db import db_get_lead_by_id, db_update_lead_disposition

    if not db_get_lead_by_id(lead_id):
        raise HTTPException(status_code=404, detail="Lead not found")
    ok = db_update_lead_disposition(lead_id, body.disposition)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid disposition")
    actor_id, actor_role = actor_from_payload(auth)
    append_audit(
        actor_id=actor_id,
        actor_role=actor_role,
        action="lead_disposition",
        source="commander",
        target_type="lead",
        target_id=str(lead_id),
        after={"disposition": body.disposition},
        risk_tier="sensitive",
    )
    return {"lead_id": lead_id, "disposition": body.disposition, "ok": True}


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
    orders = db_list_orders(limit=1)
    leads = db_list_leads(limit=1)
    generated_at = None
    sources: Dict[str, Any] = {}
    if rows:
        generated_at = rows[0].get("generated_at")
        sources = json.loads(rows[0].get("sources_json") or "{}")
    orders_at = orders[0].get("updated_at") if orders else None
    leads_at = leads[0].get("updated_at") if leads else None
    from agent.commander.settings import get_settings

    worker_at = get_settings().get("dowodca_last_active_at")
    freshness = {
        "ga4": freshness_status("ga4", generated_at),
        "orders": freshness_status("orders", orders_at),
        "leads": freshness_status("leads", leads_at),
        "worker": freshness_status("worker", worker_at),
    }
    return {
        "generated_at": generated_at,
        "sources": sources,
        "freshness": freshness,
    }


@router.get("/api/v1/commander/marketing/fb-health")
async def get_marketing_fb_health(
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    """Facebook Page token preflight — no secrets exposed."""
    from agent.publishers.facebook import check_token_health

    return check_token_health()


@router.get("/api/v1/commander/marketing/data-health")
async def get_marketing_data_health(
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    """DTL Data Health — freshness, quality flags, margin coverage (analytics only)."""
    from agent.marketing.dtl import build_data_health_report

    return build_data_health_report()


@router.post("/api/v1/commander/marketing/dtl/ingest")
async def post_marketing_dtl_ingest(
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    """
    Manual DTL ingest trigger (local/ops smoke).
    Does not require queue:act — read-scope operators may refresh facts.
    """
    from agent.marketing.dtl import run_dtl_ingest

    return run_dtl_ingest()


@router.get("/api/v1/commander/marketing/shadow")
async def get_marketing_shadow(
    limit: int = Query(default=20, ge=1, le=100),
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    """Shadow decision log — analytics / Dowódca review (F1)."""
    from agent.db import db_list_marketing_hypotheses, db_list_marketing_shadow

    return {
        "shadow": db_list_marketing_shadow(limit=limit),
        "hypotheses": db_list_marketing_hypotheses(limit=limit),
        "mb_mode": os.getenv("MB_MODE", "shadow"),
    }


@router.get("/api/v1/commander/marketing/shadow/eval-pack")
async def get_marketing_shadow_eval_pack(
    limit: int = Query(default=12, ge=1, le=200),
    window_days: int = Query(default=7, ge=1, le=90),
    stratified: bool = Query(default=True),
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    """Shadow Evaluation Pack v2 — stratified sample for Telegram/CSV scoring."""
    from agent.marketing.shadow_eval import build_eval_pack

    return build_eval_pack(
        limit=limit, window_days=window_days, stratified=stratified
    )


@router.get("/api/v1/commander/marketing/shadow/accuracy")
async def get_marketing_shadow_accuracy(
    window_days: int = Query(default=14, ge=1, le=90),
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    """Rolling Dowódca score accuracy — gate before MB_MODE=propose."""
    from agent.marketing.shadow_eval import compute_accuracy

    return compute_accuracy(window_days=window_days)


@router.post("/api/v1/commander/marketing/shadow/eval-score")
async def post_marketing_shadow_eval_score(
    action_id: str = Query(...),
    eval_score: str = Query(..., description="agree|partial|disagree"),
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    """Record one eval score (API backup for Telegram buttons)."""
    from agent.marketing.shadow_eval import compute_accuracy, record_eval_score

    result = record_eval_score(action_id, eval_score)
    if result.get("ok"):
        result["accuracy"] = compute_accuracy(window_days=14)
    return result


@router.post("/api/v1/commander/marketing/shadow/eval-push")
async def post_marketing_shadow_eval_push(
    limit: int = Query(default=10, ge=1, le=20),
    window_days: int = Query(default=7, ge=1, le=30),
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    """Push stratified eval cards to Telegram admin chat."""
    from agent.marketing.telegram_proposals import send_eval_pack_telegram

    return send_eval_pack_telegram(limit=limit, window_days=window_days)


@router.get("/api/v1/commander/marketing/memory/status")
async def get_marketing_memory_status(
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    """F2b campaign memory status (Chroma or SQL degrade)."""
    from agent.marketing.campaign_memory import memory_status

    return memory_status()


@router.post("/api/v1/commander/marketing/memory/sync")
async def post_marketing_memory_sync(
    limit: int = Query(default=100, ge=1, le=500),
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    """Re-index recent shadow rows into campaign memory."""
    from agent.marketing.campaign_memory import sync_from_shadow

    return sync_from_shadow(limit=limit)


@router.post("/api/v1/commander/marketing/brain/cycle")
async def post_marketing_brain_cycle(
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    """Manual MB decision cycle (shadow Telegram if configured)."""
    from agent.marketing import run_marketing_brain_cycle

    return run_marketing_brain_cycle(send_telegram=True)


class MarketingExecuteRequest(BaseModel):
    action_id: str
    approval_token: str


@router.post("/api/v1/marketing/actions/execute")
async def post_marketing_action_execute(
    body: MarketingExecuteRequest,
    auth=Depends(require_scope("marketing:approve")),
) -> dict:
    """
    Governance execute — requires one-time approval_token.
    Shadow mode / circuit breakers deny side-effects (423).
    """
    from agent.commander.authz import actor_from_payload
    from agent.marketing.governance import execute_action

    actor_id, _ = actor_from_payload(auth)
    result = execute_action(
        body.action_id,
        body.approval_token,
        actor=actor_id or "unknown",
    )
    code = int(result.pop("status_code", 200 if result.get("ok") else 400))
    if not result.get("ok"):
        raise HTTPException(status_code=code, detail=result)
    return result


@router.get("/api/v1/commander/marketing/breakers")
async def get_marketing_breakers(
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    """Current circuit breaker status (analytics)."""
    from agent.marketing.circuit_breakers import is_execute_allowed

    return is_execute_allowed()


@router.get("/api/v1/commander/marketing/brain-bus")
async def get_marketing_brain_bus(
    limit: int = Query(default=20, ge=1, le=100),
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    """Brain Bus recent events + ecosystem hold flag (F3 analytics)."""
    from agent.db import db_list_active_quality_flags, db_list_brain_events

    flags = [
        f
        for f in db_list_active_quality_flags(limit=50)
        if f.get("source") in ("vcms", "ceo_stub")
        or f.get("flag_type") in ("ecosystem_red", "ceo_priority")
    ]
    return {
        "events": db_list_brain_events(limit=limit),
        "ecosystem_flags": flags,
    }


@router.post("/api/v1/commander/marketing/brain-bus/ceo-priority")
async def post_ceo_priority_stub(
    body: dict,
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    """CEO stub — push weekly priority onto Brain Bus (no Ads side-effects)."""
    from agent.marketing.brain_bus import publish_ceo_priority_stub

    priority = (body or {}).get("priority") or (body or {}).get("text") or ""
    if not str(priority).strip():
        raise HTTPException(status_code=422, detail="priority required")
    return publish_ceo_priority_stub(
        str(priority).strip(),
        week=(body or {}).get("week"),
        process_now=True,
        send_telegram=bool((body or {}).get("send_telegram", True)),
    )


@router.post("/api/v1/content-calendar/{entry_id}/publish")
async def commander_publish_entry(
    entry_id: str,
    body: PublishRequest = PublishRequest(),
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


@router.post("/api/v1/commander/actions/calendar/{entry_id}/undo")
async def undo_calendar_internal(
    entry_id: str,
    auth=Depends(require_scope("marketing:approve")),
) -> dict:
    from agent.commander.undo import revert_internal_action

    result = revert_internal_action(entry_id, auth)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result)
    return result


@router.get("/api/v1/commander/tickets/{ticket_id}")
async def get_commander_ticket(
    ticket_id: int,
    token: Optional[str] = Query(default=None),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> dict:
    if token:
        verified = verify_deeplink_token(token)
        if verified != ticket_id:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
    elif credentials:
        await verify_jwt(credentials)
    else:
        raise HTTPException(status_code=401, detail="Missing Authorization or token")
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


@router.post("/api/v1/commander/cs/followup")
async def post_cs_followup(
    body: CsFollowupRequest,
    auth=Depends(require_scope("queue:act")),
) -> dict:
    """Manual Customer Success follow-up spawn (COI-CS-02). No auto-email."""
    from agent.commander.audit import append_audit
    from agent.commander.authz import actor_from_payload
    from agent.commander.cs_followup import spawn_cs_followup_ticket

    ticket_id = spawn_cs_followup_ticket(
        order_id=body.order_id.strip(),
        customer_hint=body.customer_hint.strip(),
        note=body.note.strip(),
    )
    if not ticket_id:
        raise HTTPException(status_code=500, detail="Failed to create CS follow-up")
    actor_id, actor_role = actor_from_payload(auth)
    append_audit(
        actor_id=actor_id,
        actor_role=actor_role,
        action="cs_followup_spawn",
        source="commander",
        target_type="ticket",
        target_id=str(ticket_id),
        after={"order_id": body.order_id.strip(), "source": "cs_followup"},
        risk_tier="sensitive",
    )
    return {
        "ticket_id": ticket_id,
        "queue_type": "cs_followup",
        "ok": True,
    }


@router.post("/api/v1/commander/tickets/{ticket_id}/disposition")
async def post_ticket_disposition(
    ticket_id: int,
    body: TicketDispositionRequest,
    auth=Depends(require_scope("queue:act")),
) -> dict:
    """HITL disposition for Commander tickets (CS / brief / wp)."""
    from agent.commander.audit import append_audit
    from agent.commander.authz import actor_from_payload
    from agent.db import db_commander_get_ticket, db_commander_update_ticket_status

    row = db_commander_get_ticket(ticket_id)
    if not row:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ok = db_commander_update_ticket_status(ticket_id, body.disposition)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid disposition")
    actor_id, actor_role = actor_from_payload(auth)
    append_audit(
        actor_id=actor_id,
        actor_role=actor_role,
        action="ticket_disposition",
        source="commander",
        target_type="ticket",
        target_id=str(ticket_id),
        before={"status": row.get("status")},
        after={"status": body.disposition, "source": row.get("source")},
        risk_tier="sensitive",
    )
    return {"ticket_id": ticket_id, "disposition": body.disposition, "ok": True}
