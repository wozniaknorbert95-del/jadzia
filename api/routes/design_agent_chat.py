"""Design Agent GPT chat advisor endpoints."""

from __future__ import annotations

from fastapi import APIRouter, File, Form, Header, HTTPException, Request, UploadFile

from agent.design_agent_service import _verify_api_key
from agent.inspire.chat_advisor import compute_ready, get_session, process_chat_turn
from core.models import (
    DesignAgentChatRequest,
    DesignAgentChatResponse,
    DesignAgentChatSessionResponse,
)

router = APIRouter(tags=["design-agent"])

_CHAT_RATE: dict[str, list[float]] = {}
_CHAT_RATE_LIMIT = 30
_CHAT_RATE_WINDOW_SEC = 3600


def _check_chat_rate_limit(client_ip: str) -> None:
    import time

    now = time.time()
    hits = _CHAT_RATE.get(client_ip, [])
    hits = [t for t in hits if now - t < _CHAT_RATE_WINDOW_SEC]
    if len(hits) >= _CHAT_RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Te veel chatberichten. Probeer het over een uur opnieuw.",
        )
    hits.append(now)
    _CHAT_RATE[client_ip] = hits


@router.post("/api/v1/design-agent/chat", response_model=DesignAgentChatResponse)
async def design_agent_chat(
    request: Request,
    request_body: DesignAgentChatRequest,
    x_fg_design_agent_key: str | None = Header(None, alias="X-FG-Design-Agent-Key"),
) -> DesignAgentChatResponse:
    """GPT marketing advisor chat turn (JSON body)."""
    _verify_api_key(x_fg_design_agent_key)
    client_ip = request.client.host if request.client else "unknown"
    _check_chat_rate_limit(client_ip)
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
    _check_chat_rate_limit(client_ip)
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
    return DesignAgentChatSessionResponse(
        session_id=session.session_id,
        brief_partial=dict(session.brief_partial),
        phase=session.phase,
        ready_to_generate=compute_ready(session),
        brief_confirmed=session.brief_confirmed,
        messages_count=len(session.messages),
    )
