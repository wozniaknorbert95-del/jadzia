"""
Węzły obsługi zatwierdzeń (tak/nie, wykonanie zmian, deploy).
Returns: (response_text, awaiting_input, input_type, next_task_id)
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Tuple, Optional

_log = logging.getLogger(__name__)

from ..state import (
    clear_state,
    update_operation_status,
    set_awaiting_response,
    get_stored_contents,
    get_stored_diffs,
    get_active_task_id,
    mark_task_completed,
    OperationStatus,
    add_error,
)
from ..log import log_event, EventType
from ..tools.ssh_orchestrator import write_file
from ..tools import deploy
from ..diff import create_change_summary
from ..alerts import send_alert


# Internal marker used only for automated Scenario 3 (rollback verification) in test_mode.
SCENARIO3_FORCE_ROLLBACK_TOKEN = "[SCENARIO3_FORCE_ROLLBACK]"


def _task_from_state(state: Dict, task_id: Optional[str]) -> Dict:
    """Resolve task payload from full state."""
    if task_id and state.get("tasks"):
        return (state.get("tasks") or {}).get(task_id) or state
    return state


async def handle_approval(
    chat_id: str,
    source: str,
    state: Dict,
    approved: bool,
    task_id: Optional[str] = None,
) -> Tuple[str, bool, Optional[str], Optional[str]]:
    """Obsługa zatwierdzenia (tak/nie). Returns (response, awaiting, input_type, next_task_id)."""
    task = _task_from_state(state, task_id)
    awaiting_type = task.get("awaiting_type", "")
    operation_id = task.get("id")
    if task_id:
        _log.debug("[task_id=%s] handle_approval entry approved=%s", task_id, approved)

    if not approved:
        clear_state(chat_id, source)
        log_event(EventType.USER_REJECTED, "Uzytkownik odrzucil zmiany", operation_id=operation_id, task_id=task_id, chat_id=chat_id)
        return ("Zmiany odrzucone. Operacja anulowana.", False, None, None)

    if awaiting_type == "approval":
        return await execute_changes(chat_id, source, state, task_id=task_id)

    elif awaiting_type == "deploy_approval":
        return await _execute_deploy(chat_id, source, state, task_id=task_id)

    elif awaiting_type == "continue_operation":
        return await _resume_operation(chat_id, source, state, task_id=task_id)

    else:
        if get_stored_contents(chat_id, source, task_id=task_id):
            return await execute_changes(chat_id, source, state, task_id=task_id)
        clear_state(chat_id, source)
        return ("Brak zmian do wykonania.", False, None, None)


async def execute_changes(
    chat_id: str,
    source: str,
    state: Dict,
    task_id: Optional[str] = None,
) -> Tuple[str, bool, Optional[str], Optional[str]]:
    """Wykonanie zatwierdzonych zmian (zapis + deploy) lub podgląd przy dry_run."""
    task_id = task_id or get_active_task_id(chat_id, source)
    task = _task_from_state(state, task_id)
    operation_id = task.get("id")
    # Per-task test flag (set only at creation); missing => False for legacy/production tasks.
    task_test_mode = bool(task.get("test_mode", False))
    user_input_val = task.get("user_input")
    user_input = user_input_val if isinstance(user_input_val, str) else ""
    scenario3_force_rollback = task_test_mode and (SCENARIO3_FORCE_ROLLBACK_TOKEN in user_input)

    if task.get("dry_run", False):
        log_event(
            EventType.USER_APPROVED,
            f"[DRY-RUN] Skipping file writes for task {task_id}",
            operation_id=operation_id,
            task_id=task_id,
            chat_id=chat_id,
        )
        diffs = get_stored_diffs(chat_id, source, task_id=task_id)
        file_list = list(diffs.keys()) if diffs else []
        next_task_id = mark_task_completed(chat_id, task_id, source)
        webhook_url = task.get("webhook_url")
        if webhook_url:
            from interfaces.webhooks import notify_webhook
            result = {
                "dry_run": True,
                "files_modified": file_list,
                "operation_id": task.get("id"),
            }
            await notify_webhook(webhook_url, task_id, "completed", result)
        msg = (
            "✅ DRY-RUN COMPLETE\n\n"
            f"Preview: {len(file_list)} files would be modified:\n"
            + "\n".join(f"- {path}" for path in file_list)
            + "\n\n(No files were actually written)"
        )
        return (msg, False, None, next_task_id)

    new_contents = get_stored_contents(chat_id, source, task_id=task_id)

    if not new_contents:
        clear_state(chat_id, source)
        return ("Brak zmian do zapisania.", False, None, None)

    log_event(EventType.USER_APPROVED, "Uzytkownik zatwierdzil zmiany", operation_id=operation_id, task_id=task_id, chat_id=chat_id)

    update_operation_status(OperationStatus.WRITING_FILES, chat_id, source, task_id=task_id)

    written = []
    errors = []

    for path, content in new_contents.items():
        try:
            write_file(path, content, operation_id, chat_id, source, task_id=task_id)
            written.append(path)
        except Exception as e:
            errors.append(f"{path}: {e}")
            add_error(f"Blad zapisu {path}: {e}", chat_id, source, task_id=task_id)

    if errors and not written:
        update_operation_status(OperationStatus.FAILED, chat_id, source, task_id=task_id)
        send_alert("task_failed", task_id, "\n".join(errors))
        # Do NOT clear_state: keep task in DB with status=failed so client can GET /worker/task/{id} and see error
        return (f"Blad zapisu plikow:\n" + "\n".join(errors), False, None, None)

    update_operation_status(OperationStatus.COMPLETED, chat_id, source, task_id=task_id, files_written=written)

    # Self-healing verification (only when not dry_run)
    if not task.get("dry_run", True):
        from agent.tools.rest import health_check_wordpress
        from interfaces.webhooks import record_deployment_verification

        log_event(
            EventType.FILE_WRITE,
            f"[VERIFICATION] Starting deployment health check for {task_id}",
            operation_id=operation_id,
            task_id=task_id,
            chat_id=chat_id,
        )

        # Scenario 3 (test_mode only): force synthetic failure to drive auto-rollback deterministically,
        # without performing a real HTTP health check against production.
        if scenario3_force_rollback:
            health = {
                "healthy": False,
                "status_code": 599,
                "response_time": 0.0,
                "error": "Scenario3 forced failure (test_mode)",
            }
        else:
            await asyncio.sleep(2)
            health = await health_check_wordpress("https://zzpackage.flexgrafik.nl", timeout=15)

        timestamp_iso = datetime.now(timezone.utc).isoformat()
        if not health["healthy"]:
            record_deployment_verification(timestamp_iso, healthy=False, auto_rollback_triggered=True)
            log_event(
                EventType.FILE_WRITE,
                f"[VERIFICATION] FAILED for {task_id}: {health.get('error', 'unknown')}",
                operation_id=operation_id,
                task_id=task_id,
                chat_id=chat_id,
            )
            if not task.get("test_mode"):
                send_alert(
                    "health_check_failed",
                    task_id,
                    health.get("error") or health.get("msg") or "unknown",
                )
            # Extra marker for automated Scenario 3 rollback verification (visible only in test_mode path).
            if scenario3_force_rollback:
                log_event(
                    EventType.FILE_WRITE,
                    f"[SCENARIO3] AUTO-ROLLBACK VERIFICATION for {task_id}",
                    operation_id=operation_id,
                    task_id=task_id,
                    chat_id=chat_id,
                )
            from agent.nodes.commands import handle_rollback

            rollback_result = await handle_rollback(chat_id, source)
            rollback_msg = rollback_result[0]

            webhook_url = task.get("webhook_url")
            if webhook_url:
                from interfaces.webhooks import notify_webhook

                webhook_payload = {
                    "task_id": task_id,
                    "status": "auto_healed",
                    "timestamp": timestamp_iso,
                    "health_check": health,
                    "rollback_result": rollback_msg,
                }
                await notify_webhook(webhook_url, task_id, "auto_healed", webhook_payload)

            next_task_id = mark_task_completed(chat_id, task_id, source)
            return (
                (
                    f"⚠️ **DEPLOYMENT FAILED - AUTO-ROLLBACK EXECUTED**\n\n"
                    f"**Health Check:**\n"
                    f"- Status: {health.get('status_code', 'N/A')}\n"
                    f"- Error: {health.get('error', 'N/A')}\n\n"
                    f"**Rollback Result:**\n{rollback_msg}\n\n"
                    f"Files have been restored to previous working state."
                ),
                False,
                None,
                next_task_id,
            )
        else:
            record_deployment_verification(timestamp_iso, healthy=True, auto_rollback_triggered=False)
            log_event(
                EventType.FILE_WRITE,
                f"[VERIFICATION] SUCCESS for {task_id} (HTTP {health.get('status_code', 'N/A')}, {health.get('response_time', 0):.2f}s)",
                operation_id=operation_id,
                task_id=task_id,
                chat_id=chat_id,
            )

    set_awaiting_response(True, "deploy_approval", chat_id, source, task_id=task_id)

    msg = f"✅ Zapisano {len(written)} plików:\n"
    msg += "\n".join(f"- {f}" for f in written)
    if errors:
        msg += f"\n\n⚠️ Błędy:\n" + "\n".join(errors)
    msg += "\n\nSprawdź proszę w przeglądarce, czy strona działa. Gdy potwierdzisz, napisz **Tak** (zadanie zostanie zamknięte)."

    return (msg, True, "deploy_approval", None)


async def _execute_deploy(
    chat_id: str,
    source: str,
    state: Dict,
    task_id: Optional[str] = None,
) -> Tuple[str, bool, Optional[str], Optional[str]]:
    """Po potwierdzeniu użytkownika: opcjonalny health check, zamknięcie zadania. Nie rzuca – przy błędzie zwraca komunikat i stara się zamknąć task."""
    import traceback
    task = _task_from_state(state, task_id)
    operation_id = task.get("id")
    next_task_id = None
    try:
        update_operation_status(OperationStatus.COMPLETED, chat_id, source, task_id=task_id)

        result = deploy(operation_id)

        update_operation_status(OperationStatus.COMPLETED, chat_id, source, task_id=task_id, deploy_result=result)

        if task_id:
            next_task_id = mark_task_completed(chat_id, task_id, source)
        else:
            clear_state(chat_id, source)

        webhook_url = task.get("webhook_url")
        if webhook_url:
            from interfaces.webhooks import notify_webhook
            diffs = get_stored_diffs(chat_id, source, task_id=task_id)
            wh_result = {
                "dry_run": False,
                "files_modified": list(diffs.keys()) if diffs else [],
                "operation_id": task.get("id"),
                "deploy_result": result,
            }
            await notify_webhook(webhook_url, task_id, "completed", wh_result)

        log_event(EventType.OPERATION_END, "Operacja zakonczona", operation_id=operation_id, task_id=task_id, chat_id=chat_id)

        if result.get("status") == "ok":
            return (f"✅ Zadanie zakończone.\n{result.get('msg', '')}", False, None, next_task_id)
        return (
            f"✅ Zadanie zakończone.\n⚠️ {result.get('msg', '')}\n\nUżyj /cofnij, jeśli coś nie działa.",
            False, None, next_task_id
        )
    except Exception as e:
        log_event(EventType.DEPLOY_FAILED, f"_execute_deploy error: {e}", operation_id=None, task_id=task_id, chat_id=chat_id)
        traceback.print_exc()
        try:
            if task_id:
                next_task_id = mark_task_completed(chat_id, task_id, source)
        except Exception:
            pass
        return (
            "Zadanie zamknięte. Po stronie weryfikacji wystąpił błąd – sprawdź proszę stronę ręcznie. Jeśli coś nie działa, użyj /cofnij.",
            False, None, next_task_id
        )


async def _resume_operation(
    chat_id: str,
    source: str,
    state: Dict,
    task_id: Optional[str] = None,
) -> Tuple[str, bool, Optional[str], Optional[str]]:
    """Wznawia przerwana operację."""
    task = _task_from_state(state, task_id)
    status = task.get("status")

    if status == OperationStatus.DIFF_READY:
        diffs = get_stored_diffs(chat_id, source, task_id=task_id)
        if diffs:
            summary = create_change_summary(diffs)
            set_awaiting_response(True, "approval", chat_id, source, task_id=task_id)
            return (f"Kontynuuje...\n\n{summary}\n\n**Potwierdzasz? (Norbi?)**", True, "approval", None)

    if status == OperationStatus.COMPLETED:
        set_awaiting_response(True, "deploy_approval", chat_id, source, task_id=task_id)
        return ("Pliki zapisane. Sprawdź w przeglądarce, czy strona działa. Gdy potwierdzisz, napisz **Tak**.", True, "deploy_approval", None)

    clear_state(chat_id, source)
    return ("Nie mozna wznowic operacji. Zaczynam od nowa.", False, None, None)
