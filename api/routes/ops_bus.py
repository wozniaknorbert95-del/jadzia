"""VF-VHQ-W5 — Operations Bus Commander API (typed events, no chat)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from api.dependencies import require_scope
from agent.ops_bus.catalog import INGEST_ALLOWED_TYPES, FORBIDDEN_PAYLOAD_KEYS, ROOM_IDS
from agent.ops_bus.emit import emit_ops_bus_event, set_approval_state
from agent.ops_bus.flags import is_ops_bus_enabled
from agent.db import db_ops_bus_get_by_event_id, db_ops_bus_list

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ops-bus"])


class OpsBusIngestRequest(BaseModel):
    event_type: Literal["wizard_started"]
    source_room: str = "wizard-quote"
    dest_room: str = "sales-room"
    payload_ref: Optional[str] = None
    lead_id: Optional[int] = None
    wizard_deeplink: Optional[str] = Field(default=None, max_length=512)
    correlation_id: Optional[str] = Field(default=None, max_length=128)
    payload: Optional[Dict[str, Any]] = None

    @field_validator("payload")
    @classmethod
    def no_chat_keys(cls, value: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not value:
            return value
        for key in value:
            if str(key).lower() in FORBIDDEN_PAYLOAD_KEYS:
                raise ValueError(f"forbidden payload key: {key}")
        return value


class OpsBusApprovalRequest(BaseModel):
    state: Literal["approved", "rejected"]


@router.get("/api/v1/commander/ops-bus/events")
async def list_ops_bus_events(
    event_type: Optional[str] = Query(default=None, alias="type"),
    correlation_id: Optional[str] = Query(default=None),
    approval_state: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    _auth=Depends(require_scope("commander:read")),
) -> dict:
    if not is_ops_bus_enabled():
        return {"events": [], "total": 0, "enabled": False}
    rows = db_ops_bus_list(
        event_type=event_type,
        correlation_id=correlation_id,
        approval_state=approval_state,
        limit=limit,
    )
    return {"events": rows, "total": len(rows), "enabled": True}


@router.post("/api/v1/commander/ops-bus/ingest")
async def ingest_ops_bus_event(
    body: OpsBusIngestRequest,
    auth=Depends(require_scope("queue:act")),
) -> dict:
    if not is_ops_bus_enabled():
        return {"ok": True, "skipped": True, "reason": "ops_bus_disabled"}

    if body.event_type not in INGEST_ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="event_type not allowed for ingest")
    if body.source_room not in ROOM_IDS or body.dest_room not in ROOM_IDS:
        raise HTTPException(status_code=400, detail="invalid room")

    from agent.commander.authz import actor_from_payload

    actor_id, actor_role = actor_from_payload(auth)
    lead_id = body.lead_id
    payload_ref = body.payload_ref
    if lead_id is not None:
        payload_ref = payload_ref or str(lead_id)
        corr = body.correlation_id or f"corr:lead:{lead_id}"
        anon = str(lead_id)
    else:
        payload_ref = payload_ref or "session:commander"
        corr = body.correlation_id or "corr:commander:wizard"
        anon = "anon"

    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    source_event_id = f"wiz_beacon:{actor_id}:{anon}:{day}"

    payload = dict(body.payload or {})
    payload.setdefault("beacon", "commander_ui")
    if lead_id is not None:
        payload["lead_id"] = lead_id
    if body.wizard_deeplink:
        payload["wizard_deeplink"] = body.wizard_deeplink

    result = emit_ops_bus_event(
        event_type="wizard_started",
        source_room=body.source_room,
        dest_room=body.dest_room,
        payload_ref=str(payload_ref),
        source_system="commander_ui",
        source_event_id=source_event_id,
        correlation_id=corr,
        payload=payload,
        approval_level="L0",
        actor_id=actor_id,
        actor_role=actor_role,
        evidence_id="EV-W5-002",
    )
    if not result.ok and not result.skipped:
        raise HTTPException(status_code=400, detail=result.error or "emit_failed")
    return {
        "ok": True,
        "event_id": result.event_id,
        "duplicate": result.duplicate,
        "skipped": result.skipped,
        "approval_state": result.approval_state,
    }


@router.post("/api/v1/commander/ops-bus/events/{event_id}/approval")
async def approve_ops_bus_event(
    event_id: str,
    body: OpsBusApprovalRequest,
    auth=Depends(require_scope("queue:act")),
) -> dict:
    """L2 state flip only — no side effects. L3/L4 → 403."""
    row = db_ops_bus_get_by_event_id(event_id)
    if not row:
        raise HTTPException(status_code=404, detail="Event not found")

    level = row.get("approval_level") or "L0"
    if level in ("L3", "L4"):
        raise HTTPException(
            status_code=403,
            detail=f"{level} requires explicit Founder GO — silent approve forbidden",
        )

    from agent.commander.authz import actor_from_payload

    actor_id, actor_role = actor_from_payload(auth)
    result = set_approval_state(
        event_id=event_id,
        new_state=body.state,
        actor_id=actor_id,
        actor_role=actor_role,
    )
    if not result.ok:
        if result.error == f"{level}_forbidden" or (
            result.error and result.error.endswith("_forbidden")
        ):
            raise HTTPException(status_code=403, detail=result.error)
        if result.error == "not_found":
            raise HTTPException(status_code=404, detail="Event not found")
        raise HTTPException(status_code=400, detail=result.error or "approval_failed")

    return {
        "ok": True,
        "event_id": event_id,
        "approval_state": result.approval_state,
        "side_effects": False,
    }
