"""
Telegram API Router (Transfer Protocol V4).
Uses Worker API (POST/GET /worker/task, POST /worker/task/{id}/input) with JWT.
Commands: /zadanie, /status, /cofnij, /pomoc. Inline keyboard for approval (diff_ready).
When TELEGRAM_BOT_TOKEN is set, replies are sent to Telegram via sendMessage (direct webhook).
"""

import asyncio
import os
import time
import logging
from typing import Optional, Tuple, List

import httpx
from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, ValidationError

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_API_BASE = "https://api.telegram.org"

from agent.telegram_formatter import (
    format_response_for_telegram,
    format_error_for_telegram,
    get_help_message,
)
from agent.telegram_validator import (
    TelegramWebhookRequest,
    normalize_telegram_update,
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
logger = logging.getLogger(__name__)

# ── Idempotency: dedup Telegram updates by update_id (TTL cache) ──
_DEDUP_TTL_SECONDS = 300  # 5 minutes
_processed_updates: dict[int, float] = {}  # update_id -> timestamp


def _is_duplicate_update(update_id: int) -> bool:
    """Return True if this update_id was already processed (within TTL)."""
    now = time.time()
    # Evict expired entries (lazy cleanup, max 200 entries kept)
    if len(_processed_updates) > 200:
        expired = [uid for uid, ts in _processed_updates.items() if now - ts > _DEDUP_TTL_SECONDS]
        for uid in expired:
            _processed_updates.pop(uid, None)
    if update_id in _processed_updates:
        age = now - _processed_updates[update_id]
        if age < _DEDUP_TTL_SECONDS:
            return True
    _processed_updates[update_id] = now
    return False


def _get_task_id_for_chat(chat_id: str) -> Optional[str]:
    """Get active task_id for chat from DB only (SYSTEM_BIBLE: SQLite = source of truth)."""
    from agent.db import db_get_active_task, db_get_task
    try:
        task_id = db_get_active_task(chat_id, "telegram")
        if task_id and db_get_task(task_id) is not None:
            return task_id
        # Fallback: last non-terminal task (e.g. after restart when active_task_id is None)
        from agent.db import db_get_last_active_task
        last = db_get_last_active_task(chat_id, "telegram")
        return last["task_id"] if last else None
    except Exception as e:
        logger.warning("[Telegram] _get_task_id_for_chat failed: %s", e, extra={"chat_id": chat_id})
        return None


def parse_telegram_command(message: str, callback_data: Optional[str] = None) -> Tuple[str, str]:
    """
    Parse webhook input into (command, payload).
    command: "zadanie" | "status" | "cofnij" | "pomoc" | "callback" | "approval" | "message"
    payload: instruction text, or callback_data, or "true"/"false" for approval.
    Normalizes Telegram @BotUsername suffix (e.g. /pomoc@JadziaBot -> /pomoc) for matching.
    """
    if callback_data:
        return "callback", callback_data
    msg = (message or "").strip()
    lower = msg.lower()
    # First token only, strip @BotUsername for command matching (Telegram sends /cmd@BotName in groups)
    cmd_token = msg.split(None, 1)[0] if msg else ""
    cmd_only = cmd_token.split("@")[0] if "@" in cmd_token else cmd_token
    cmd_lower = cmd_only.lower()
    if cmd_lower in ("/status", "status"):
        return "status", ""
    if cmd_lower in ("/cofnij", "cofnij"):
        return "cofnij", ""
    if cmd_lower in ("/pomoc", "pomoc", "/help", "help"):
        return "pomoc", ""
    if cmd_only.startswith("/zadanie"):
        payload = msg[len(cmd_token):].strip()
        return "zadanie", payload
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
    """Response for n8n or direct Telegram (sendMessage when TELEGRAM_BOT_TOKEN set)."""
    success: bool
    messages: list
    awaiting_input: bool = False
    operation_id: Optional[str] = None
    reply_markup: Optional[dict] = None
    error: Optional[dict] = None


async def _send_telegram_replies(
    chat_id: str,
    response: TelegramWebhookResponse,
    callback_query_id: Optional[str] = None,
) -> None:
    """
    Send reply messages to Telegram via Bot API (sendMessage).
    If callback_query_id is set, call answerCallbackQuery first to clear loading state.
    Does not raise; logs errors.
    """
    if not TELEGRAM_BOT_TOKEN:
        return
    if not response.messages:
        logger.debug("[Telegram] sendMessage skipped: response.messages is empty (chat_id=%s)", chat_id)
        return
    url_base = f"{TELEGRAM_API_BASE}/bot{TELEGRAM_BOT_TOKEN}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if callback_query_id:
                await client.post(
                    f"{url_base}/answerCallbackQuery",
                    json={"callback_query_id": callback_query_id},
                )
            reply_markup = response.reply_markup
            sent = 0
            for i, msg in enumerate(response.messages):
                text = msg.get("text") if isinstance(msg, dict) else None
                if not text:
                    continue
                payload = {"chat_id": chat_id, "text": text}
                if msg.get("parse_mode"):
                    payload["parse_mode"] = msg["parse_mode"]
                if reply_markup and i == 0:
                    payload["reply_markup"] = reply_markup
                log_payload = {**payload, "text": (text[:300] + "..." if len(text) > 300 else text)}
                logger.debug("[Telegram] sendMessage request: %s", log_payload)
                r = await client.post(f"{url_base}/sendMessage", json=payload)
                if r.status_code >= 400:
                    try:
                        body = r.json()
                    except Exception:
                        body = r.text
                    logger.error("[Telegram] sendMessage %s response: %s", r.status_code, body)
                r.raise_for_status()
                sent += 1
            if sent == 0:
                logger.debug("[Telegram] sendMessage skipped: all messages had empty text (chat_id=%s)", chat_id)
    except Exception as e:
        logger.error("[Telegram] sendMessage error: %s", e)


async def send_awaiting_response_to_telegram(
    chat_id: str,
    response_text: str,
    task_id: Optional[str] = None,
    status: Optional[str] = None,
    awaiting_input: bool = True,
) -> None:
    """
    Push a response to Telegram from background processing (e.g. worker_loop).
    Handles awaiting-input (plan_approval, diff_ready) and final responses (completed, failed).
    Does not raise; logs errors.
    """
    # Jadzia session chat_id uses "telegram_{user_id}". Telegram Bot API requires numeric chat_id.
    numeric_id = chat_id.removeprefix("telegram_") if str(chat_id).startswith("telegram_") else chat_id
    logger.info("[Telegram push] sending to numeric_id=%s (original=%s)", numeric_id, chat_id)
    logger.debug(
        "[Telegram] send_awaiting_response_to_telegram called: chat_id=%r numeric_id=%r task_id=%r status=%r awaiting_input=%r response_len=%d",
        chat_id,
        numeric_id,
        task_id,
        status,
        awaiting_input,
        len(response_text or ""),
    )
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("[Telegram push] skipped: TELEGRAM_BOT_TOKEN not set")
        return
    if not chat_id:
        logger.warning("[Telegram push] skipped: chat_id empty")
        return
    if not str(chat_id).startswith("telegram_"):
        logger.warning("[Telegram push] skipped: chat_id does not start with telegram_ (chat_id=%r)", chat_id)
        return
    messages: List[dict] = format_response_for_telegram(response_text, awaiting_input=awaiting_input)
    if not messages:
        logger.warning("[Telegram push] skipped: format_response_for_telegram returned empty messages (chat_id=%r)", chat_id)
        return
    reply_markup = build_inline_keyboard_approval(task_id) if (status == "diff_ready" and task_id) else None
    logger.info(
        "[Telegram push] sending %d message(s) (chat_id=%r numeric_id=%r task_id=%r status=%r)",
        len(messages),
        chat_id,
        numeric_id,
        task_id,
        status,
    )
    url_base = f"{TELEGRAM_API_BASE}/bot{TELEGRAM_BOT_TOKEN}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            for i, msg in enumerate(messages):
                text = msg.get("text") if isinstance(msg, dict) else None
                if not text:
                    continue
                payload = {"chat_id": numeric_id, "text": text}
                if msg.get("parse_mode"):
                    payload["parse_mode"] = msg["parse_mode"]
                if reply_markup and i == 0:
                    payload["reply_markup"] = reply_markup
                log_payload = {**payload, "text": (text[:300] + "..." if len(text) > 300 else text)}
                logger.debug("[Telegram push] sendMessage request: %s", log_payload)
                r = await client.post(f"{url_base}/sendMessage", json=payload)
                if r.status_code >= 400:
                    try:
                        body = r.json()
                    except Exception:
                        body = r.text
                    logger.error(
                        "[Telegram push] sendMessage failed status=%s chat_id=%r numeric_id=%r task_id=%r body=%r",
                        r.status_code,
                        chat_id,
                        numeric_id,
                        task_id,
                        body,
                    )
                r.raise_for_status()
    except Exception as e:
        logger.error(
            "[Telegram push] sendMessage exception chat_id=%r numeric_id=%r task_id=%r status=%r",
            chat_id,
            numeric_id,
            task_id,
            status,
            exc_info=True,
        )


async def _handle_approval(
    chat_id: str, task_id: str, approved: bool, jwt_token: str, base_url: str,
) -> TelegramWebhookResponse:
    """Unified approval handler for both inline keyboard callbacks and text 'tak'/'nie'."""
    logger.info("[Telegram] approval: chat_id=%s task_id=%s approved=%s", chat_id, task_id, approved)
    result = await submit_input(task_id, jwt_token, base_url, approval=approved)
    response_text = result.get("response", "") or ("Zatwierdzono." if approved else "Odrzucono.")
    awaiting = result.get("awaiting_input", False)
    status = result.get("status", "")
    messages = format_response_for_telegram(response_text, awaiting_input=awaiting)
    reply_markup = build_inline_keyboard_approval(task_id) if (status == "diff_ready" and awaiting) else None
    return TelegramWebhookResponse(success=True, messages=messages, awaiting_input=awaiting, reply_markup=reply_markup)


async def _handle_webhook_request(
    request: TelegramWebhookRequest,
    x_webhook_secret: Optional[str],
    *,
    skip_webhook_secret: bool = False,
) -> TelegramWebhookResponse:
    """Process a single webhook request (n8n or normalized Telegram Update).
    When skip_webhook_secret=True (native Telegram Update), X-Webhook-Secret is not required
    because Telegram does not send that header."""
    start_time = time.time()

    try:
        if not skip_webhook_secret:
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
    logger.info("[Telegram] webhook command=%s chat_id=%s payload_len=%d", command, chat_id, len(payload))

    try:
        if command == "callback":
            parsed = parse_callback_approval(payload)
            if not parsed:
                msg = format_response_for_telegram("Nieprawidłowy callback.", awaiting_input=False)
                return TelegramWebhookResponse(success=True, messages=msg)
            task_id, approval = parsed
            # Verify task exists in DB
            from agent.db import db_get_task
            if not db_get_task(task_id):
                await asyncio.sleep(0.2)
                if not db_get_task(task_id):
                    logger.warning("[Telegram] approval: task not found task_id=%s chat_id=%s", task_id, chat_id)
                    messages = format_response_for_telegram(
                        "Nie widzę już tego zadania (wygasło lub zostało usunięte).\nWyślij `/zadanie ...` ponownie.",
                        awaiting_input=False,
                    )
                    return TelegramWebhookResponse(success=True, messages=messages)
            return await _handle_approval(chat_id, task_id, approval, jwt_token, base_url)

        if command == "approval":
            task_id = _get_task_id_for_chat(chat_id)
            if not task_id:
                await asyncio.sleep(0.2)
                task_id = _get_task_id_for_chat(chat_id)
            if not task_id:
                from agent.db import db_get_awaiting_approval_task
                awaiting_task = db_get_awaiting_approval_task(chat_id, "telegram")
                if awaiting_task:
                    task_id = awaiting_task["task_id"]
            if not task_id:
                logger.info("[Telegram] approval: no task found chat_id=%s", chat_id)
                messages = format_response_for_telegram("Brak aktywnego zadania do zatwierdzenia. Użyj /zadanie.", awaiting_input=False)
                return TelegramWebhookResponse(success=True, messages=messages)
            approval = payload == "true"
            return await _handle_approval(chat_id, task_id, approval, jwt_token, base_url)

        if command == "pomoc":
            text = get_help_message()
            messages = format_response_for_telegram(text, awaiting_input=False)
            # Ensure at least one sendable message (avoid empty/empty-text from MarkdownV2)
            if not messages or not any(m.get("text") for m in messages):
                messages = [{"text": "Pomoc: /zadanie, /status, /cofnij, /pomoc", "parse_mode": None}]
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
            task_id = _get_task_id_for_chat(chat_id)
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

        # Quick ACK: task is always enqueued; worker loop will process it and push results to Telegram
        pos = create_res.get("position_in_queue", 1)
        messages = format_response_for_telegram(
            f"Przyjęto zadanie (pozycja w kolejce: {pos}). Wyślę wynik, gdy będzie gotowy.",
            awaiting_input=False,
        )
        duration_ms = int((time.time() - start_time) * 1000)
        logger.info("[Telegram] quick_ack: task_id=%s position=%s %dms", task_id, pos, duration_ms)
        return TelegramWebhookResponse(success=True, messages=messages)

    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code if e.response is not None else 0
        logger.error("[Telegram] webhook HTTP error %s: %s", status_code, e)
        if status_code in (404, 409):
            # Task no longer exists in DB — clear stale mapping so user can retry
            logger.warning(
                "[Telegram] nie widzę tego zadania: HTTP %s chat_id=%s source=telegram (submit_input returned task_gone)",
                status_code, chat_id,
            )
            messages = format_response_for_telegram(
                "Nie widzę już tego zadania (wygasło lub zostało usunięte).\n"
                "Wyślij `/zadanie ...` ponownie.",
                awaiting_input=False,
            )
            return TelegramWebhookResponse(success=False, messages=messages, error={"type": "task_gone", "message": str(e)})
        if status_code in (502, 503, 504):
            # Transient server error — friendly message
            messages = format_response_for_telegram(
                "Serwer chwilowo niedostępny. Spróbuj ponownie za chwilę.",
                awaiting_input=False,
            )
            return TelegramWebhookResponse(success=False, messages=messages, error={"type": "transient", "status_code": status_code, "message": str(e)})
        # Other HTTP errors — generic internal error
        err_msg = format_error_for_telegram("internal", operation_id=chat_id)
        return TelegramWebhookResponse(
            success=False,
            messages=[{"text": err_msg, "parse_mode": "MarkdownV2"}],
            error={"type": "http_error", "status_code": status_code, "message": str(e)},
        )
    except (httpx.TimeoutException, httpx.ConnectError) as e:
        logger.warning("[Telegram] webhook transient error: %s: %s", type(e).__name__, e)
        messages = format_response_for_telegram(
            "Połączenie z serwerem nie powiodło się. Spróbuj ponownie za chwilę.",
            awaiting_input=False,
        )
        return TelegramWebhookResponse(
            success=False,
            messages=messages,
            error={"type": "transient", "message": str(e)},
        )
    except Exception as e:
        logger.error("[Telegram] webhook error: %s", e, exc_info=True)
        err_msg = format_error_for_telegram("internal", operation_id=chat_id)
        return TelegramWebhookResponse(
            success=False,
            messages=[{"text": err_msg, "parse_mode": "MarkdownV2"}],
            error={"type": "internal", "message": str(e)},
        )


@router.post("/webhook", response_model=TelegramWebhookResponse)
async def telegram_webhook(
    raw_request: Request,
    x_webhook_secret: Optional[str] = Header(None),
):
    """Main webhook: accepts Telegram native Update or n8n format; validate, route command, call Worker API; send replies via sendMessage when TELEGRAM_BOT_TOKEN set."""
    try:
        body = await raw_request.json()
    except Exception:
        return TelegramWebhookResponse(success=False, messages=[], error={"type": "bad_request", "message": "Invalid JSON"})
    if not isinstance(body, dict):
        return TelegramWebhookResponse(success=False, messages=[], error={"type": "bad_request", "message": "Body must be object"})

    if body.get("update_id") is not None:
        # Idempotency: skip duplicate Telegram updates (retries after timeout)
        update_id = body["update_id"]
        if isinstance(update_id, int) and _is_duplicate_update(update_id):
            logger.debug("[Telegram] dedup: skipping duplicate update_id=%s", update_id)
            return TelegramWebhookResponse(success=True, messages=[])
        normalized = normalize_telegram_update(body)
        if normalized is None:
            return TelegramWebhookResponse(success=True, messages=[])
        response = await _handle_webhook_request(
            normalized, x_webhook_secret, skip_webhook_secret=True
        )
        callback_id = (body.get("callback_query") or {}).get("id") if isinstance(body.get("callback_query"), dict) else None
        await _send_telegram_replies(normalized.chat_id, response, callback_id)
        return response

    try:
        request = TelegramWebhookRequest(**body)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    response = await _handle_webhook_request(request, x_webhook_secret, skip_webhook_secret=False)
    await _send_telegram_replies(request.chat_id, response, None)
    return response


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
