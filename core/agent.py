"""Core agent orchestration — process_message and error handling.

Migrated from agent/agent.py (A3-01). Central entry point for all task processing.
"""

import asyncio
import logging
from typing import Optional, Tuple

from agent.state import (
    agent_lock,
    LockError,
    get_active_task_id,
    find_task_by_id,
    get_current_status,
)
from agent.log import log_error
from agent.nodes.routing import route_user_input
from agent.prompt import get_error_recovery_prompt
from core.llm import call_claude_with_retry, detect_session_source

logger = logging.getLogger(__name__)


async def process_message(
    user_input: str,
    chat_id: str,
    source: Optional[str] = None,
    task_id: Optional[str] = None,
    dry_run: bool = False,
    webhook_url: Optional[str] = None,
    test_mode: bool = False,
    push_to_telegram: bool = False,
    auto_advance: bool = True,
) -> Tuple[str, bool, Optional[str]]:
    if source is None:
        source = detect_session_source(chat_id)

    try:
        try:
            with agent_lock(timeout=5, chat_id=chat_id, source=source):
                _tid = task_id or get_active_task_id(chat_id, source)
                logger.debug("[process_message] task_id=%s acquired lock (auto_advance=%s)", _tid, auto_advance)
                result = await route_user_input(
                    user_input,
                    chat_id,
                    source,
                    call_claude_with_retry,
                    task_id=task_id,
                    dry_run=dry_run,
                    webhook_url=webhook_url,
                    test_mode=test_mode,
                )
                response, awaiting, input_type = result[0], result[1], result[2]
                next_task_id = result[3] if len(result) > 3 else None
                logger.debug("[process_message] result: awaiting=%s, input_type=%s, next_task_id=%r, push_to_telegram=%s, chat_id=%r", awaiting, input_type, next_task_id, push_to_telegram, chat_id)
                if next_task_id and auto_advance:
                    task_payload = find_task_by_id(chat_id, next_task_id, source)
                    next_input = (task_payload or {}).get("user_input", "")
                    if next_input:
                        logger.debug("[task_id=%s] task_completion_triggers_next auto-starting", next_task_id)
                        next_result = await route_user_input(
                            next_input,
                            chat_id,
                            source,
                            call_claude_with_retry,
                            task_id=next_task_id,
                        )
                        nr0, nr1, nr2 = next_result[0], next_result[1], next_result[2]
                        should_push_next = str(chat_id).startswith("telegram_") and push_to_telegram
                        logger.debug("[process_message] push_to_telegram check (next_result branch): nr1=%s, chat_id.startswith(telegram_)=%s, push_to_telegram=%s => send=%s", nr1, str(chat_id).startswith("telegram_"), push_to_telegram, should_push_next)
                        if should_push_next:
                            from api.telegram import send_awaiting_response_to_telegram
                            tid = get_active_task_id(chat_id, source) or next_task_id
                            status = get_current_status(chat_id, source, task_id=tid)
                            await send_awaiting_response_to_telegram(chat_id, nr0, task_id=tid, status=status, awaiting_input=nr1)
                        logger.debug("[process_message] task_id=%s releasing lock, awaiting=%s", next_task_id, nr1)
                        return (nr0, nr1, nr2)
                elif next_task_id and not auto_advance:
                    logger.debug("[process_message] next_task_id=%s available but auto_advance=False, worker loop will handle", next_task_id)
                should_push = str(chat_id).startswith("telegram_") and push_to_telegram
                logger.debug("[process_message] push_to_telegram check (main branch): awaiting=%s, chat_id.startswith(telegram_)=%s, push_to_telegram=%s => send=%s", awaiting, str(chat_id).startswith("telegram_"), push_to_telegram, should_push)
                if should_push:
                    from api.telegram import send_awaiting_response_to_telegram
                    tid = get_active_task_id(chat_id, source) or task_id
                    status = get_current_status(chat_id, source, task_id=tid)
                    await send_awaiting_response_to_telegram(chat_id, response, task_id=tid, status=status, awaiting_input=awaiting)
                logger.debug("[process_message] task_id=%s releasing lock, awaiting=%s", task_id, awaiting)
                return (response, awaiting, input_type)
        except LockError:
            return (
                "Agent jest zajety inna operacja. Poczekaj chwile i sprobuj ponownie.",
                False,
                None,
            )
    except Exception as e:
        logger.error("[MAIN ERROR] %s: %s", type(e).__name__, e, exc_info=True)
        log_error(str(e))
        from api.webhooks import notify_webhook, record_task_failure
        record_task_failure(str(e))
        tid = get_active_task_id(chat_id, source)
        if tid:
            task_payload = find_task_by_id(chat_id, tid, source)
            wh_url = (task_payload or {}).get("webhook_url")
            if wh_url:
                await notify_webhook(wh_url, tid, "failed", {"error": str(e)})
        error_result = await handle_error(e, chat_id, source)
        if str(chat_id).startswith("telegram_") and push_to_telegram:
            try:
                from api.telegram import send_awaiting_response_to_telegram
                _tid = tid or task_id
                await send_awaiting_response_to_telegram(
                    chat_id, error_result[0], task_id=_tid,
                    status="failed", awaiting_input=False,
                )
                logger.debug("[process_message] pushed error to Telegram for chat_id=%s task_id=%s", chat_id, _tid)
            except Exception as push_err:
                logger.debug("[process_message] failed to push error to Telegram: %s", push_err)
        return error_result


async def handle_error(
    error: Exception,
    chat_id: str,
    source: str,
) -> Tuple[str, bool, Optional[str]]:
    error_msg = str(error)

    try:
        operation_state = get_current_status(chat_id, source) or "brak operacji"
        recovery_prompt = get_error_recovery_prompt(
            error_message=error_msg,
            context=f"Chat: {chat_id}",
            operation_state=operation_state,
        )

        from core.llm import call_claude_with_retry
        response = await call_claude_with_retry([{"role": "user", "content": recovery_prompt}])
        return (response, False, None)

    except Exception:
        return (
            f"❌ Wystapil blad: {error_msg}\n\n"
            "Mozesz:\n"
            "- /rollback - cofnac zmiany\n"
            "- /clear - wyczysc stan\n"
            "- /status - sprawdz status",
            False, None,
        )


__all__ = [
    "process_message",
    "handle_error",
]
