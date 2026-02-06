"""
Węzły planowania (nowe zadanie, parse planu, żądania informacyjne).
Returns: (response_text, awaiting_input, input_type)
"""

import json
from typing import Dict, Tuple, Optional

from ..state import (
    load_state,
    save_state,
    clear_state,
    create_operation,
    update_operation_status,
    set_awaiting_response,
    OperationStatus,
    add_error,
)
from ..log import log_event, log_error, EventType
from ..context import classify_task_type, get_file_map, get_context_for_task
from ..prompt import get_planner_prompt, get_simple_response_prompt
from ..tools.ssh_orchestrator import list_files, list_directory
from .generate import generate_changes
from ..alerts import send_alert


def parse_plan(response: str) -> Dict:
    """Parsuje odpowiedź Claude z planem"""

    try:
        start = response.find('{')
        end = response.rfind('}') + 1

        if start != -1 and end > start:
            json_str = response[start:end]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    return {
        "understood_intent": response[:200] if response else "Nieznane",
        "files_to_read": [],
        "files_to_modify": [],
        "steps": [response[:500] if response else "Analiza"],
        "recommendations": [],
        "risks": []
    }


async def handle_info_request(user_input: str) -> Tuple[str, bool, Optional[str]]:
    """Obsługuje żądania informacyjne (listowanie plików itp.)"""

    lower_input = user_input.lower()

    path = ""

    path_indicators = ["w ", "z ", "folder ", "katalog ", "directory ", "path "]
    for indicator in path_indicators:
        if indicator in lower_input:
            idx = lower_input.find(indicator) + len(indicator)
            rest = user_input[idx:].strip()
            path = rest.split()[0] if rest else ""
            break

    if "child" in lower_input:
        path = "wp-content/themes/hello-theme-child-master"
    elif "theme" in lower_input or "motyw" in lower_input:
        path = "wp-content/themes"
    elif "plugin" in lower_input or "wtyczk" in lower_input:
        path = "wp-content/plugins"

    try:
        success, files, error = list_directory(path, recursive=False)

        if success:
            result = f"**Zawartosc katalogu: {path or '/'}**\n\n"
            result += "```\n"
            result += "\n".join(files[:50])
            if len(files) > 50:
                result += f"\n... i {len(files) - 50} wiecej"
            result += "\n```"
            return (result, False, None)
        else:
            return (f"Blad listowania: {error}", False, None)

    except Exception as e:
        return (f"Blad: {e}", False, None)


async def handle_new_task(
    user_input: str,
    chat_id: str,
    source: str,
    call_claude,
    task_id: Optional[str] = None,
    dry_run: bool = False,
    webhook_url: Optional[str] = None,
    test_mode: bool = False,
) -> Tuple[str, bool, Optional[str], Optional[str]]:
    """Planowanie nowego zadania. Returns (response, awaiting, input_type, next_task_id)."""
    if task_id:
        print(f"[task_id={task_id}] handle_new_task entry")

    info_keywords = ["wylistuj", "pokaz", "lista", "sprawdz", "ile", "jakie", "co jest", "ls", "dir"]
    is_info_request = any(kw in user_input.lower() for kw in info_keywords)

    if is_info_request:
        r = await handle_info_request(user_input)
        return (r[0], r[1], r[2], None)

    operation = create_operation(
        user_input,
        chat_id,
        source,
        task_id=task_id,
        dry_run=dry_run,
        test_mode=test_mode,
        webhook_url=webhook_url,
    )
    operation_id = operation["id"]
    tid = operation.get("task_id") or task_id

    log_event(
        EventType.OPERATION_START,
        f"Nowa operacja: {user_input[:100]}",
        operation_id=operation_id,
        task_id=tid
    )

    try:
        update_operation_status(OperationStatus.PLANNING, chat_id, source, task_id=tid)

        smart_context = None
        try:
            task_type = classify_task_type(user_input)
            file_map = get_file_map("")
            smart_context = get_context_for_task(task_type, file_map)
            planner_context_str = smart_context["planner_context"] or "Brak listy plikow"
            plan_prompt = get_planner_prompt(user_input, planner_context_str)
            plan_response = await call_claude(
                [{"role": "user", "content": plan_prompt}],
                system=smart_context["system_prompt"]
            )
        except Exception as e:
            log_error(f"Smart context fallback: {e}", task_id=tid)
            try:
                project_files = list_files("*.php") + list_files("*.css")
                project_structure = "\n".join(project_files[:50])
            except Exception:
                project_structure = "Nie mozna pobrac struktury plikow"
            plan_prompt = get_planner_prompt(user_input, project_structure)
            plan_response = await call_claude([{"role": "user", "content": plan_prompt}])

        plan = parse_plan(plan_response)

        update_operation_status(
            OperationStatus.PLANNING,
            chat_id, source,
            task_id=tid,
            plan=plan,
            files_to_modify=plan.get("files_to_modify", [])
        )

        log_event(
            EventType.PLAN_CREATED,
            f"Plan utworzony: {len(plan.get('files_to_modify', []))} plikow",
            data=plan,
            operation_id=operation_id,
            task_id=tid
        )

        # Recommendations: high = inform + ask approval; low = real question (A or B)
        recs_raw = plan.get("recommendations") or []
        # Backward compat: old "questions" as low-confidence recommendations
        if not recs_raw and plan.get("questions"):
            recs_raw = [
                {"decision": q, "reason": "", "confidence": "low", "options": []}
                for q in (plan.get("questions") or [])
            ]
        recs = [r for r in recs_raw if isinstance(r, dict)]
        high = [r for r in recs if (r.get("confidence") or "").lower() == "high"]
        low = [r for r in recs if (r.get("confidence") or "").lower() != "high"]

        if low:
            # Low-confidence: real question, user picks A or B
            parts = ["Nie jestem pewien w jednej kwestii:\n"]
            for r in low:
                opts = r.get("options") or []
                if len(opts) >= 2:
                    parts.append(f"- {r.get('decision', '')} Co wolisz: {opts[0]} czy {opts[1]}?")
                else:
                    parts.append(f"- {r.get('decision', '')} {r.get('reason', '')}")
            state = load_state(chat_id, source)
            if state:
                task_payload = (state.get("tasks") or {}).get(tid) if (tid and state.get("tasks")) else state
                (task_payload or state)["pending_plan_with_questions"] = plan
                save_state(state, chat_id, source)
            set_awaiting_response(True, "answer_questions", chat_id, source, task_id=tid)
            return (
                "\n".join(parts) + "\n\nProszę o odpowiedź.",
                True,
                "answer_questions",
                None
            )

        if high:
            # High-confidence: inform + ask approval (no quiz)
            parts = []
            for r in high:
                d, reason = r.get("decision", ""), (r.get("reason") or "").strip()
                if reason:
                    parts.append(f"Planuję: {d} — bo {reason}")
                else:
                    parts.append(f"Planuję: {d}")
            msg = "\n".join(parts) + "\n\nCzy zatwierdzasz?"
            state = load_state(chat_id, source)
            if state:
                task_payload = (state.get("tasks") or {}).get(tid) if (tid and state.get("tasks")) else state
                (task_payload or state)["pending_plan_with_questions"] = plan
                save_state(state, chat_id, source)
            set_awaiting_response(True, "plan_approval", chat_id, source, task_id=tid)
            return (msg, True, "plan_approval", None)

        if not plan.get("files_to_modify") and not plan.get("files_to_read"):
            clear_state(chat_id, source)
            simple_prompt = get_simple_response_prompt(user_input)
            response = await call_claude([{"role": "user", "content": simple_prompt}])
            return (response, False, None, None)

        return await generate_changes(user_input, chat_id, source, plan, smart_context, call_claude, task_id=tid)

    except Exception as e:
        add_error(str(e), chat_id, source, task_id=tid)
        update_operation_status(OperationStatus.FAILED, chat_id, source, task_id=tid)
        send_alert("task_failed", tid, str(e))
        raise
