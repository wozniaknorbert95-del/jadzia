"""GPT marketing advisor chat — session store + OpenRouter (mockable in tests)."""

from __future__ import annotations

import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

import httpx
from cachetools import TTLCache

from agent.inspire.chat_prompts import REQUIRED_BRIEF_FIELDS, SYSTEM_PROMPT
from agent.inspire.tier_resolver import resolve_tier_skus

logger = logging.getLogger(__name__)

SESSION_TTL_SEC = 2 * 3600
SESSIONS: TTLCache = TTLCache(maxsize=500, ttl=SESSION_TTL_SEC)

_LLM_CALLABLE: Callable[[list[dict[str, str]]], dict[str, Any]] | None = None


@dataclass
class ChatSession:
    session_id: str
    phase: int = 1
    brief_partial: dict[str, Any] = field(default_factory=dict)
    brief_confirmed: bool = False
    messages: list[dict[str, str]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ChatTurnResult:
    session_id: str
    reply_nl: str
    brief_partial: dict[str, Any]
    phase: int
    ready_to_generate: bool
    brief_confirmed: bool


def set_llm_callable(fn: Callable[[list[dict[str, str]]], dict[str, Any]] | None) -> None:
    """Test hook — inject mock LLM responses."""
    global _LLM_CALLABLE
    _LLM_CALLABLE = fn


def _default_openrouter_call(messages: list[dict[str, str]]) -> dict[str, Any]:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY ontbreekt")

    model = os.getenv("DA_CHAT_MODEL", "openai/gpt-4o-mini")
    payload = {
        "model": model,
        "messages": messages,
        "response_format": {"type": "json_object"},
        "temperature": 0.4,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return json.loads(content)


def _call_llm(messages: list[dict[str, str]]) -> dict[str, Any]:
    if _LLM_CALLABLE is not None:
        return _LLM_CALLABLE(messages)
    return _default_openrouter_call(messages)


def _merge_brief(session: ChatSession, updates: dict[str, Any]) -> None:
    for key, val in updates.items():
        if val is None:
            continue
        if isinstance(val, str) and not val.strip():
            continue
        if isinstance(val, list) and not val:
            continue
        session.brief_partial[key] = val


def _resolve_tier_skus_if_ready(session: ChatSession) -> None:
    vehicle = session.brief_partial.get("vehicle")
    if not vehicle:
        return
    if session.brief_partial.get("mockup_b_sku") and session.brief_partial.get("mockup_a_sku"):
        return
    try:
        tier_b, tier_a = resolve_tier_skus(vehicle, session.brief_partial)
        session.brief_partial.setdefault("mockup_b_sku", tier_b.sku)
        session.brief_partial.setdefault("mockup_a_sku", tier_a.sku)
    except (ValueError, FileNotFoundError) as exc:
        logger.warning("tier resolve skipped: %s", exc)


def _missing_fields(brief: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for fld in REQUIRED_BRIEF_FIELDS:
        val = brief.get(fld)
        if val is None or val == "" or val == []:
            missing.append(fld)
    return missing


def _compute_ready(session: ChatSession) -> bool:
    if not session.brief_confirmed:
        return False
    return len(_missing_fields(session.brief_partial)) == 0


def compute_ready(session: ChatSession) -> bool:
    return _compute_ready(session)


def get_session(session_id: str) -> ChatSession | None:
    return SESSIONS.get(session_id)


def get_or_create_session(session_id: str | None) -> ChatSession:
    if session_id and session_id in SESSIONS:
        return SESSIONS[session_id]
    sid = session_id or str(uuid.uuid4())
    session = ChatSession(session_id=sid)
    SESSIONS[sid] = session
    return session


def attach_logo(session_id: str, filename: str) -> None:
    session = get_or_create_session(session_id)
    session.brief_partial["logo_file"] = filename


def process_chat_turn(
    *,
    session_id: str | None,
    message: str,
    logo_filename: str | None = None,
) -> ChatTurnResult:
    session = get_or_create_session(session_id)
    if logo_filename:
        session.brief_partial["logo_file"] = logo_filename

    user_msg = message.strip()
    if not user_msg and not logo_filename:
        raise ValueError("Bericht mag niet leeg zijn.")

    if user_msg:
        session.messages.append({"role": "user", "content": user_msg})

    context = json.dumps(
        {
            "current_phase": session.phase,
            "brief_partial": session.brief_partial,
            "brief_confirmed": session.brief_confirmed,
        },
        ensure_ascii=False,
    )
    llm_messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Huidige sessiestatus: {context}"},
        *session.messages,
    ]

    parsed = _call_llm(llm_messages)
    reply_nl = str(parsed.get("reply_nl", "")).strip() or "Kun je dat iets uitgebreider toelichten?"
    session.phase = int(parsed.get("phase", session.phase))
    session.phase = max(1, min(8, session.phase))

    updates = parsed.get("brief_updates") or {}
    if isinstance(updates, dict):
        _merge_brief(session, updates)

    if parsed.get("brief_confirmed") is True:
        session.brief_confirmed = True

    _resolve_tier_skus_if_ready(session)
    ready = _compute_ready(session)

    session.messages.append({"role": "assistant", "content": reply_nl})

    return ChatTurnResult(
        session_id=session.session_id,
        reply_nl=reply_nl,
        brief_partial=dict(session.brief_partial),
        phase=session.phase,
        ready_to_generate=ready,
        brief_confirmed=session.brief_confirmed,
    )
