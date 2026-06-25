"""Portal qualification agent — session orchestration for flexgrafik.nl."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional

from cachetools import TTLCache

from agent.portal_qualification.lead_store import save_portal_qual_lead
from agent.portal_qualification.slot_extractor import extract_slot_value
from agent.portal_qualification.slot_extractor_llm import extract_slot_llm
from agent.portal_qualification.state_machine import PortalQualificationStateMachine
from agent.portal_qualification.taxonomy import get_step_config

logger = logging.getLogger(__name__)

_qual_sessions: TTLCache = TTLCache(maxsize=2000, ttl=24 * 3600)
_cache_lock = asyncio.Lock()
_state_machine = PortalQualificationStateMachine()

SCHEMA_VERSION = "qual_v1"


async def _normalize_message_for_step(step: str, message: str) -> str:
    if step in ("greeting", "recommend", "done"):
        return message

    try:
        cfg = get_step_config(step)
    except KeyError:
        return message

    slot = cfg.get("slot")
    if not slot:
        return message

    if extract_slot_value(slot, message):
        return message

    llm_value = await extract_slot_llm(slot, message)
    if llm_value:
        return llm_value

    return message


async def process_portal_qualification(
    *,
    session_id: str,
    message: str,
    step: Optional[str] = None,
    consent_lead_storage: bool = False,
) -> Dict[str, Any]:
    async with _cache_lock:
        session = _qual_sessions.get(session_id) or {
            "step": "greeting",
            "profile": {},
            "consent_lead_storage": False,
        }

    if consent_lead_storage:
        session["consent_lead_storage"] = True

    # Server-owned step — ignore stale client step after session exists
    current_step = session.get("step") or step or "greeting"
    profile = dict(session.get("profile") or {})

    normalized_message = await _normalize_message_for_step(current_step, message)

    result = _state_machine.process_turn(
        step=current_step,
        message=normalized_message,
        profile=profile,
        consent_lead_storage=session.get("consent_lead_storage", False),
    )

    if result.get("recommended_preset_id") and session.get("consent_lead_storage"):
        saved = await asyncio.to_thread(
            save_portal_qual_lead,
            session_id=session_id,
            profile=result.get("qualification_profile") or {},
            recommended_preset_id=result["recommended_preset_id"],
        )
        result["lead_saved"] = saved
    else:
        result["lead_saved"] = False

    async with _cache_lock:
        session["step"] = result["step_next"]
        session["profile"] = result.get("qualification_profile") or profile
        _qual_sessions[session_id] = session

    return {
        "schema_version": SCHEMA_VERSION,
        **result,
    }


def clear_qualification_sessions_for_tests() -> None:
    _qual_sessions.clear()
