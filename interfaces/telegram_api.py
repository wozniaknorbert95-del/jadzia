"""
Telegram API Router (Transfer Protocol V4).
Uses Worker API (POST/GET /worker/task, POST /worker/task/{id}/input) with JWT.
Commands: /zadanie, /status, /cofnij, /pomoc. Inline keyboard for approval (diff_ready).
"""

import time
from typing import Optional, Tuple

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from agent.telegram_formatter import (
    format_response_for_telegram,
    format_error_for_telegram,
    get_help_message,
)
from agent.telegram_validator import (
    TelegramWebhookRequest,
    validate_webhook_secret,
    validate_user_whitelist,
    get_jadzia_chat_id,
)
from interfaces.telegram_worker_client import (
    get_bot_jwt_token,
    get_base_url,
    create_task,
    get_task,
    submit_input,
    do_rollback,
)

router = APIRouter(prefix="/telegram", tags=["telegram"])

# In-memory: chat_id -> last task_id (for /status and approval)
_telegram_chat_to_task_id: dict[str, str] = {}


def parse_telegram_command(message: str, callback_data: Optional[str] = None) -> Tuple[str, str]:
    """
    Parse webhook input into (command, payload).
    command: "zadanie" | "status" | "cofnij" | "pomoc" | "callback" | "approval" | "message"
    payload: instruction text, or callback_data, or "true"/"false" for approval.
    """
    if callback_data:
        return "callback", callback_data
    msg = (message or "").strip()
    lower = msg.lower()
    if lower in ("/status", "status"):
        return "status", ""
    if lower in ("/cofnij", "cofnij"):
        return "cofnij", ""
    if lower in ("/pomoc", "pomoc", "/help", "help"):
        return "pomoc", ""
    if msg.startswith("/zadanie"):
        rest = msg[len("/zadanie"):].strip()
        return "zadanie", rest
    if lower in ("tak", "nie", "t", "n", "yes", "no"):
        return "approval", "true" if lower in ("tak", "t", "yes") else "false"
    return "message", msg


def build_inline_keyboard_approval(task_id: str) -> dict:
    """Telegram InlineKeyboardMarkup: Tak / Nie with callback_data task_id:approve:yes / no."""
    return {
        "inline_keyboard": [
            [
                {"text": "Tak", "callback_data": f"{task_id}:approve:yes"},
                {"text": "Nie", "callback_data": f"{task_id}:approve:no"},
            ]
        ]
    }


def parse_callback_approval(callback_data: str) -> Optional[Tuple[str, bool]]:
    """Parse callback_data 'task_id:approve:yes' or 'task_id:approve:no'. Returns (task_id, approval) or None."""
    if not callback_data or ":" not in callback_data:
        return None
    parts = callback_data.split(":", 2)
    if len(parts) != 3 or parts[1] != "approve":
        return None
    task_id, _, choice = parts
    if choice == "yes":
        return (task_id.strip(), True)
    if choice == "no":
        return (task_id.strip(), False)
    return None


class TelegramWebhookResponse(BaseModel):
    """Response for n8n to forward to Telegram."""
    success: bool
    messages: list
    awaiting_input: bool = False
    operation_id: Optional[str] = None
    reply_markup: Optional[dict] = None
    error: Optional[dict] = None


@router.post("/webhook", response_model=TelegramWebhookResponse)
async def telegram_webhook(
    request: TelegramWebhookRequest,
    x_webhook_secret: Optional[str] = Header(None),
):
    """Main webhook: validate, route command, call Worker API, return formatted messages + optional reply_markup."""
    start_time = time.time()

    try:
        validate_webhook_secret(x_webhook_secret)
        validate_user_whitelist(request.user_id)
    except HTTPException as e:
        if e.status_code == 401:
            error_type = "unauthorized"
        elif e.status_code == 403:
            error_type = "forbidden"
        else:
            error_type = "internal"
        return TelegramWebhookResponse(
            success=False,
            messages=[{"text": format_error_for_telegram(error_type, user_id=request.user_id), "parse_mode": "MarkdownV2"}],
            error={"type": error_type, "status_code": e.status_code, "detail": str(e.detail)},
        )

    chat_id = get_jadzia_chat_id(request.user_id)
    jwt_token = get_bot_jwt_token()
    base_url = get_base_url()

    if not jwt_token:
        return TelegramWebhookResponse(
            success=False,
            messages=[{"text": format_error_for_telegram("internal", operation_id="no_jwt"), "parse_mode": "MarkdownV2"}],
            error={"type": "internal", "message": "TELEGRAM_BOT_JWT_TOKEN or JWT_SECRET not set"},
        )

    command, payload = parse_telegram_command(request.message, request.callback_data)
    print(f"📱 Telegram webhook: chat_id={chat_id}, command={command}, payload_len={len(payload)}")

    try:
        if command == "callback":
            parsed = parse_callback_approval(payload)
            if not parsed:
                msg = format_response_for_telegram("Nieprawidłowy callback.", awaiting_input=False)
                return TelegramWebhookResponse(success=True, messages=msg)
            task_id, approval = parsed
            result = await submit_input(task_id, jwt_token, base_url, approval=approval)
            _telegram_chat_to_task_id[chat_id] = task_id
            response_text = result.get("response", "") or ( "Zatwierdzono." if approval else "Odrzucono." )
            awaiting = result.get("awaiting_input", False)
            status = result.get("status", "")
            messages = format_response_for_telegram(response_text, awaiting_input=awaiting)
            reply_markup = build_inline_keyboard_approval(task_id) if (status == "diff_ready" and awaiting) else None
            return TelegramWebhookResponse(success=True, messages=messages, awaiting_input=awaiting, reply_markup=reply_markup)

        if command == "approval":
            task_id = _telegram_chat_to_task_id.get(chat_id)
            if not task_id:
                messages = format_response_for_telegram("Brak aktywnego zadania do zatwierdzenia. Użyj /zadanie.", awaiting_input=False)
                return TelegramWebhookResponse(success=True, messages=messages)
            approval = payload == "true"
            result = await submit_input(task_id, jwt_token, base_url, approval=approval)
            response_text = result.get("response", "") or ("Zatwierdzono." if approval else "Odrzucono.")
            awaiting = result.get("awaiting_input", False)
            status = result.get("status", "")
            messages = format_response_for_telegram(response_text, awaiting_input=awaiting)
            reply_markup = build_inline_keyboard_approval(task_id) if (status == "diff_ready" and awaiting) else None
            return TelegramWebhookResponse(success=True, messages=messages, awaiting_input=awaiting, reply_markup=reply_markup)

        if command == "pomoc":
            text = get_help_message()
            messages = format_response_for_telegram(text, awaiting_input=False)
            return TelegramWebhookResponse(success=True, messages=messages)

        if command == "cofnij":
            result = await do_rollback(base_url)
            status = result.get("status", "error")
            msg = result.get("message", str(result))
            if status == "ok":
                text = f"✅ Cofnięto.\n{msg}"
            else:
                text = f"⚠️ Cofnięcie: {msg}"
            messages = format_response_for_telegram(text, awaiting_input=False)
            return TelegramWebhookResponse(success=True, messages=messages)

        if command == "status":
            task_id = _telegram_chat_to_task_id.get(chat_id)
            if not task_id:
                messages = format_response_for_telegram("Brak aktywnego zadania. Użyj /zadanie.", awaiting_input=False)
                return TelegramWebhookResponse(success=True, messages=messages)
            result = await get_task(task_id, jwt_token, base_url)
            response_text = result.get("response", "") or f"Status: {result.get('status', '?')}"
            awaiting = result.get("awaiting_input", False)
            messages = format_response_for_telegram(response_text, awaiting_input=awaiting)
            reply_markup = build_inline_keyboard_approval(task_id) if (result.get("status") == "diff_ready" and awaiting) else None
            return TelegramWebhookResponse(success=True, messages=messages, awaiting_input=awaiting, reply_markup=reply_markup)

        # zadanie | message -> create task
        instruction = payload if payload else request.message.strip()
        if not instruction:
            messages = format_response_for_telegram("Podaj treść zadania, np. /zadanie zmień kolor przycisku", awaiting_input=False)
            return TelegramWebhookResponse(success=True, messages=messages)

        create_res = await create_task(instruction, chat_id, jwt_token, base_url, test_mode=False)
        task_id = create_res.get("task_id", "")
        _telegram_chat_to_task_id[chat_id] = task_id

        if create_res.get("status") == "queued":
            pos = create_res.get("position_in_queue", 0)
            messages = format_response_for_telegram(f"Zadanie dodane do kolejki (pozycja {pos}).", awaiting_input=False)
            return TelegramWebhookResponse(success=True, messages=messages)

        # processing: get task to retrieve response text (create_task already waited)
        result = await get_task(task_id, jwt_token, base_url)
        response_text = result.get("response", "") or "Zadanie w toku."
        awaiting = result.get("awaiting_input", False)
        messages = format_response_for_telegram(response_text, awaiting_input=awaiting)
        reply_markup = build_inline_keyboard_approval(task_id) if (result.get("status") == "diff_ready" and awaiting) else None

        duration_ms = int((time.time() - start_time) * 1000)
        print(f"✅ Telegram response: {len(messages)} messages, {duration_ms}ms, awaiting={awaiting}")
        return TelegramWebhookResponse(success=True, messages=messages, awaiting_input=awaiting, reply_markup=reply_markup)

    except Exception as e:
        print(f"❌ Telegram webhook error: {e}")
        import traceback
        traceback.print_exc()
        err_msg = format_error_for_telegram("internal", operation_id=chat_id)
        return TelegramWebhookResponse(
            success=False,
            messages=[{"text": err_msg, "parse_mode": "MarkdownV2"}],
            error={"type": "internal", "message": str(e)},
        )


@router.get("/health")
async def telegram_health():
    """Health check for Telegram integration."""
    from agent.telegram_validator import get_configuration_status
    config = get_configuration_status()
    jwt_ok = bool(get_bot_jwt_token())
    return {
        "status": "ok" if (config["is_fully_configured"] and jwt_ok) else "warning",
        "service": "telegram-webhook",
        "configuration": {**config, "jwt_configured": jwt_ok},
        "message": "Ready" if (config["is_fully_configured"] and jwt_ok) else "Missing configuration (check .env)",
    }


@router.post("/test")
async def telegram_test(message: str = "Test", user_id: str = "test_user"):
    """Test endpoint for formatting (no Worker API)."""
    from agent.telegram_formatter import format_response_for_telegram, escape_markdown_v2
    test_response = f"**Test**\n\nMessage: {escape_markdown_v2(message)}\nUser: `{user_id}`"
    messages = format_response_for_telegram(test_response.strip(), awaiting_input=False)
    return {"success": True, "messages": messages, "note": "Use /telegram/webhook for production."}
