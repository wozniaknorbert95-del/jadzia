"""Chat and widget endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError

from api.dependencies import get_claude_service, verify_jwt
from api.ingress import (
    WIDGET_BODY_MAX_BYTES,
    check_widget_rate_limit,
    read_limited_body_async,
    resolve_widget_session,
)
from core.models import ChatRequest, ChatResponse, CustomerChatRequest, CustomerChatResponse
from core.services import ClaudeService

router = APIRouter(tags=["chat"])
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    claude: ClaudeService = Depends(get_claude_service),
    _auth=Depends(verify_jwt),
):
    """Main endpoint for agent communication."""
    try:
        from core.agent import process_message

        response, awaiting_input, input_type = await process_message(
            user_input=request.message,
            chat_id=request.chat_id,
        )
        return ChatResponse(
            response=response,
            awaiting_input=awaiting_input,
            input_type=input_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/widget/chat", response_model=CustomerChatResponse)
async def widget_chat(request: Request):
    """Customer widget chat endpoint."""
    body = await read_limited_body_async(request, max_bytes=WIDGET_BODY_MAX_BYTES)
    try:
        payload = CustomerChatRequest.model_validate_json(body)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    session_id = resolve_widget_session(payload.session_id)
    check_widget_rate_limit(request, session_id)
    try:
        from agent.customer_agent import process_customer_message

        result = await process_customer_message(
            session_id=session_id,
            user_input=payload.message,
        )
        return CustomerChatResponse(
            session_id=session_id,
            reply=result.get("reply", ""),
            lead=result.get("lead", {}),
            lead_score=result.get("lead_score"),
            intent=result.get("intent"),
            category=result.get("category"),
            reason=result.get("reason"),
            wizard_deeplink=result.get("wizard_deeplink"),
            cta_sku=result.get("cta_sku"),
            lead_id=result.get("lead_id"),
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Widget chat processing failed")
        raise HTTPException(status_code=500, detail="Customer chat is temporarily unavailable")
