"""Telegram webhook router (Transfer Protocol V4).

Uses Worker API (POST/GET /worker/task, POST /worker/task/{id}/input) with JWT.
Commands: /ticket, /commander, /status, /cofnij, /pomoc. Inline keyboard for approval (diff_ready).
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

from agent.telegram_formatter import format_response_for_telegram, format_error_for_telegram, get_help_message
from agent.telegram_validator import (
    TelegramWebhookRequest,
    normalize_telegram_update,
    validate_webhook_secret,
    validate_user_whitelist,
    get_jadzia_chat_id,
)
from api.telegram_client import (
    get_bot_jwt_token,
    get_base_url,
    get_public_base_url,
    create_task,
    get_task,
    submit_input,
    do_rollback,
)


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_API_BASE = "https://api.telegram.org"

router = APIRouter(prefix="/telegram", tags=["telegram"])
logger = logging.getLogger(__name__)

_DEDUP_TTL_SECONDS = 300
_processed_updates: dict[int, float] = {}


def _is_duplicate_update(update_id: int) -> bool:
    now = time.time()
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
    from agent.db import db_get_active_task, db_get_task
    try:
        task_id = db_get_active_task(chat_id, "telegram")
        if task_id and db_get_task(task_id) is not None:
            return task_id
        from agent.db import db_get_last_active_task
        last = db_get_last_active_task(chat_id, "telegram")
        return last["task_id"] if last else None
    except Exception as e:
        logger.warning("[Telegram] _get_task_id_for_chat failed: %s", e, extra={"chat_id": chat_id})
        return None


def parse_telegram_command(message: str, callback_data: Optional[str] = None) -> Tuple[str, str]:
    if callback_data:
        return "callback", callback_data
    msg = (message or "").strip()
    lower = msg.lower()
    cmd_token = msg.split(None, 1)[0] if msg else ""
    cmd_only = cmd_token.split("@")[0] if "@" in cmd_token else cmd_token
    cmd_lower = cmd_only.lower()
    if cmd_lower in ("/status", "status"):
        return "status", ""
    if cmd_lower in ("/cofnij", "cofnij"):
        return "cofnij", ""
    if cmd_lower in ("/pomoc", "pomoc", "/help", "help"):
        return "pomoc", ""
    if cmd_only.startswith("/ticket") or cmd_only.startswith("/zadanie"):
        payload = msg[len(cmd_token):].strip()
        return "ticket", payload
    if cmd_lower in ("/commander", "commander", "/jwt", "jwt"):
        return "commander", ""
    if cmd_lower in ("/mb_eval", "mb_eval"):
        return "mb_eval", ""
    if lower in ("tak", "nie", "t", "n", "yes", "no"):
        return "approval", "true" if lower in ("tak", "t", "yes") else "false"
    return "message", msg


def build_inline_keyboard_approval(task_id: str) -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": "Tak", "callback_data": f"{task_id}:approve:yes"},
                {"text": "Nie", "callback_data": f"{task_id}:approve:no"},
            ]
        ]
    }


def parse_callback_approval(callback_data: str) -> Optional[Tuple[str, bool]]:
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
                logger.debug("[Telegram] sendMessage request: chat_id=%s text_len=%d", chat_id, len(text))
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
    numeric_id = chat_id.removeprefix("telegram_") if str(chat_id).startswith("telegram_") else chat_id
    logger.info("[Telegram push] sending to numeric_id=%s (original=%s)", numeric_id, chat_id)
    logger.debug(
        "[Telegram] send_awaiting_response_to_telegram called: chat_id=%r numeric_id=%r task_id=%r status=%r awaiting_input=%r response_len=%d",
        chat_id, numeric_id, task_id, status, awaiting_input, len(response_text or ""),
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
        len(messages), chat_id, numeric_id, task_id, status,
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
                logger.debug("[Telegram push] sendMessage request: chat_id=%s text_len=%d", numeric_id, len(text))
                r = await client.post(f"{url_base}/sendMessage", json=payload)
                if r.status_code >= 400:
                    try:
                        body = r.json()
                    except Exception:
                        body = r.text
                    logger.error("[Telegram push] sendMessage failed status=%s chat_id=%r numeric_id=%r task_id=%r body=%r", r.status_code, chat_id, numeric_id, task_id, body)
                r.raise_for_status()
    except Exception as e:
        logger.error("[Telegram push] sendMessage exception chat_id=%r numeric_id=%r task_id=%r status=%r", chat_id, numeric_id, task_id, status, exc_info=True)


async def _handle_approval(
    chat_id: str, task_id: str, approved: bool, jwt_token: str, base_url: str,
) -> TelegramWebhookResponse:
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
            # MKT-BRAIN-PRO F1 — MB proposal HITL (shadow: no side-effects)
            from agent.marketing.telegram_proposals import handle_mb_hitl, parse_mb_callback

            mb_parsed = parse_mb_callback(payload)
            if mb_parsed:
                mb_action, mb_action_id = mb_parsed
                result = handle_mb_hitl(mb_action, mb_action_id)
                messages = format_response_for_telegram(
                    result.get("message") or "OK",
                    awaiting_input=False,
                )
                return TelegramWebhookResponse(success=bool(result.get("ok")), messages=messages)

            parsed = parse_callback_approval(payload)
            if not parsed:
                msg = format_response_for_telegram("Nieprawidłowy callback.", awaiting_input=False)
                return TelegramWebhookResponse(success=True, messages=msg)
            task_id, approval = parsed
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

        if command == "mb_eval":
            from agent.marketing.shadow_eval import compute_accuracy
            from agent.marketing.telegram_proposals import send_eval_pack_telegram

            push = send_eval_pack_telegram(limit=10, window_days=7)
            acc = push.get("accuracy_snapshot") or compute_accuracy(window_days=14)
            acc_s = acc.get("accuracy")
            acc_txt = f"{acc_s:.0%}" if isinstance(acc_s, float) else "n/a"
            gate = "gate OK" if acc.get("gate_ready") else acc.get("gate_reason")
            text = (
                f"{push.get('message') or 'Eval pack'}\n"
                f"14d accuracy={acc_txt} n={acc.get('n_scored')} ({gate})"
            )
            messages = format_response_for_telegram(text, awaiting_input=False)
            return TelegramWebhookResponse(success=bool(push.get("ok")), messages=messages)

        if command == "pomoc":
            text = get_help_message()
            messages = format_response_for_telegram(text, awaiting_input=False)
            if not messages or not any(m.get("text") for m in messages):
                messages = [{"text": "Pomoc: /zadanie, /status, /cofnij, /mb_eval, /pomoc", "parse_mode": None}]
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
                messages = format_response_for_telegram(
                    "Brak aktywnego zadania SSH. Użyj /ticket aby otworzyć ticket w Commander.",
                    awaiting_input=False,
                )
                return TelegramWebhookResponse(success=True, messages=messages)
            result = await get_task(task_id, jwt_token, base_url)
            response_text = result.get("response", "") or f"Status: {result.get('status', '?')}"
            awaiting = result.get("awaiting_input", False)
            messages = format_response_for_telegram(response_text, awaiting_input=awaiting)
            reply_markup = build_inline_keyboard_approval(task_id) if (result.get("status") == "diff_ready" and awaiting) else None
            return TelegramWebhookResponse(success=True, messages=messages, awaiting_input=awaiting, reply_markup=reply_markup)

        if command == "commander":
            from agent.commander.session_login import mint_login_link

            try:
                login = mint_login_link(
                    base_url=get_public_base_url(),
                    sub=str(request.user_id),
                    role="dowodca",
                )
            except Exception as exc:
                logger.error("[Telegram] /commander mint failed: %s", exc)
                messages = format_response_for_telegram(
                    "Nie udało się wygenerować logowania Commander. Sprawdź JWT_SECRET.",
                    awaiting_input=False,
                )
                return TelegramWebhookResponse(success=True, messages=messages)
            messages = format_response_for_telegram(
                "COI Commander — logowanie mobilne (jednorazowy link, 15 min):\n"
                f"{login['url']}\n"
                "Po otwarciu: Home → Ack leadów. Nie udostępniaj linku.",
                awaiting_input=False,
            )
            return TelegramWebhookResponse(success=True, messages=messages)

        if command == "ticket":
            description = payload if payload else request.message.strip()
            if not description or description.lower().startswith("/ticket"):
                messages = format_response_for_telegram(
                    "Podaj opis ticketu, np. /ticket naprawa nagłówka WP",
                    awaiting_input=False,
                )
                return TelegramWebhookResponse(success=True, messages=messages)

            from agent.commander.tickets import create_ticket_from_telegram

            ticket_res = create_ticket_from_telegram(description, get_public_base_url())
            if ticket_res.get("status") != "ok":
                messages = format_response_for_telegram(
                    "Nie udało się utworzyć ticketu. Spróbuj ponownie.",
                    awaiting_input=False,
                )
                return TelegramWebhookResponse(success=True, messages=messages)

            link = ticket_res["deeplink"]["url"]
            messages = format_response_for_telegram(
                f"Ticket #{ticket_res['ticket_id']} utworzony.\n"
                f"Otwórz w Commander (ważny 15 min):\n{link}\n"
                f"Wykonanie tylko w dashboardzie — bez SSH z Telegram.",
                awaiting_input=False,
            )
            return TelegramWebhookResponse(success=True, messages=messages)

        instruction = payload if payload else request.message.strip()
        if not instruction:
            messages = format_response_for_telegram(
                "Użyj /ticket <opis> aby utworzyć ticket w Commander (bez SSH z Telegram).",
                awaiting_input=False,
            )
            return TelegramWebhookResponse(success=True, messages=messages)

        # Legacy free-text: redirect to ticket flow (CE-02)
        from agent.commander.tickets import create_ticket_from_telegram

        ticket_res = create_ticket_from_telegram(instruction, get_public_base_url())
        if ticket_res.get("status") == "ok":
            link = ticket_res["deeplink"]["url"]
            messages = format_response_for_telegram(
                f"Ticket #{ticket_res['ticket_id']} — otwórz Commander:\n{link}",
                awaiting_input=False,
            )
            return TelegramWebhookResponse(success=True, messages=messages)

        messages = format_response_for_telegram(
            "Nie udało się utworzyć ticketu. Użyj /ticket <opis>.",
            awaiting_input=False,
        )
        return TelegramWebhookResponse(success=True, messages=messages)

    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code if e.response is not None else 0
        logger.error("[Telegram] webhook HTTP error %s: %s", status_code, e)
        if status_code in (404, 409):
            logger.warning("[Telegram] nie widzę tego zadania: HTTP %s chat_id=%s source=telegram", status_code, chat_id)
            messages = format_response_for_telegram(
                "Nie widzę już tego zadania (wygasło lub zostało usunięte).\nWyślij `/zadanie ...` ponownie.",
                awaiting_input=False,
            )
            return TelegramWebhookResponse(success=False, messages=messages, error={"type": "task_gone", "message": str(e)})
        if status_code in (502, 503, 504):
            messages = format_response_for_telegram("Serwer chwilowo niedostępny. Spróbuj ponownie za chwilę.", awaiting_input=False)
            return TelegramWebhookResponse(success=False, messages=messages, error={"type": "transient", "status_code": status_code, "message": str(e)})
        err_msg = format_error_for_telegram("internal", operation_id=chat_id)
        return TelegramWebhookResponse(
            success=False,
            messages=[{"text": err_msg, "parse_mode": "MarkdownV2"}],
            error={"type": "http_error", "status_code": status_code, "message": str(e)},
        )
    except (httpx.TimeoutException, httpx.ConnectError) as e:
        logger.warning("[Telegram] webhook transient error: %s: %s", type(e).__name__, e)
        messages = format_response_for_telegram("Połączenie z serwerem nie powiodło się. Spróbuj ponownie za chwilę.", awaiting_input=False)
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
    try:
        body = await raw_request.json()
    except Exception:
        return TelegramWebhookResponse(success=False, messages=[], error={"type": "bad_request", "message": "Invalid JSON"})
    if not isinstance(body, dict):
        return TelegramWebhookResponse(success=False, messages=[], error={"type": "bad_request", "message": "Body must be object"})

    if body.get("update_id") is not None:
        update_id = body["update_id"]
        if isinstance(update_id, int) and _is_duplicate_update(update_id):
            logger.debug("[Telegram] dedup: skipping duplicate update_id=%s", update_id)
            return TelegramWebhookResponse(success=True, messages=[])
        normalized = normalize_telegram_update(body)
        if normalized is None:
            return TelegramWebhookResponse(success=True, messages=[])
        response = await _handle_webhook_request(normalized, x_webhook_secret, skip_webhook_secret=True)
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
    from agent.telegram_formatter import format_response_for_telegram, escape_markdown_v2
    test_response = f"**Test**\n\nMessage: {escape_markdown_v2(message)}\nUser: `{user_id}`"
    messages = format_response_for_telegram(test_response.strip(), awaiting_input=False)
    return {"success": True, "messages": messages, "note": "Use /telegram/webhook for production."}


_telegram_chat_to_task_id = _get_task_id_for_chat


__all__ = [
    "router",
    "send_awaiting_response_to_telegram",
    "TelegramWebhookResponse",
    "_is_duplicate_update",
    "_processed_updates",
    "_DEDUP_TTL_SECONDS",
    "_get_task_id_for_chat",
    "_send_telegram_replies",
    "parse_telegram_command",
    "build_inline_keyboard_approval",
    "parse_callback_approval",
    "_handle_approval",
    "_handle_webhook_request",
    "telegram_webhook",
    "telegram_health",
    "telegram_test",
]
