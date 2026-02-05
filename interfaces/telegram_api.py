"""
Telegram API Router
===================

FastAPI router for Telegram webhook integration.

Endpoint: POST /telegram-webhook
Accepts webhook calls from n8n, processes via agent, returns formatted response.
"""

import time
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

# Import from local modules (adjust imports based on actual structure)
# These will be imported from agent/ directory when integrated
try:
    from agent.telegram_formatter import (
        format_response_for_telegram,
        format_error_for_telegram,
        get_help_message,
        escape_markdown_v2
    )
    from agent.telegram_validator import (
        TelegramWebhookRequest,
        validate_webhook_secret,
        validate_user_whitelist,
        get_jadzia_chat_id
    )
    from agent.agent import process_message
    from agent.state import LockError
except ImportError:
    # Fallback for standalone testing
    print("⚠️ Warning: Could not import agent modules, using mocks")
    pass


# ═══════════════════════════════════════════════════════════════
# ROUTER SETUP
# ═══════════════════════════════════════════════════════════════

router = APIRouter(prefix="/telegram", tags=["telegram"])


# ═══════════════════════════════════════════════════════════════
# RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════

class TelegramWebhookResponse(BaseModel):
    """Response format for n8n to forward to Telegram"""
    success: bool
    messages: list  # List of {"text": str, "parse_mode": str}
    awaiting_input: bool = False
    operation_id: Optional[str] = None
    error: Optional[dict] = None


# ═══════════════════════════════════════════════════════════════
# WEBHOOK ENDPOINT
# ═══════════════════════════════════════════════════════════════

@router.post("/webhook", response_model=TelegramWebhookResponse)
async def telegram_webhook(
    request: TelegramWebhookRequest,
    x_webhook_secret: Optional[str] = Header(None)
):
    """
    Main Telegram webhook endpoint.
    
    Flow:
    1. Validate webhook secret
    2. Validate user whitelist
    3. Map user_id → chat_id
    4. Call process_message() (SYNC)
    5. Format response for Telegram
    6. Return to n8n
    
    Args:
        request: Webhook request from n8n
        x_webhook_secret: Security header
    
    Returns:
        TelegramWebhookResponse with messages for Telegram
    """
    start_time = time.time()
    
    # ═══════════════════════════════════════════════════════════
    # 1. VALIDATION
    # ═══════════════════════════════════════════════════════════
    
    try:
        validate_webhook_secret(x_webhook_secret)
        validate_user_whitelist(request.user_id)
    
    except HTTPException as e:
        # Convert HTTPException to user-friendly Telegram message
        if e.status_code == 401:
            error_type = "unauthorized"
        elif e.status_code == 403:
            error_type = "forbidden"
        else:
            error_type = "internal"
        
        error_msg = format_error_for_telegram(
            error_type,
            user_id=request.user_id
        )
        
        return TelegramWebhookResponse(
            success=False,
            messages=[{"text": error_msg, "parse_mode": "MarkdownV2"}],
            error={
                "type": error_type,
                "status_code": e.status_code,
                "detail": str(e.detail)
            }
        )
    
    # ═══════════════════════════════════════════════════════════
    # 2. SESSION MAPPING
    # ═══════════════════════════════════════════════════════════
    
    chat_id = get_jadzia_chat_id(request.user_id)
    
    # Log incoming request (optional, for debugging)
    print(f"📱 Telegram webhook: user_id={request.user_id}, chat_id={chat_id}, msg='{request.message[:50]}'")
    
    # ═══════════════════════════════════════════════════════════
    # 3. PROCESS MESSAGE
    # ═══════════════════════════════════════════════════════════
    
    try:
        # Call main agent function (SYNC mode)
        # Returns: (response_text, awaiting_input, input_type)
        response_text, awaiting_input, input_type = await process_message(
            user_input=request.message,
            chat_id=chat_id
        )
        
        # Extract operation_id from state if available
        from agent.state import get_operation_id
        operation_id = get_operation_id(chat_id=chat_id, source="telegram")
        
        # ═══════════════════════════════════════════════════════
        # 4. FORMAT RESPONSE
        # ═══════════════════════════════════════════════════════
        
        # Check if response contains diffs (simple heuristic)
        diffs = None
        if "```" in response_text and ("+++" in response_text or "---" in response_text):
            # Response likely contains diffs
            # For now, keep diffs in main text
            # TODO: Could parse and separate diffs if needed
            pass
        
        # Format for Telegram
        messages = format_response_for_telegram(
            text=response_text,
            awaiting_input=awaiting_input,
            diffs=diffs
        )
        
        # ═══════════════════════════════════════════════════════
        # 5. RETURN RESPONSE
        # ═══════════════════════════════════════════════════════
        
        duration_ms = int((time.time() - start_time) * 1000)
        print(f"✅ Telegram response: {len(messages)} messages, {duration_ms}ms, awaiting={awaiting_input}")
        
        return TelegramWebhookResponse(
            success=True,
            messages=messages,
            awaiting_input=awaiting_input,
            operation_id=operation_id
        )
    
    # ═══════════════════════════════════════════════════════════
    # ERROR HANDLING
    # ═══════════════════════════════════════════════════════════
    
    except LockError:
        # Agent is busy with another operation
        error_msg = format_error_for_telegram("locked", retry_after=5)
        
        return TelegramWebhookResponse(
            success=False,
            messages=[{"text": error_msg, "parse_mode": "MarkdownV2"}],
            error={
                "type": "locked",
                "retry_after": 5
            }
        )
    
    except Exception as e:
        # Unknown error
        error_type = "internal"
        
        # Try to get operation_id for error reporting
        try:
            from agent.state import get_operation_id
            operation_id = get_operation_id(chat_id=chat_id, source="telegram")
        except:
            operation_id = "unknown"
        
        error_msg = format_error_for_telegram(
            error_type,
            operation_id=operation_id
        )
        
        # Log error
        print(f"❌ Telegram webhook error: {e}")
        import traceback
        traceback.print_exc()
        
        return TelegramWebhookResponse(
            success=False,
            messages=[{"text": error_msg, "parse_mode": "MarkdownV2"}],
            error={
                "type": error_type,
                "message": str(e),
                "operation_id": operation_id
            }
        )


# ═══════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════

@router.get("/health")
async def telegram_health():
    """
    Health check for Telegram integration.
    
    Returns configuration status and readiness.
    """
    from agent.telegram_validator import get_configuration_status
    
    config = get_configuration_status()
    
    return {
        "status": "ok" if config["is_fully_configured"] else "warning",
        "service": "telegram-webhook",
        "configuration": config,
        "message": "Ready" if config["is_fully_configured"] else "Missing configuration (check .env)"
    }


# ═══════════════════════════════════════════════════════════════
# TEST ENDPOINT (optional, for debugging)
# ═══════════════════════════════════════════════════════════════

@router.post("/test")
async def telegram_test(
    message: str = "Test message",
    user_id: str = "test_user"
):
    """
    Test endpoint to verify Telegram formatting without going through webhook.
    
    Usage: POST /telegram/test?message=Hello&user_id=123
    """
    from agent.telegram_formatter import format_response_for_telegram, escape_markdown_v2
    
    # Simple test response
    test_response = f"""
**Test Response**

Your message: {escape_markdown_v2(message)}
User ID: `{user_id}`

This is a test of:
- MarkdownV2 escaping
- Message formatting
- Multi\\-line support

```python
# Code block test
def hello():
    return "world"
```
"""
    
    messages = format_response_for_telegram(
        text=test_response.strip(),
        awaiting_input=True
    )
    
    return {
        "success": True,
        "messages": messages,
        "note": "This is a test endpoint. Use /telegram/webhook for production."
    }
