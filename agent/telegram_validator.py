"""
Telegram Security Validator
============================

Handles:
- Webhook secret validation (X-Webhook-Secret header)
- User whitelist verification
- Request structure validation
"""

import os
from typing import Optional, Tuple
from fastapi import Header, HTTPException
from pydantic import BaseModel, Field, root_validator, validator


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# Load from environment
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
ALLOWED_TELEGRAM_USERS_RAW = os.getenv("ALLOWED_TELEGRAM_USERS", "")

# Parse whitelist (comma-separated list of user IDs)
ALLOWED_TELEGRAM_USERS = set(
    user_id.strip() 
    for user_id in ALLOWED_TELEGRAM_USERS_RAW.split(",") 
    if user_id.strip()
)


# ═══════════════════════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════════════════════

class TelegramWebhookRequest(BaseModel):
    """
    Expected request structure from n8n webhook.
    n8n forwards Telegram updates in this format.
    Optional callback_data for inline button presses (e.g. task_id:approve:yes).
    """
    message: str = Field(default="", description="User message text")
    chat_id: str = Field(..., description="Telegram chat ID")
    user_id: str = Field(..., description="Telegram user ID")
    message_id: int = Field(..., description="Telegram message ID")
    callback_data: Optional[str] = Field(None, description="Inline keyboard callback (e.g. task_id:approve:yes)")

    @validator("message")
    def message_strip(cls, v):
        return (v or "").strip()

    @validator("user_id")
    def user_id_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("User ID cannot be empty")
        return v.strip()

    @root_validator(skip_on_failure=True)
    def require_message_or_callback(cls, values):
        if values.get("callback_data"):
            return values
        if not (values.get("message") or "").strip():
            raise ValueError("Message cannot be empty when callback_data is not provided")
        return values


# ═══════════════════════════════════════════════════════════════
# VALIDATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def validate_webhook_secret(x_webhook_secret: Optional[str] = Header(None)) -> bool:
    """
    Validate webhook secret from header.
    
    Args:
        x_webhook_secret: Secret from X-Webhook-Secret header
    
    Raises:
        HTTPException: If secret is invalid or missing
    
    Returns:
        True if valid
    """
    # Check if secret is configured
    if not TELEGRAM_WEBHOOK_SECRET:
        # If no secret configured, log warning but allow (dev mode)
        print("⚠️ WARNING: TELEGRAM_WEBHOOK_SECRET not configured!")
        return True
    
    # Check if secret provided in request
    if not x_webhook_secret:
        raise HTTPException(
            status_code=401,
            detail="Missing X-Webhook-Secret header"
        )
    
    # Verify secret matches
    if x_webhook_secret != TELEGRAM_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook secret"
        )
    
    return True


def validate_user_whitelist(user_id: str) -> bool:
    """
    Validate user is in whitelist.
    
    Args:
        user_id: Telegram user ID to check
    
    Raises:
        HTTPException: If user not whitelisted
    
    Returns:
        True if whitelisted
    """
    # Check if whitelist is configured
    if not ALLOWED_TELEGRAM_USERS:
        # If no whitelist, log warning but allow (dev mode)
        print("⚠️ WARNING: ALLOWED_TELEGRAM_USERS not configured! All users allowed.")
        return True
    
    # Check if user in whitelist
    if user_id not in ALLOWED_TELEGRAM_USERS:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "forbidden",
                "message": f"User {user_id} not whitelisted",
                "user_id": user_id
            }
        )
    
    return True


def validate_telegram_request(
    request: TelegramWebhookRequest,
    x_webhook_secret: Optional[str] = Header(None)
) -> Tuple[bool, Optional[str]]:
    """
    Complete validation pipeline for Telegram webhook request.
    
    Args:
        request: Parsed request body
        x_webhook_secret: Secret from header
    
    Returns:
        Tuple of (is_valid, error_message)
        - (True, None) if all validations pass
        - (False, error_msg) if any validation fails
    
    Note:
        This function catches HTTPExceptions from individual validators
        and returns them as (False, message) for easier handling in endpoint.
    """
    try:
        # Validate secret
        validate_webhook_secret(x_webhook_secret)
        
        # Validate user whitelist
        validate_user_whitelist(request.user_id)
        
        return True, None
    
    except HTTPException as e:
        # Extract error message
        if isinstance(e.detail, dict):
            error_msg = e.detail.get("message", str(e.detail))
        else:
            error_msg = str(e.detail)
        
        return False, error_msg


# ═══════════════════════════════════════════════════════════════
# SESSION MAPPING
# ═══════════════════════════════════════════════════════════════

def get_jadzia_chat_id(telegram_user_id: str) -> str:
    """
    Map Telegram user_id to JADZIA chat_id.
    Format: telegram_{user_id}
    """
    if telegram_user_id.startswith("telegram_"):
        return telegram_user_id
    return f"telegram_{telegram_user_id}"


def is_telegram_session(chat_id: str) -> bool:
    """
    Check if chat_id is from Telegram.
    
    Args:
        chat_id: Chat ID to check
    
    Returns:
        True if from Telegram source
    """
    return chat_id.startswith("telegram_")


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION HELPERS
# ═══════════════════════════════════════════════════════════════

def is_telegram_configured() -> bool:
    """
    Check if Telegram integration is properly configured.
    
    Returns:
        True if both secret and whitelist are set
    """
    return bool(TELEGRAM_WEBHOOK_SECRET and ALLOWED_TELEGRAM_USERS)


def get_configuration_status() -> dict:
    """
    Get current configuration status for debugging.
    
    Returns:
        Dict with configuration info (secrets masked)
    """
    return {
        "webhook_secret_configured": bool(TELEGRAM_WEBHOOK_SECRET),
        "whitelist_configured": bool(ALLOWED_TELEGRAM_USERS),
        "whitelisted_users_count": len(ALLOWED_TELEGRAM_USERS),
        "is_fully_configured": is_telegram_configured()
    }
