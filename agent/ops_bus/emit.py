"""Emit typed Operations Bus events with audit + approval hooks."""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agent.ops_bus.catalog import (
    APPROVAL_LEVELS,
    AUDIT_ACTIONS,
    EVIDENCE_BY_TYPE,
    EVENT_TYPES,
    FORBIDDEN_PAYLOAD_KEYS,
    MAX_PAYLOAD_BYTES,
    ROOM_IDS,
)
from agent.ops_bus.flags import is_ops_bus_enabled

logger = logging.getLogger(__name__)


@dataclass
class EmitResult:
    ok: bool
    event_id: Optional[str] = None
    duplicate: bool = False
    skipped: bool = False
    error: Optional[str] = None
    approval_needed_id: Optional[str] = None
    approval_state: Optional[str] = None
    synced_event_ids: Optional[List[str]] = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_payload(payload: Dict[str, Any]) -> Optional[str]:
    for key in payload:
        if str(key).lower() in FORBIDDEN_PAYLOAD_KEYS:
            return f"forbidden payload key: {key}"
    try:
        encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    except (TypeError, ValueError) as exc:
        return f"payload not serializable: {exc}"
    if len(encoded.encode("utf-8")) > MAX_PAYLOAD_BYTES:
        return "payload exceeds size limit"
    return None


def emit_ops_bus_event(
    *,
    event_type: str,
    source_room: str,
    dest_room: str,
    payload_ref: str,
    source_system: str,
    source_event_id: str,
    correlation_id: str,
    payload: Optional[Dict[str, Any]] = None,
    approval_level: str = "L0",
    causation_event_id: Optional[str] = None,
    actor_id: Optional[str] = None,
    actor_role: str = "system",
    evidence_id: Optional[str] = None,
) -> EmitResult:
    """
    Persist a typed bus event.

    L0/L1 → approval_state=none
    L2 → approval_state=pending + companion approval_needed
    L3/L4 → reject executable emit; record approval_needed STOP only
    """
    if not is_ops_bus_enabled():
        return EmitResult(ok=True, skipped=True, error="ops_bus_disabled")

    if event_type not in EVENT_TYPES:
        return EmitResult(ok=False, error=f"unknown event_type: {event_type}")
    if approval_level not in APPROVAL_LEVELS:
        return EmitResult(ok=False, error=f"invalid approval_level: {approval_level}")
    if source_room not in ROOM_IDS or dest_room not in ROOM_IDS:
        return EmitResult(ok=False, error="invalid source_room or dest_room")
    if not payload_ref or not source_event_id or not correlation_id:
        return EmitResult(ok=False, error="payload_ref, source_event_id, correlation_id required")

    body = dict(payload or {})
    payload_err = _validate_payload(body)
    if payload_err:
        return EmitResult(ok=False, error=payload_err)

    # L3/L4: never silent-exec; record STOP approval_needed only
    if approval_level in ("L3", "L4") and event_type != "approval_needed":
        return _record_l3_l4_stop(
            parent_type=event_type,
            source_room=source_room,
            dest_room=dest_room,
            payload_ref=payload_ref,
            source_system=source_system,
            source_event_id=source_event_id,
            correlation_id=correlation_id,
            payload=body,
            approval_level=approval_level,
            actor_id=actor_id,
            actor_role=actor_role,
        )

    from agent.db import db_ops_bus_get_by_source, db_ops_bus_insert

    existing = db_ops_bus_get_by_source(event_type, source_event_id)
    if existing:
        return EmitResult(
            ok=True,
            event_id=existing.get("event_id"),
            duplicate=True,
            approval_state=existing.get("approval_state"),
        )

    approval_state = "none"
    if approval_level == "L2":
        approval_state = "pending"
    elif approval_level in ("L3", "L4") and event_type == "approval_needed":
        # STOP vault record — pending + non-mutable via API (403 on approve)
        approval_state = "pending"

    event_id = str(uuid.uuid4())
    ev = evidence_id or EVIDENCE_BY_TYPE.get(event_type)
    row = {
        "event_id": event_id,
        "event_type": event_type,
        "source_room": source_room,
        "dest_room": dest_room,
        "payload_ref": str(payload_ref),
        "payload_json": body,
        "approval_level": approval_level,
        "approval_state": approval_state,
        "evidence_id": ev,
        "correlation_id": correlation_id,
        "causation_event_id": causation_event_id,
        "source_system": source_system,
        "source_event_id": source_event_id,
        "actor_id": actor_id,
        "created_at": _utc_now(),
    }
    inserted = db_ops_bus_insert(row)
    if not inserted:
        # race: unique constraint → treat as duplicate
        again = db_ops_bus_get_by_source(event_type, source_event_id)
        if again:
            return EmitResult(
                ok=True,
                event_id=again.get("event_id"),
                duplicate=True,
                approval_state=again.get("approval_state"),
            )
        return EmitResult(ok=False, error="insert_failed")

    _append_bus_audit(
        event_type=event_type,
        event_id=event_id,
        payload_ref=str(payload_ref),
        actor_id=actor_id or "system",
        actor_role=actor_role,
        after={
            "event_type": event_type,
            "approval_level": approval_level,
            "approval_state": approval_state,
            "correlation_id": correlation_id,
            "source_event_id": source_event_id,
        },
        risk_tier="elevated" if approval_level == "L2" else "sensitive",
    )

    approval_needed_id = None
    if approval_level == "L2" and event_type != "approval_needed":
        companion = emit_ops_bus_event(
            event_type="approval_needed",
            source_room=source_room,
            dest_room="approval-vault",
            payload_ref=event_id,
            source_system=source_system,
            source_event_id=f"approval_needed:{event_id}",
            correlation_id=correlation_id,
            payload={
                "parent_event_id": event_id,
                "parent_type": event_type,
                "go_type": "l2_pending",
            },
            approval_level="L2",
            causation_event_id=event_id,
            actor_id=actor_id,
            actor_role=actor_role,
            evidence_id="EV-W5-005",
        )
        approval_needed_id = companion.event_id

    logger.info(
        "[OpsBus] emitted type=%s event_id=%s corr=%s",
        event_type,
        event_id,
        correlation_id,
    )
    return EmitResult(
        ok=True,
        event_id=event_id,
        approval_needed_id=approval_needed_id,
        approval_state=approval_state,
    )


def _record_l3_l4_stop(
    *,
    parent_type: str,
    source_room: str,
    dest_room: str,
    payload_ref: str,
    source_system: str,
    source_event_id: str,
    correlation_id: str,
    payload: Dict[str, Any],
    approval_level: str,
    actor_id: Optional[str],
    actor_role: str,
) -> EmitResult:
    """Hard STOP: do not persist parent as executable; record approval_needed only."""
    stop_source = f"stop:{approval_level}:{source_event_id}"
    from agent.db import db_ops_bus_get_by_source

    existing = db_ops_bus_get_by_source("approval_needed", stop_source)
    if existing:
        return EmitResult(
            ok=False,
            error=f"{approval_level}_requires_founder_go",
            event_id=None,
            approval_needed_id=existing.get("event_id"),
            duplicate=True,
        )

    companion = emit_ops_bus_event(
        event_type="approval_needed",
        source_room=source_room,
        dest_room="approval-vault",
        payload_ref=str(payload_ref),
        source_system=source_system,
        source_event_id=stop_source,
        correlation_id=correlation_id,
        payload={
            "parent_type": parent_type,
            "go_type": "founder_go_required",
            "approval_level": approval_level,
            "dest_room": dest_room,
            "stop": True,
            "parent_payload": payload,
        },
        approval_level=approval_level,
        actor_id=actor_id,
        actor_role=actor_role,
        evidence_id="EV-W5-005",
    )
    return EmitResult(
        ok=False,
        error=f"{approval_level}_requires_founder_go",
        approval_needed_id=companion.event_id,
        approval_state="pending",
    )


def _append_bus_audit(
    *,
    event_type: str,
    event_id: str,
    payload_ref: str,
    actor_id: str,
    actor_role: str,
    after: Dict[str, Any],
    risk_tier: str,
) -> None:
    from agent.commander.audit import append_audit

    target_type = "lead" if event_type == "lead_qualified" else (
        "order" if event_type == "order_created" else "ops_bus_event"
    )
    append_audit(
        actor_id=actor_id,
        actor_role=actor_role,
        action=AUDIT_ACTIONS.get(event_type, f"ops_bus.{event_type}"),
        source="ops_bus",
        target_type=target_type,
        target_id=payload_ref if target_type in ("lead", "order") else event_id,
        after=after,
        risk_tier=risk_tier,
    )


def _l2_peer_event_ids(row: Dict[str, Any]) -> List[str]:
    """DI-S3: companion ↔ parent pairs that must stay consistent."""
    from agent.db import db_ops_bus_get_by_source

    peers: List[str] = []
    event_id = str(row.get("event_id") or "")
    event_type = row.get("event_type") or ""
    payload = row.get("payload") or {}
    if event_type == "approval_needed":
        parent_id = payload.get("parent_event_id")
        if parent_id:
            peers.append(str(parent_id))
        return peers
    # Parent L2 executable → companion source_event_id convention
    companion = db_ops_bus_get_by_source(
        "approval_needed", f"approval_needed:{event_id}"
    )
    if companion and companion.get("event_id"):
        peers.append(str(companion["event_id"]))
    return peers


def set_approval_state(
    *,
    event_id: str,
    new_state: str,
    actor_id: str,
    actor_role: str,
) -> EmitResult:
    """L2-only state flip; syncs parent↔companion; no deploy/publish/charge."""
    if new_state not in ("approved", "rejected"):
        return EmitResult(ok=False, error="invalid_approval_state")
    if not is_ops_bus_enabled():
        return EmitResult(ok=True, skipped=True, error="ops_bus_disabled")

    from agent.db import db_ops_bus_get_by_event_id, db_ops_bus_set_approval_state
    from agent.commander.audit import append_audit

    row = db_ops_bus_get_by_event_id(event_id)
    if not row:
        return EmitResult(ok=False, error="not_found")
    level = row.get("approval_level") or "L0"
    if level in ("L3", "L4"):
        return EmitResult(ok=False, error=f"{level}_forbidden")
    if level != "L2":
        return EmitResult(ok=False, error="only_l2_mutable")
    if row.get("approval_state") != "pending":
        return EmitResult(ok=False, error="not_pending")

    ok = db_ops_bus_set_approval_state(event_id, new_state)
    if not ok:
        return EmitResult(ok=False, error="update_failed")

    append_audit(
        actor_id=actor_id,
        actor_role=actor_role,
        action="ops_bus.approval_state",
        source="ops_bus",
        target_type="ops_bus_event",
        target_id=event_id,
        before={"approval_state": "pending", "approval_level": level},
        after={"approval_state": new_state, "approval_level": level},
        risk_tier="elevated",
    )

    synced: List[str] = []
    for peer_id in _l2_peer_event_ids(row):
        if peer_id == event_id:
            continue
        peer = db_ops_bus_get_by_event_id(peer_id)
        if not peer:
            continue
        if (peer.get("approval_level") or "L0") != "L2":
            continue
        if peer.get("approval_state") != "pending":
            continue
        if not db_ops_bus_set_approval_state(peer_id, new_state):
            continue
        synced.append(peer_id)
        append_audit(
            actor_id=actor_id,
            actor_role=actor_role,
            action="ops_bus.approval_state_sync",
            source="ops_bus",
            target_type="ops_bus_event",
            target_id=peer_id,
            before={"approval_state": "pending", "approval_level": "L2"},
            after={
                "approval_state": new_state,
                "approval_level": "L2",
                "synced_from": event_id,
            },
            risk_tier="elevated",
        )

    return EmitResult(
        ok=True,
        event_id=event_id,
        approval_state=new_state,
        synced_event_ids=synced or None,
    )
