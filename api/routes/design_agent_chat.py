"""Design Agent GPT chat advisor endpoints."""

from __future__ import annotations

from fastapi import APIRouter, File, Form, Header, HTTPException, Request, Response, UploadFile

from agent.design_agent_service import _verify_api_key
from agent.inspire.chat_advisor import (
    compute_ready,
    get_chat_opening,
    get_session,
    logo_reupload_required,
    missing_fields,
    process_chat_turn,
)
from agent.inspire.chat_locale import error_message, normalize_locale
from agent.rate_store import check_and_record
from core.models import (
    DesignAgentChatRequest,
    DesignAgentChatResponse,
    DesignAgentChatSessionResponse,
)

router = APIRouter(tags=["design-agent"])

_CHAT_RATE_WINDOW_SEC = 3600

_NO_CACHE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
}


def _apply_no_cache(response: Response) -> None:
    for key, value in _NO_CACHE_HEADERS.items():
        response.headers[key] = value


def _chat_rate_limit() -> int:
    import os

    try:
        return max(30, int(os.getenv("DA_CHAT_RATE_LIMIT", "200")))
    except ValueError:
        return 200


def _rate_bucket(client_ip: str, session_id: str | None) -> str:
    if session_id and session_id.strip():
        return f"session:{session_id.strip()}"
    return f"ip:{client_ip}"


def _check_chat_rate_limit(
    client_ip: str,
    session_id: str | None = None,
    *,
    locale: str | None = None,
) -> None:
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
                detail=error_message("rate_limit_chat", locale),
            ) from exc
        raise


def _to_response(result) -> DesignAgentChatResponse:
    reply = getattr(result, "reply", None) or result.reply_nl
    loc = getattr(result, "locale", None) or normalize_locale(
        (result.brief_partial or {}).get("locale")
    )
    return DesignAgentChatResponse(
        session_id=result.session_id,
        reply=reply,
        reply_nl=result.reply_nl or reply,
        brief_partial=result.brief_partial,
        phase=result.phase,
        ready_to_generate=result.ready_to_generate,
        brief_confirmed=result.brief_confirmed,
        missing_fields=result.missing_fields,
        logo_reupload_required=result.logo_reupload_required,
        stap=result.stap,
        stap_label=result.stap_label,
        quick_replies=result.quick_replies,
        quick_reply_field=result.quick_reply_field,
        quick_previews=getattr(result, "quick_previews", None) or [],
        opening_source=result.opening_source,
        lead_id=getattr(result, "lead_id", None),
        locale=loc,
    )


@router.get("/api/v1/design-agent/chat/opening", response_model=DesignAgentChatResponse)
async def design_agent_chat_opening(
    request: Request,
    response: Response,
    session_id: str | None = None,
    locale: str | None = None,
    x_fg_design_agent_key: str | None = Header(None, alias="X-FG-Design-Agent-Key"),
) -> DesignAgentChatResponse:
    """Deterministic brain opening — no LLM, no 'Hoi'. Always fresh session (ignore session_id)."""
    _verify_api_key(x_fg_design_agent_key)
    client_ip = request.client.host if request.client else "unknown"
    _check_chat_rate_limit(client_ip, None, locale=locale)
    try:
        result = get_chat_opening(None, locale=locale)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    _apply_no_cache(response)
    return _to_response(result)


@router.post("/api/v1/design-agent/chat", response_model=DesignAgentChatResponse)
async def design_agent_chat(
    request: Request,
    response: Response,
    request_body: DesignAgentChatRequest,
    x_fg_design_agent_key: str | None = Header(None, alias="X-FG-Design-Agent-Key"),
) -> DesignAgentChatResponse:
    """GPT marketing advisor chat turn (JSON body)."""
    _verify_api_key(x_fg_design_agent_key)
    client_ip = request.client.host if request.client else "unknown"
    loc = request_body.locale
    _check_chat_rate_limit(client_ip, request_body.session_id, locale=loc)
    if (
        not request_body.message.strip()
        and not request_body.field_updates
        and not request_body.quick_reply_id
    ):
        raise HTTPException(status_code=400, detail=error_message("empty_message", loc))
    try:
        result = process_chat_turn(
            session_id=request_body.session_id,
            message=request_body.message,
            field_updates=request_body.field_updates,
            quick_reply_id=request_body.quick_reply_id,
            quick_reply_field=request_body.quick_reply_field,
            locale=loc,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    _apply_no_cache(response)
    return _to_response(result)


@router.post("/api/v1/design-agent/chat/turn", response_model=DesignAgentChatResponse)
async def design_agent_chat_multipart(
    request: Request,
    response: Response,
    message: str = Form(""),
    session_id: str = Form(""),
    brand_colors: str = Form("[]"),
    quick_reply_id: str = Form(""),
    quick_reply_field: str = Form(""),
    locale: str = Form(""),
    logo: UploadFile | None = File(None),
    vehicle_photo: UploadFile | None = File(None),
    x_fg_design_agent_key: str | None = Header(None, alias="X-FG-Design-Agent-Key"),
) -> DesignAgentChatResponse:
    """Chat turn with optional logo + vehicle photo upload (multipart)."""
    _verify_api_key(x_fg_design_agent_key)
    client_ip = request.client.host if request.client else "unknown"
    loc = locale or None
    _check_chat_rate_limit(client_ip, session_id or None, locale=loc)
    logo_name = logo.filename if logo and logo.filename else None
    logo_bytes: bytes | None = None
    if logo and logo.filename:
        logo_bytes = await logo.read()
    if vehicle_photo and vehicle_photo.filename and message:
        message = f"{message.strip()} [foto: {vehicle_photo.filename}]".strip()
    elif vehicle_photo and vehicle_photo.filename:
        message = message or f"Bus foto: {vehicle_photo.filename}"
    try:
        result = process_chat_turn(
            session_id=session_id or None,
            message=message,
            logo_filename=logo_name,
            logo_bytes=logo_bytes,
            brand_colors=brand_colors,
            quick_reply_id=quick_reply_id or None,
            quick_reply_field=quick_reply_field or None,
            locale=loc,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    _apply_no_cache(response)
    return _to_response(result)


@router.delete("/api/v1/design-agent/chat/{session_id}", status_code=204, response_class=Response)
async def design_agent_chat_session_delete(
    session_id: str,
    x_fg_design_agent_key: str | None = Header(None, alias="X-FG-Design-Agent-Key"),
) -> Response:
    """Ops/HITL — purge persisted orchestrator session."""
    _verify_api_key(x_fg_design_agent_key)
    from agent.inspire import chat_session_store

    chat_session_store.delete_session(session_id)
    return Response(status_code=204)


@router.get(
    "/api/v1/design-agent/chat/{session_id}",
    response_model=DesignAgentChatSessionResponse,
)
async def design_agent_chat_session(
    response: Response,
    session_id: str,
    locale: str | None = None,
    x_fg_design_agent_key: str | None = Header(None, alias="X-FG-Design-Agent-Key"),
) -> DesignAgentChatSessionResponse:
    """Return accumulated brief for a chat session."""
    _verify_api_key(x_fg_design_agent_key)
    session = get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=error_message("session_not_found", locale),
        )
    brief = dict(session.brief_partial)
    last_reply = ""
    for msg in reversed(session.messages):
        if msg.get("role") == "assistant":
            last_reply = str(msg.get("content") or "")
            break
    tail = session.messages[-5:] if session.messages else []
    stap = int(brief.get("_stap") or session.phase)
    loc = normalize_locale(locale or brief.get("locale"))
    _apply_no_cache(response)
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
        last_reply=last_reply,
        messages_tail=tail,
        stap=stap,
        stap_label="",
        quick_replies=[],
        locale=loc,
    )
