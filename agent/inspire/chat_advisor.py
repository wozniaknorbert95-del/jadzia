"""GPT marketing advisor chat — session store + OpenRouter (mockable in tests)."""

from __future__ import annotations

import json
import logging
import os
import re
import uuid
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

import httpx
from cachetools import TTLCache

from agent.inspire.chat_prompts import REQUIRED_BRIEF_FIELDS, SYSTEM_PROMPT
from agent.inspire import chat_session_store
from agent.inspire.tier_resolver import resolve_tier_skus

logger = logging.getLogger(__name__)

SESSION_TTL_SEC = 2 * 3600
SESSIONS: TTLCache = TTLCache(maxsize=500, ttl=SESSION_TTL_SEC)

_LLM_CALLABLE: Callable[[list[dict[str, str]]], dict[str, Any]] | None = None

_EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
_CONSENT_RE = re.compile(
    r"\b(consent|akkoord|toestemming|zgoda|ja\s*mag|mag\s*bewaren)\b",
    re.IGNORECASE,
)


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
    missing_fields: list[str]
    logo_reupload_required: bool
    stap: int = 1
    stap_label: str = ""
    quick_replies: list[dict[str, str]] = field(default_factory=list)
    quick_reply_field: str = ""
    opening_source: str = "legacy"
    lead_id: Optional[str] = None


def _chat_engine() -> str:
    return os.getenv("DA_CHAT_ENGINE", "orchestrator").strip().lower()


def _use_orchestrator() -> bool:
    return _chat_engine() != "legacy"


def get_chat_opening(session_id: str | None = None) -> ChatTurnResult:
    if _use_orchestrator():
        from agent.inspire import chat_orchestrator_bridge

        return chat_orchestrator_bridge.get_opening(session_id)
    session = get_or_create_session(session_id)
    from engine.v4.intake.intake_copy import get_opening_nl

    try:
        _ensure_inspire_path()
        opening = get_opening_nl()
    except Exception:
        opening = (
            "Mooi — ik pak dit aan zoals een professionele voertuig-reclame studio dat zou doen. "
            "Daarna maak ik twee richtingen: Standard en Premium."
        )
    return ChatTurnResult(
        session_id=session.session_id,
        reply_nl=opening,
        brief_partial=dict(session.brief_partial),
        phase=1,
        ready_to_generate=False,
        brief_confirmed=False,
        missing_fields=_missing_fields(session.brief_partial),
        logo_reupload_required=logo_reupload_required(session.brief_partial),
        stap=1,
        stap_label="Bedrijf",
        opening_source="brain",
    )


def _ensure_inspire_path() -> None:
    repo = Path(os.getenv("INSPIRE_REPO_PATH", "/opt/inspire"))
    import sys

    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))


def _session_to_dict(session: ChatSession) -> dict[str, Any]:
    return {
        "session_id": session.session_id,
        "phase": session.phase,
        "brief_partial": session.brief_partial,
        "brief_confirmed": session.brief_confirmed,
        "messages": session.messages,
        "created_at": session.created_at,
    }


def _session_from_dict(data: dict[str, Any]) -> ChatSession:
    return ChatSession(
        session_id=str(data["session_id"]),
        phase=int(data.get("phase", 1)),
        brief_partial=dict(data.get("brief_partial") or {}),
        brief_confirmed=bool(data.get("brief_confirmed")),
        messages=list(data.get("messages") or []),
        created_at=str(data.get("created_at") or datetime.now(timezone.utc).isoformat()),
    )


def _persist_session(session: ChatSession) -> None:
    SESSIONS[session.session_id] = session
    chat_session_store.save_session(session.session_id, _session_to_dict(session))


def _has_contact_cta(brief: dict[str, Any]) -> bool:
    return bool(str(brief.get("telefoon") or "").strip() or str(brief.get("website") or "").strip())


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
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            logger.warning("LLM returned invalid JSON: %s", exc)
            return {
                "reply_nl": "Sorry, even een technische hapering. Kun je je vraag kort herhalen?",
                "phase": 1,
                "brief_updates": {},
                "brief_confirmed": False,
            }


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
        logger.warning("tier resolve failed: %s", exc)
        session.brief_partial["_tier_resolve_failed"] = True
        session.brief_partial.pop("mockup_b_sku", None)
        session.brief_partial.pop("mockup_a_sku", None)


def _normalize_vehicle_id(raw: str) -> str:
    if not raw:
        return ""
    v = str(raw).lower().replace("*", "").strip()
    if v in ("bestelbus_l", "bestelbus l") or "bus_l" in v:
        return "bus_l"
    if "bus_xl" in v:
        return "bus_xl"
    if "caddy" in v or "partner" in v:
        return "caddy"
    if "passenger" in v or "kombi" in v:
        return "passenger"
    return v.replace(" ", "_").lstrip("_")


def _parse_brand_colors(raw: str | list[Any] | None) -> list[str]:
    """Parse brand_colors from JSON form field or list (F-077 client → server)."""
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(c).strip() for c in raw if str(c).strip()]
    text = str(raw).strip()
    if not text or text == "[]":
        return []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(c).strip() for c in parsed if str(c).strip()]
    except json.JSONDecodeError:
        pass
    return []


def extract_brief_fields_from_text(
    brief: dict[str, Any],
    text: str,
    *,
    inline: bool = False,
) -> dict[str, Any]:
    """Backfill brief from NL user message or phase-7 summary (F-011/F-017)."""
    updates: dict[str, Any] = {}
    if not text or not str(text).strip():
        return updates

    val_pat = r"([^\n.]+)" if inline else r"([^\n]+)"

    def pick(key: str, label: str, *, pattern: str | None = None) -> None:
        if str(brief.get(key) or "").strip():
            return
        if pattern is None:
            pattern = rf"(?:\*\*)?{label}(?:\*\*)?:\s*{val_pat}"
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            val = m.group(1).strip().replace("*", "").strip()
            if inline and val.endswith("."):
                val = val[:-1].strip()
            updates[key] = val

    pick("bedrijfsnaam", "Bedrijfsnaam")
    pick("branche", "Branche")
    pick("diensten", "Diensten")
    pick("doelgroep", "Doelgroep")
    pick("positionering", "Positionering")
    pick("telefoon", "Telefoon")
    if inline:
        pick("website", "Website", pattern=rf"(?:\*\*)?Website(?:\*\*)?:\s*([\w./-]+(?:\.[\w./-]+)*)")
    else:
        pick("website", "Website")
    pick("slogan", "Slogan")

    if not str(brief.get("positionering") or "").strip() and not updates.get("positionering"):
        if re.search(r"\bbalanced\b", text, re.IGNORECASE):
            updates["positionering"] = "balanced"
        elif re.search(r"\bstrak\b", text, re.IGNORECASE):
            updates["positionering"] = "strak"

    if not str(brief.get("vehicle") or "").strip():
        veh = re.search(
            r"(?:\*\*)?Voertuig(?:\*\*)?:\s*([^(\n.]+)(?:\s*\(([a-z_]+)\))?",
            text,
            re.IGNORECASE,
        )
        if veh:
            updates["vehicle"] = _normalize_vehicle_id(veh.group(2) or veh.group(1))
        else:
            vid = re.search(r"\((bus_l|bus_xl|caddy|passenger)\)", text, re.IGNORECASE)
            if vid:
                updates["vehicle"] = vid.group(1).lower()
            elif re.search(r"\bbus_l\b", text, re.IGNORECASE):
                updates["vehicle"] = "bus_l"

    if updates.get("vehicle"):
        updates["vehicle"] = _normalize_vehicle_id(str(updates["vehicle"]))

    if not str(brief.get("primary_cta") or "").strip():
        website = str(updates.get("website") or brief.get("website") or "").strip()
        telefoon = str(updates.get("telefoon") or brief.get("telefoon") or "").strip()
        if website:
            updates["primary_cta"] = "website"
        elif telefoon:
            updates["primary_cta"] = "telefoon"

    return updates


def parse_user_message_fields(brief: dict[str, Any], message: str) -> dict[str, Any]:
    """Structured fields from client chat input (inline NL format)."""
    return extract_brief_fields_from_text(brief, message, inline=True)


def parse_summary_fields(brief: dict[str, Any], reply_nl: str) -> dict[str, Any]:
    """Backfill brief from phase-7 summary when LLM omits brief_updates (F-011)."""
    return extract_brief_fields_from_text(brief, reply_nl, inline=False)


def missing_fields(brief: dict[str, Any]) -> list[str]:
    """Public wrapper for brief completeness checks (API + tests)."""
    if _use_orchestrator():
        try:
            _ensure_inspire_path()
            from engine.v4.intake import chat_bridge

            _, missing = chat_bridge.compute_ready_pre_confirm(brief)
            return missing
        except Exception:
            pass
    return _missing_fields(brief)


def logo_reupload_required(brief: dict[str, Any]) -> bool:
    """Server stores logo filename only — client must hold File bytes for generate."""
    return bool(str(brief.get("logo_file") or "").strip())


def _missing_fields(brief: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    has_logo = bool(str(brief.get("logo_file") or "").strip())
    for fld in REQUIRED_BRIEF_FIELDS:
        # brand_colors extracted client-side from logo; generate sends JSON (brain/inspiration-contract)
        if fld == "brand_colors" and has_logo:
            continue
        val = brief.get(fld)
        if val is None or val == "" or val == []:
            missing.append(fld)
    return missing


def _compute_ready(session: ChatSession) -> bool:
    """Brief complete for mockups — confirmation is UI-only (not via chat LLM)."""
    if session.phase < 7:
        return False
    if session.brief_partial.get("_tier_resolve_failed"):
        return False
    if not _has_contact_cta(session.brief_partial):
        return False
    return len(_missing_fields(session.brief_partial)) == 0


def mark_brief_confirmed(session_id: str) -> None:
    """Set confirmed after explicit client action (generate form / future confirm endpoint)."""
    if _use_orchestrator():
        from agent.inspire import chat_orchestrator_bridge

        raw = chat_session_store.load_session(session_id)
        if raw and int(raw.get("schema_version") or 0) == 2:
            raw["brief_confirmed"] = True
            chat_session_store.save_session(session_id, raw)
            return
    session = get_or_create_session(session_id)
    session.brief_confirmed = True
    _persist_session(session)


def compute_ready(session: ChatSession) -> bool:
    if _use_orchestrator():
        try:
            _ensure_inspire_path()
            from engine.v4.intake import chat_bridge

            ready, _ = chat_bridge.compute_ready_pre_confirm(session.brief_partial)
            return ready and session.phase >= 7
        except Exception:
            pass
    return _compute_ready(session)


def get_session(session_id: str) -> ChatSession | None:
    if session_id in SESSIONS:
        return SESSIONS[session_id]
    if _use_orchestrator():
        from agent.inspire import chat_orchestrator_bridge

        orch = chat_orchestrator_bridge.load_chat_session(session_id)
        if orch:
            SESSIONS[session_id] = orch
            return orch
    raw = chat_session_store.load_session(session_id)
    if not raw:
        return None
    if int(raw.get("schema_version") or 0) == 2:
        return None
    session = _session_from_dict(raw)
    SESSIONS[session_id] = session
    return session


def get_or_create_session(session_id: str | None) -> ChatSession:
    if session_id:
        existing = get_session(session_id)
        if existing:
            return existing
    sid = session_id or str(uuid.uuid4())
    session = ChatSession(session_id=sid)
    _persist_session(session)
    return session


def attach_logo(session_id: str, filename: str) -> None:
    session = get_or_create_session(session_id)
    session.brief_partial["logo_file"] = filename
    _persist_session(session)


def _extract_inspire_email(
    message: str,
    field_updates: dict[str, Any] | None,
    brief_partial: dict[str, Any] | None,
) -> Optional[str]:
    for blob in (field_updates, brief_partial):
        if not isinstance(blob, dict):
            continue
        raw = blob.get("email")
        if isinstance(raw, str) and raw.strip():
            m = _EMAIL_RE.search(raw.strip())
            if m:
                return m.group(0).lower()
    m = _EMAIL_RE.search(message or "")
    return m.group(0).lower() if m else None


def _has_inspire_consent(
    message: str,
    field_updates: dict[str, Any] | None,
    brief_partial: dict[str, Any] | None,
) -> bool:
    for blob in (field_updates, brief_partial):
        if isinstance(blob, dict) and blob.get("consent_lead_storage") is True:
            return True
    return bool(_CONSENT_RE.search(message or ""))


def _maybe_persist_inspire_lead(
    *,
    session_id: str,
    message: str,
    field_updates: dict[str, Any] | None,
    brief_partial: dict[str, Any] | None,
) -> Optional[str]:
    """Durable lead only with email + consent (RODO). REV-DEMAND-03."""
    email = _extract_inspire_email(message, field_updates, brief_partial)
    if not email or not _has_inspire_consent(message, field_updates, brief_partial):
        return None
    try:
        from agent.db import db_create_lead
    except Exception as e:
        logger.error(
            "[INSPIRE] lead import failed session=%s: %s",
            session_id,
            e,
            exc_info=True,
        )
        return None

    name = None
    if isinstance(brief_partial, dict):
        raw_name = brief_partial.get("bedrijfsnaam") or brief_partial.get("name")
        if isinstance(raw_name, str) and raw_name.strip():
            name = raw_name.strip()[:120]

    try:
        lead_id, status = db_create_lead(
            {
                "email": email,
                "name": name,
                "source": "inspire",
                "consent_status": True,
                "game_score": None,
                "reward_tier": f"inspire:{(session_id or '')[:32]}",
            }
        )
    except Exception as e:
        logger.error(
            "[INSPIRE] lead persist failed session=%s: %s - %s",
            session_id,
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None
    if status in ("success", "duplicate") and lead_id:
        logger.info(
            "[INSPIRE] lead %s id=%s session=%s",
            status,
            lead_id,
            session_id,
        )
        return str(lead_id)
    return None


def _attach_inspire_lead(
    result: ChatTurnResult,
    *,
    message: str,
    field_updates: dict[str, Any] | None,
) -> ChatTurnResult:
    lead_id = _maybe_persist_inspire_lead(
        session_id=result.session_id,
        message=message,
        field_updates=field_updates,
        brief_partial=result.brief_partial,
    )
    if not lead_id:
        return result
    return replace(result, lead_id=lead_id)


def process_chat_turn(
    *,
    session_id: str | None,
    message: str,
    logo_filename: str | None = None,
    brand_colors: str | list[Any] | None = None,
    field_updates: dict[str, Any] | None = None,
    quick_reply_id: str | None = None,
    quick_reply_field: str | None = None,
) -> ChatTurnResult:
    if _use_orchestrator():
        from agent.inspire import chat_orchestrator_bridge

        colors = _parse_brand_colors(brand_colors)
        result = chat_orchestrator_bridge.process_turn(
            session_id=session_id,
            message=message,
            field_updates=field_updates,
            quick_reply_id=quick_reply_id,
            quick_reply_field=quick_reply_field,
            logo_filename=logo_filename,
            brand_colors=colors or None,
        )
        return _attach_inspire_lead(
            result, message=message, field_updates=field_updates
        )

    session = get_or_create_session(session_id)
    if logo_filename:
        session.brief_partial["logo_file"] = logo_filename

    colors = _parse_brand_colors(brand_colors)
    if colors:
        session.brief_partial["brand_colors"] = colors

    user_msg = message.strip()
    if not user_msg and not logo_filename:
        raise ValueError("Bericht mag niet leeg zijn.")

    if user_msg:
        session.messages.append({"role": "user", "content": user_msg})
        user_updates = parse_user_message_fields(session.brief_partial, user_msg)
        if user_updates:
            _merge_brief(session, user_updates)
        _resolve_tier_skus_if_ready(session)

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
    session.phase = max(1, min(7, session.phase))

    updates = parsed.get("brief_updates") or {}
    if isinstance(updates, dict):
        _merge_brief(session, updates)

    if session.phase >= 7 and reply_nl:
        summary_updates = parse_summary_fields(session.brief_partial, reply_nl)
        if summary_updates:
            _merge_brief(session, summary_updates)

    # brief_confirmed is never set from LLM JSON — only mark_brief_confirmed() / generate path.

    _resolve_tier_skus_if_ready(session)
    if session.brief_partial.get("_tier_resolve_failed"):
        reply_nl = (
            "**Voertuigtype niet herkend.** Kies opnieuw: Caddy, Bus L, Bus XL of Personenbus. "
            "Mock-ups zijn pas mogelijk na een geldige voertuigkeuze.\n\n" + reply_nl
        )
    ready = _compute_ready(session)
    missing = _missing_fields(session.brief_partial)
    if not ready and session.phase >= 7:
        logger.info(
            "ready_to_generate=false session_id=%s missing_fields=%s",
            session.session_id,
            missing,
        )

    session.messages.append({"role": "assistant", "content": reply_nl})
    _persist_session(session)

    result = ChatTurnResult(
        session_id=session.session_id,
        reply_nl=reply_nl,
        brief_partial=dict(session.brief_partial),
        phase=session.phase,
        ready_to_generate=ready,
        brief_confirmed=session.brief_confirmed,
        missing_fields=missing,
        logo_reupload_required=logo_reupload_required(session.brief_partial),
        stap=session.phase,
        stap_label="",
        opening_source="legacy",
    )
    return _attach_inspire_lead(
        result, message=user_msg or message, field_updates=field_updates
    )
