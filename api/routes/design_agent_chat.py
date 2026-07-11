"""Design Agent GPT chat advisor endpoints."""

from __future__ import annotations

from fastapi import APIRouter, File, Form, Header, HTTPException, Request, UploadFile

from agent.design_agent_service import _verify_api_key
from agent.rate_store import check_and_record
from agent.inspire.chat_advisor import (
    compute_ready,
    get_session,
    logo_reupload_required,
    missing_fields,
    process_chat_turn,
)
from core.models import (
    DesignAgentChatRequest,
    DesignAgentChatResponse,
    DesignAgentChatSessionResponse,
)

router = APIRouter(tags=["design-agent"])

_CHAT_RATE_WINDOW_SEC = 3600


def _chat_rate_limit() -> int:
    import os

    try:
        return max(30, int(os.getenv("DA_CHAT_RATE_LIMIT", "200")))
    except ValueError:
        return 200


def _rate_bucket(client_ip: str, session_id: str | None) -> str:
    """Per-session when known; otherwise per IP (shared NAT friendly for one intake)."""
    if session_id and session_id.strip():
        return f"session:{session_id.strip()}"
    return f"ip:{client_ip}"


def _check_chat_rate_limit(client_ip: str, session_id: str | None = None) -> None:
    limit = _chat_rate_limit()
    bucket = _rate_bucket(client_ip, session_id)
    try:
        check_and_record(
            bucket,
            window_sec=_CHAT_RATE_WINDOW_SEC,
            limit=limit,
        )
    except ValueError as exc:
        if str(exc) == "RATE_LIMIT":
            raise HTTPException(
                status_code=429,
                detail="Te veel chatberichten. Probeer het over een uur opnieuw.",
            ) from exc
        raise


@router.post("/api/v1/design-agent/chat", response_model=DesignAgentChatResponse)
async def design_agent_chat(
    request: Request,
    request_body: DesignAgentChatRequest,
    x_fg_design_agent_key: str | None = Header(None, alias="X-FG-Design-Agent-Key"),
) -> DesignAgentChatResponse:
    """GPT marketing advisor chat turn (JSON body)."""
    _verify_api_key(x_fg_design_agent_key)
    client_ip = request.client.host if request.client else "unknown"
    _check_chat_rate_limit(client_ip, request_body.session_id)
    try:
        result = process_chat_turn(
            session_id=request_body.session_id,
            message=request_body.message,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return DesignAgentChatResponse(
        session_id=result.session_id,
        reply_nl=result.reply_nl,
        brief_partial=result.brief_partial,
        phase=result.phase,
        ready_to_generate=result.ready_to_generate,
        brief_confirmed=result.brief_confirmed,
        missing_fields=result.missing_fields,
        logo_reupload_required=result.logo_reupload_required,
    )


@router.post("/api/v1/design-agent/chat/turn", response_model=DesignAgentChatResponse)
async def design_agent_chat_multipart(
    request: Request,
    message: str = Form(""),
    session_id: str = Form(""),
    logo: UploadFile | None = File(None),
    x_fg_design_agent_key: str | None = Header(None, alias="X-FG-Design-Agent-Key"),
) -> DesignAgentChatResponse:
    """Chat turn with optional logo upload (multipart)."""
    _verify_api_key(x_fg_design_agent_key)
    client_ip = request.client.host if request.client else "unknown"
    _check_chat_rate_limit(client_ip, session_id or None)
    logo_name = logo.filename if logo and logo.filename else None
    try:
        result = process_chat_turn(
            session_id=session_id or None,
            message=message,
            logo_filename=logo_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return DesignAgentChatResponse(
        session_id=result.session_id,
        reply_nl=result.reply_nl,
        brief_partial=result.brief_partial,
        phase=result.phase,
        ready_to_generate=result.ready_to_generate,
        brief_confirmed=result.brief_confirmed,
        missing_fields=result.missing_fields,
        logo_reupload_required=result.logo_reupload_required,
    )


@router.get(
    "/api/v1/design-agent/chat/{session_id}",
    response_model=DesignAgentChatSessionResponse,
)
async def design_agent_chat_session(
    session_id: str,
    x_fg_design_agent_key: str | None = Header(None, alias="X-FG-Design-Agent-Key"),
) -> DesignAgentChatSessionResponse:
    """Return accumulated brief for a chat session."""
    _verify_api_key(x_fg_design_agent_key)
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessie niet gevonden of verlopen.")
    brief = dict(session.brief_partial)
    last_reply = ""
    for msg in reversed(session.messages):
        if msg.get("role") == "assistant":
            last_reply = str(msg.get("content") or "")
            break
    return DesignAgentChatSessionResponse(
        session_id=session.session_id,
        brief_partial=brief,
        phase=session.phase,
        ready_to_generate=compute_ready(session),
        brief_confirmed=session.brief_confirmed,
        messages_count=len(session.messages),
        missing_fields=missing_fields(brief),
        logo_reupload_required=logo_reupload_required(brief),
        last_reply_nl=last_reply,
    )
