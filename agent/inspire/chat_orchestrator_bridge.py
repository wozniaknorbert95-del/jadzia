"""Orchestrator-backed chat intake (brain SSoT) — jadzia bridge."""

from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path
from typing import Any

from agent.inspire import chat_session_store
from agent.inspire.chat_advisor import ChatSession, ChatTurnResult, logo_reupload_required
from agent.inspire.tier_resolver import resolve_tier_skus

logger = logging.getLogger(__name__)


def _ensure_inspire_path() -> Path:
    repo = Path(os.getenv("INSPIRE_REPO_PATH", "/opt/inspire"))
    import sys

    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    return repo


def _orch_imports():
    _ensure_inspire_path()
    from engine.v4.intake import chat_bridge
    from engine.v4.intake.intake_copy import get_stap_labels_nl
    from engine.v4.intake.orchestrator import (
        IntakePhase,
        IntakeState,
        process_intake_opening,
        process_intake_turn,
    )

    return chat_bridge, get_stap_labels_nl, IntakePhase, IntakeState, process_intake_opening, process_intake_turn


def _load_state(session_id: str) -> tuple[IntakeState | None, dict[str, Any] | None]:
    chat_bridge, _, IntakePhase, IntakeState, _, _ = _orch_imports()
    raw = chat_session_store.load_session(session_id)
    if not raw:
        return None, None
    if int(raw.get("schema_version") or 0) != chat_bridge.SESSION_SCHEMA_VERSION:
        return None, raw
    state = chat_bridge.hydrate_intake_state(raw, session_id)
    return state, raw


def _save_state(state: IntakeState, flat: dict[str, Any], brief_confirmed: bool) -> None:
    chat_bridge, _, _, _, _, _ = _orch_imports()
    payload = chat_bridge.serialize_intake_state(state)
    payload["session_id"] = state.session_id
    payload["brief_partial"] = flat
    payload["phase_int"] = chat_bridge.stap_from_phase(state.phase.value)
    payload["brief_confirmed"] = brief_confirmed
    chat_session_store.save_session(state.session_id, payload)


def _resolve_tier_skus_flat(flat: dict[str, Any]) -> None:
    vehicle = flat.get("vehicle")
    if not vehicle:
        return
    if flat.get("mockup_b_sku") and flat.get("mockup_a_sku"):
        return
    try:
        tier_b, tier_a = resolve_tier_skus(str(vehicle), flat)
        flat.setdefault("mockup_b_sku", tier_b.sku)
        flat.setdefault("mockup_a_sku", tier_a.sku)
        flat.pop("_tier_resolve_failed", None)
    except (ValueError, FileNotFoundError) as exc:
        logger.warning("tier resolve failed: %s", exc)
        flat["_tier_resolve_failed"] = True
        flat.pop("mockup_b_sku", None)
        flat.pop("mockup_a_sku", None)


def _build_field_updates(
    field_updates: dict[str, Any] | None,
    quick_reply_id: str | None,
    quick_reply_field: str | None,
) -> dict[str, Any] | None:
    chat_bridge, _, _, _, _, _ = _orch_imports()
    if field_updates:
        return field_updates
    if quick_reply_id and quick_reply_field:
        return chat_bridge.map_chip_to_field_updates(quick_reply_field, quick_reply_id)
    return None


def _result_from_turn(
    state: IntakeState,
    turn,
    flat: dict[str, Any],
    brief_confirmed: bool,
) -> ChatTurnResult:
    chat_bridge, get_stap_labels_nl, _, _, _, _ = _orch_imports()
    stap = chat_bridge.stap_from_phase(turn.phase)
    labels = get_stap_labels_nl()
    ready, missing = chat_bridge.compute_ready_pre_confirm(flat)
    if flat.get("_tier_resolve_failed"):
        ready = False
    return ChatTurnResult(
        session_id=state.session_id,
        reply_nl=turn.reply_nl,
        brief_partial=flat,
        phase=stap,
        ready_to_generate=ready and stap >= 7,
        brief_confirmed=brief_confirmed,
        missing_fields=missing,
        logo_reupload_required=logo_reupload_required(flat),
        stap=stap,
        stap_label=labels.get(stap, ""),
        quick_replies=turn.buttons,
        quick_reply_field=turn.quick_reply_field or "",
        opening_source="brain",
    )


def get_opening(session_id: str | None = None) -> ChatTurnResult:
    chat_bridge, _, IntakePhase, IntakeState, process_intake_opening, _ = _orch_imports()
    sid = session_id or str(uuid.uuid4())
    state = IntakeState(session_id=sid, phase=IntakePhase.OPENING)
    turn = process_intake_opening(state)
    flat = chat_bridge.flat_brief_from_draft(state.brief_draft)
    _resolve_tier_skus_flat(flat)
    _save_state(state, flat, False)
    return _result_from_turn(state, turn, flat, False)


def process_turn(
    *,
    session_id: str | None,
    message: str,
    field_updates: dict[str, Any] | None = None,
    quick_reply_id: str | None = None,
    quick_reply_field: str | None = None,
    logo_filename: str | None = None,
    brand_colors: list[str] | None = None,
) -> ChatTurnResult:
    chat_bridge, _, IntakePhase, IntakeState, _, process_intake_turn = _orch_imports()
    updates = _build_field_updates(field_updates, quick_reply_id, quick_reply_field)

    if session_id:
        state, raw = _load_state(session_id)
        if state is None:
            sid = session_id
            state = IntakeState(session_id=sid, phase=IntakePhase.OPENING)
            brief_confirmed = False
        else:
            brief_confirmed = bool((raw or {}).get("brief_confirmed"))
    else:
        sid = str(uuid.uuid4())
        state = IntakeState(session_id=sid, phase=IntakePhase.OPENING)
        brief_confirmed = False

    if logo_filename:
        chat_bridge.apply_logo_upload(state.brief_draft, logo_filename)
    if brand_colors:
        chat_bridge.apply_brand_colors(state.brief_draft, brand_colors)

    if not message.strip() and not updates and not logo_filename and not brand_colors:
        raise ValueError("Bericht mag niet leeg zijn.")

    turn = process_intake_turn(
        state,
        message=message.strip(),
        field_updates=updates,
    )
    flat = chat_bridge.flat_brief_from_draft(state.brief_draft)
    _resolve_tier_skus_flat(flat)
    _save_state(state, flat, brief_confirmed)
    return _result_from_turn(state, turn, flat, brief_confirmed)


def load_chat_session(session_id: str) -> ChatSession | None:
    chat_bridge, _, _, _, _, _ = _orch_imports()
    raw = chat_session_store.load_session(session_id)
    if not raw:
        return None
    if int(raw.get("schema_version") or 0) != chat_bridge.SESSION_SCHEMA_VERSION:
        return None
    return ChatSession(
        session_id=session_id,
        phase=int(raw.get("phase_int") or 1),
        brief_partial=dict(raw.get("brief_partial") or {}),
        brief_confirmed=bool(raw.get("brief_confirmed")),
        messages=list(raw.get("messages") or []),
        created_at=str(raw.get("created_at") or ""),
    )
