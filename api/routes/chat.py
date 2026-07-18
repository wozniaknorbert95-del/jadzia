"""Chat and widget endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_claude_service, verify_jwt
from core.models import ChatRequest, ChatResponse, CustomerChatRequest, CustomerChatResponse
from core.services import ClaudeService

router = APIRouter(tags=["chat"])


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
async def widget_chat(request: CustomerChatRequest):
    """Customer widget chat endpoint."""
    try:
        from agent.customer_agent import process_customer_message

        result = await process_customer_message(
            session_id=request.session_id,
            user_input=request.message,
        )
        return CustomerChatResponse(
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
