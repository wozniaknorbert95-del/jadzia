"""
Routing użytkownika do odpowiedniego węzła.
Obsługuje: komendy, intent (approval/rejection), questions answered, user response, new task.
"""

import logging
from typing import Dict, Tuple, Optional

_log = logging.getLogger(__name__)

from ..state import (
    load_state,
    save_state,
    clear_state,
    get_stored_diffs,
    get_pending_plan,
    has_pending_operation,
    get_pending_operation_summary,
    get_active_task_id,
    OperationStatus,
    set_awaiting_response,
    is_test_mode,
)
from ..diff import create_change_summary
from .commands import (
    handle_status,
    handle_rollback,
    handle_help,
    handle_clear,
    handle_test,
    handle_scan_command,
)
from .approval import handle_approval
from .planning import handle_new_task
from .generate import generate_changes
from .intent import classify_intent
from ..prompt import get_approval_prompt


async def _handle_questions_answered(
    user_input: str,
    state: Dict,
    chat_id: str,
    source: str,
    call_claude,
    task_id: Optional[str] = None,
) -> Tuple[str, bool, Optional[str]]:
    """Obsługuje odpowiedź użytkownika na pytania od PLANNERA (low-confidence recommendations)."""
    task_payload = (state.get("tasks") or {}).get(task_id) if (task_id and state.get("tasks")) else state
    plan = (task_payload or state).get("pending_plan_with_questions") or (task_payload or state).get("plan")
    if not plan:
        clear_state(chat_id, source)
        return (
            "Przepraszam, straciłem kontekst. Możesz powtórzyć swoje zapytanie od początku?",
            False, None, None
        )
    original_intent = plan.get("understood_intent", "")
    plan["understood_intent"] = f"{original_intent}\n\nDodatkowe informacje od użytkownika: {user_input}"
    plan["recommendations"] = []
    plan["questions"] = []
    if task_payload:
        task_payload["pending_plan_with_questions"] = None
    else:
        state["pending_plan_with_questions"] = None
    save_state(state, chat_id, source)

    if not plan.get("files_to_modify") and not plan.get("files_to_read"):
        clear_state(chat_id, source)
        return (
            f"Rozumiem: {user_input}\n\nAle nie mam plików do modyfikacji w tym planie. "
            "Możesz sprecyzować, który plik chcesz zmienić?",
            False, None, None
        )
    original_user_input = (task_payload or state).get("user_input", "")
    combined_input = f"{original_user_input}\n\nDodatkowe informacje: {user_input}"
    return await generate_changes(combined_input, chat_id, source, plan, None, call_claude, task_id=task_id)


async def _handle_plan_approval(
    state: Dict,
    chat_id: str,
    source: str,
    call_claude,
    task_id: Optional[str] = None,
) -> Tuple[str, bool, Optional[str]]:
    """Po zatwierdzeniu planu (high-confidence recommendations) – uruchom generate_changes bez merge."""
    task_payload = (state.get("tasks") or {}).get(task_id) if (task_id and state.get("tasks")) else state
    plan = (task_payload or state).get("pending_plan_with_questions") or (task_payload or state).get("plan")
    if not plan:
        # Do NOT clear_state: it deletes the whole session and all tasks, causing 404 after process_message.
        # Return message only so the task stays in DB and client gets a valid response.
        return (
            "Przepraszam, straciłem kontekst. Możesz powtórzyć od początku?",
            False, None, None
        )
    if task_payload:
        task_payload["pending_plan_with_questions"] = None
    else:
        state["pending_plan_with_questions"] = None
    save_state(state, chat_id, source)
    original_user_input = (task_payload or state).get("user_input", "")
    return await generate_changes(original_user_input, chat_id, source, plan, None, call_claude, task_id=task_id)


async def _handle_user_response(
    user_input: str,
    state: Dict,
    chat_id: str,
    source: str,
    call_claude,
    task_id: Optional[str] = None,
) -> Tuple[str, bool, Optional[str]]:
    """Obsługuje odpowiedź użytkownika (approve/reject/question)."""
    task_payload = (state.get("tasks") or {}).get(task_id) if (task_id and state.get("tasks")) else state
    s = task_payload or state
    awaiting_type = s.get("awaiting_type", "")

    if awaiting_type == "answer_questions":
        return await _handle_questions_answered(user_input, state, chat_id, source, call_claude, task_id=task_id)

    if awaiting_type == "plan_approval":
        approval_prompt = get_approval_prompt(user_input)
        interpretation = await call_claude([{"role": "user", "content": approval_prompt}])
        interpretation = interpretation.strip().lower()
        if interpretation == "approve":
            return await _handle_plan_approval(state, chat_id, source, call_claude, task_id=task_id)
        if interpretation == "reject":
            if task_payload:
                task_payload["pending_plan_with_questions"] = None
            else:
                state["pending_plan_with_questions"] = None
            set_awaiting_response(False, None, chat_id, source, task_id=task_id)
            save_state(state, chat_id, source)
            return (
                "Anulowano. Opisz od nowa co chcesz zrobić.",
                False, None, None
            )
        set_awaiting_response(True, awaiting_type, chat_id, source, task_id=task_id)
        return (
            'Odpowiedz "tak" aby zatwierdzić plan lub "nie" aby anulować.',
            True, awaiting_type, None
        )

    approval_prompt = get_approval_prompt(user_input)
    interpretation = await call_claude([{"role": "user", "content": approval_prompt}])
    interpretation = interpretation.strip().lower()

    if interpretation == "approve":
        return await handle_approval(chat_id, source, state, True, task_id=task_id)

    elif interpretation == "reject":
        return await handle_approval(chat_id, source, state, False, task_id=task_id)

    elif interpretation == "question":
        set_awaiting_response(True, awaiting_type, chat_id, source, task_id=task_id)
        response = await call_claude([
            {"role": "user", "content": s.get("user_input", "")},
            {"role": "assistant", "content": "Przygotowalem zmiany..."},
            {"role": "user", "content": user_input}
        ])
        return (f"{response}\n\n**Potwierdzasz zmiany? (Norbi?)**", True, awaiting_type, None)

    else:
        set_awaiting_response(True, awaiting_type, chat_id, source, task_id=task_id)
        return (
            'Możesz odpowiedzieć "tak" aby zatwierdzić lub "nie" aby odrzucić, Norbi.',
            True,
            awaiting_type,
            None
        )


async def route_user_input(
    message: str,
    chat_id: str,
    source: str,
    call_claude,
    task_id: Optional[str] = None,
    dry_run: bool = False,
    webhook_url: Optional[str] = None,
    test_mode: Optional[bool] = None,
) -> Tuple[str, bool, Optional[str]]:
    """Routing użytkownika do odpowiedniego węzła. task_id=None uses active task."""
    task_id = task_id or get_active_task_id(chat_id, source)
    if task_id:
        _log.debug("[task_id=%s] route_user_input entry", task_id)

    lower_input = message.strip().lower()

    if lower_input in ["/status", "status"]:
        r = await handle_status(chat_id, source)
        return (r[0], r[1], r[2], None)

    if lower_input in ["/rollback", "rollback", "cofnij"]:
        r = await handle_rollback(chat_id, source)
        return (r[0], r[1], r[2], None)

    if lower_input in ["/clear", "clear", "anuluj"]:
        r = await handle_clear(chat_id, source)
        return (r[0], r[1], r[2], None)

    if lower_input in ["/help", "help", "pomoc"]:
        r = handle_help(chat_id, source)
        return (r[0], r[1], r[2], None)

    if lower_input in ["/test", "test"]:
        r = await handle_test()
        return (r[0], r[1], r[2], None)

    if lower_input in ["/skanuj", "skanuj", "scan"]:
        r = await handle_scan_command(chat_id, source)
        return (r[0], r[1], r[2], None)

    intent = await classify_intent(message, chat_id, source, call_claude, task_id=task_id)

    if intent == "APPROVAL":
        state = load_state(chat_id, source)
        if state and has_pending_operation(chat_id, source, task_id=task_id):
            # plan_approval must go to _handle_plan_approval (needs call_claude); handle_approval has no branch for it and would clear_state.
            task_payload = (state.get("tasks") or {}).get(task_id) if (task_id and state.get("tasks")) else state
            awaiting_type = (task_payload or state).get("awaiting_type", "")
            if awaiting_type == "plan_approval":
                return await _handle_plan_approval(state, chat_id, source, call_claude, task_id=task_id)
            return await handle_approval(chat_id, source, state, True, task_id=task_id)
        return ("Nie ma żadnego planu do zatwierdzenia. Co mam zrobić?", False, None, None)

    elif intent == "REJECTION":
        state = load_state(chat_id, source)
        if state and has_pending_operation(chat_id, source, task_id=task_id):
            return await handle_approval(chat_id, source, state, False, task_id=task_id)
        return ("Okej, nie ma problemu. Co chcesz teraz zrobić?", False, None, None)

    elif intent == "MODIFICATION":
        if get_pending_plan(chat_id, source, task_id=task_id):
            return ("Rozumiem, że chcesz zmienić plan. Opisz dokładnie co chcesz zmienić.", False, None, None)
        intent = "NEW_TASK"

    if intent == "UNCLEAR":
        return (
            "🤔 Hmm, nie jestem pewna co masz na myśli.\n\n"
            "Możesz:\n"
            "- Powiedzieć co chcesz zmienić w sklepie\n"
            "- Napisać 'pokaż pliki' żeby zobaczyć strukturę\n"
            "- Albo po prostu opisz problem",
            False,
            None,
            None
        )

    state = load_state(chat_id, source)
    if state and has_pending_operation(chat_id, source, task_id=task_id):
        # Resolve test_mode from state if not explicitly provided (per-task, immutable flag).
        if task_id and test_mode is None:
            try:
                test_mode = is_test_mode(chat_id, task_id, source)
            except Exception:
                test_mode = None

        # In test_mode, auto-approve pending operations without waiting for user HTTP input.
        if test_mode:
            from agent.log import log_event, EventType  # local import to avoid cycles

            task_payload = (state.get("tasks") or {}).get(task_id) if (task_id and state.get("tasks")) else state
            awaiting_type = (task_payload or state).get("awaiting_type")
            awaiting_response = (task_payload or state).get("awaiting_response", False)

            if awaiting_response and awaiting_type in {"approval", "deploy_approval", "plan_approval", "continue_operation", "answer_questions"}:
                log_event(
                    EventType.OPERATION_STEP,
                    f"[test_auto_approve] Auto-approval in test_mode awaiting_type={awaiting_type}",
                    task_id=task_id,
                    chat_id=chat_id,
                )

                # For questions, synthesize a neutral answer and reuse question handler.
                if awaiting_type == "answer_questions":
                    return await _handle_questions_answered(
                        "Brak dodatkowych pytań (auto-approval test_mode).",
                        state,
                        chat_id,
                        source,
                        call_claude,
                        task_id=task_id,
                    )

                # For approvals / deploy / continue, reuse approval handler with approved=True.
                return await handle_approval(chat_id, source, state, True, task_id=task_id)

        return await _handle_user_response(message, state, chat_id, source, call_claude, task_id=task_id)

    if has_pending_operation(chat_id, source, task_id=task_id):
        state = load_state(chat_id, source)
        if state:
            from ..state import get_current_status
            status = get_current_status(chat_id, source, task_id=task_id)
            if status == OperationStatus.DIFF_READY:
                diffs = get_stored_diffs(chat_id, source, task_id=task_id)
                if diffs:
                    summary = create_change_summary(diffs)
                    set_awaiting_response(True, "approval", chat_id, source, task_id=task_id)
                    return (
                        f"Masz oczekujące zmiany:\n\n{summary}\n\n**Czy mam to wdrożyć?**",
                        True,
                        "approval",
                        None
                    )
        summary = get_pending_operation_summary(chat_id, source, task_id=task_id)
        return (
            f"{summary}\n\nCzy chcesz kontynuować?",
            True,
            "continue_operation",
            None
        )

    return await handle_new_task(
        message,
        chat_id,
        source,
        call_claude,
        task_id=task_id,
        dry_run=dry_run,
        webhook_url=webhook_url,
        test_mode=test_mode or False,
    )
