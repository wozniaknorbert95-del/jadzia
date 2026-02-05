"""
Węzły generowania zmian (czytanie plików, coder, diff, store).
Returns: (response_text, awaiting_input, input_type)
"""

import json
import re
from typing import Dict, Tuple, Optional

from ..state import (
    load_state,
    clear_state,
    update_operation_status,
    store_diffs,
    store_new_contents,
    add_error,
    set_awaiting_response,
    get_active_task_id,
    OperationStatus,
)
from ..log import log_event, EventType
from ..context import get_minimal_context
from ..prompt import get_coder_prompt
from ..helpers import clean_code_for_file
from ..diff import generate_diff, format_diff_for_display, create_change_summary
from ..tools.ssh_orchestrator import get_path_type, list_directory, read_file, SSHOrchestrator

MAX_FILE_SIZE = 10000


def truncate_file_content(content: str, max_size: int = MAX_FILE_SIZE) -> Tuple[str, bool]:
    """Skraca zawartość pliku jeśli jest za długa."""
    if len(content) <= max_size:
        return content, False

    chunk_size = max_size // 2 - 100

    start = content[:chunk_size]
    end = content[-chunk_size:]

    skipped = len(content) - (chunk_size * 2)
    skipped_lines = content[chunk_size:-chunk_size].count('\n')

    truncated = (
        f"{start}\n\n"
        f"[... POMINIĘTO {skipped} znaków ({skipped_lines} linii) ...]\n\n"
        f"{end}"
    )

    return truncated, True


def smart_truncate_for_task(content: str, task: str, file_path: str) -> str:
    """Inteligentne skracanie - próbuje znaleźć relevantny fragment."""
    if len(content) <= MAX_FILE_SIZE:
        return content

    task_lower = task.lower()

    # Szukaj funkcji
    if "function" in task_lower or "funkcj" in task_lower:
        func_match = re.search(r'funkcj[ęa]\s+(\w+)|function\s+(\w+)', task, re.IGNORECASE)
        if func_match:
            func_name = func_match.group(1) or func_match.group(2)
            func_pos = content.find(f"function {func_name}")
            if func_pos == -1:
                func_pos = content.find(f"def {func_name}")

            if func_pos != -1:
                start = max(0, func_pos - 500)
                end = min(len(content), func_pos + MAX_FILE_SIZE - 500)
                return content[start:end]

    # Szukaj CSS selectora
    if file_path.endswith('.css') or file_path.endswith('.scss'):
        selector_match = re.search(r'\.([\w-]+)|\#([\w-]+)', task)
        if selector_match:
            selector = selector_match.group(0)
            selector_pos = content.find(selector)
            if selector_pos != -1:
                start = max(0, selector_pos - 500)
                end = min(len(content), selector_pos + MAX_FILE_SIZE - 500)
                return content[start:end]

    # Fallback
    truncated, _ = truncate_file_content(content, MAX_FILE_SIZE)
    return truncated


async def _classify_task_complexity(user_input: str, plan: Dict) -> str:
    """Klasyfikuje zadanie jako 'simple' lub 'complex'."""
    simple_keywords = [
        "komentarz", "comment", "kolor", "color", "tekst", "text",
        "zmień", "change", "dodaj", "add", "usuń", "remove",
        "css", "style", "wygląd"
    ]
    complex_keywords = [
        "funkcj", "function", "hook", "action", "filter",
        "woocommerce", "payment", "płatność", "checkout",
        "logik", "logic", "walidacj", "validation"
    ]
    user_lower = user_input.lower()
    plan_str = json.dumps(plan).lower()
    files_count = len(plan.get("files_to_modify", []))
    if files_count > 2:
        return "complex"
    simple_score = sum(1 for kw in simple_keywords if kw in user_lower or kw in plan_str)
    complex_score = sum(1 for kw in complex_keywords if kw in user_lower or kw in plan_str)
    if complex_score > 0:
        return "complex"
    if simple_score > 0:
        return "simple"
    return "complex"


async def generate_changes(
    user_input: str,
    chat_id: str,
    source: str,
    plan: Dict,
    smart_context: Optional[Dict],
    call_claude,
    task_id: Optional[str] = None,
) -> Tuple[str, bool, Optional[str], Optional[str]]:
    """Generowanie zmian dla plików z planu. Returns (response, awaiting, input_type, next_task_id)."""
    from ..state import get_operation_id
    if task_id:
        print(f"[task_id={task_id}] generate_changes entry")
    operation_id = get_operation_id(chat_id, source, task_id=task_id) or "unknown"

    update_operation_status(OperationStatus.READING_FILES, chat_id, source, task_id=task_id)

    files_to_read = plan.get("files_to_read", []) + plan.get("files_to_modify", [])
    files_to_read = list(set(files_to_read))

    file_contents = {}
    errors = []

    for path in files_to_read:
        try:
            path_type = get_path_type(path)

            if path_type == "directory":
                success, files, error = list_directory(path)
                if success:
                    file_contents[path] = f"[KATALOG] Zawartość:\n" + "\n".join(files[:20])
                else:
                    errors.append(f"{path}: {error}")
            elif path_type == "file":
                content = read_file(path)
                file_contents[path] = content
            else:
                errors.append(f"{path}: nie istnieje")

        except Exception as e:
            errors.append(f"{path}: {e}")

    if errors and not file_contents:
        clear_state(chat_id, source)
        return (
            f"Nie udalo sie przeczytac plikow:\n" + "\n".join(errors),
            False, None, None
        )

    files_to_modify = [f for f in plan.get("files_to_modify", [])
                       if f in file_contents and not file_contents[f].startswith("[KATALOG]")]

    if not files_to_modify:
        clear_state(chat_id, source)
        result = "**Wyniki analizy:**\n\n"
        for path, content in file_contents.items():
            if content.startswith("[KATALOG]"):
                result += f"📁 **{path}**\n{content}\n\n"
            else:
                result += f"📄 **{path}** ({len(content)} znakow)\n"

        if errors:
            result += "\n**Bledy:**\n" + "\n".join(errors)

        return (result, False, None, None)

    task_complexity = await _classify_task_complexity(user_input, plan)

    new_contents = {}
    diffs = {}

    for path in files_to_modify:
        old_content_full = file_contents[path]

        old_content = smart_truncate_for_task(
            old_content_full,
            task=plan.get('understood_intent', user_input),
            file_path=path
        )

        if len(old_content) < len(old_content_full):
            print(f"[OPTYM] Skrócono plik {path}: "
                  f"{len(old_content_full)} → {len(old_content)} znaków "
                  f"(oszczędność: {len(old_content_full) - len(old_content)})")

        conventions = smart_context["conventions"] if smart_context else get_minimal_context()
        state_for_prompt = load_state(chat_id, source)
        tid_for_prompt = task_id or get_active_task_id(chat_id, source)
        task_for_prompt = None
        if state_for_prompt and tid_for_prompt and state_for_prompt.get("tasks"):
            task_for_prompt = state_for_prompt["tasks"].get(tid_for_prompt)
        elif state_for_prompt and not state_for_prompt.get("tasks"):
            task_for_prompt = state_for_prompt
        validation_errors = (task_for_prompt or {}).get("validation_errors") or {}
        extra_validation = ""
        if path in validation_errors:
            err_list = validation_errors.get(path) or []
            extra_validation = "\n\nPrevious attempt failed validation for this file. Please fix:\n" + "\n".join(f"  - {e}" for e in err_list)
        task_description = f"{plan.get('understood_intent', user_input)}\n\nKroki: {plan.get('steps', [])}{extra_validation}"
        coder_prompt = get_coder_prompt(
            file_path=path,
            current_content=old_content,
            task_description=task_description,
            conventions=conventions
        )

        new_content = await call_claude(
            [{"role": "user", "content": coder_prompt}],
            task_complexity=task_complexity
        )

        new_content_cleaned = clean_code_for_file(new_content, path)
        new_contents[path] = new_content_cleaned

        diff = generate_diff(old_content, new_content_cleaned, path)
        diffs[path] = diff

    store_diffs(diffs, chat_id, source, task_id=task_id)

    if not store_new_contents(new_contents, chat_id, source, task_id=task_id):
        add_error("Nie udalo sie zapisac nowych zawartosci do stanu!", chat_id, source, task_id=task_id)
        return (
            "Blad wewnetrzny: nie mozna zapisac zmian do stanu. Sprobuj ponownie.",
            False, None, None
        )

    update_operation_status(OperationStatus.DIFF_READY, chat_id, source, task_id=task_id)

    log_event(
        EventType.DIFF_GENERATED,
        f"Wygenerowano diffy dla {len(diffs)} plikow",
        operation_id=operation_id,
        task_id=task_id
    )

    # Quality assurance validation
    from ..nodes.quality import validate_changes
    diffs_for_quality = {path: {"new": new_contents[path]} for path in new_contents}
    ssh_orch = SSHOrchestrator()
    validation = await validate_changes(diffs_for_quality, ssh_orch)

    if not validation["valid"]:
        error_msg = "Walidacja kodu nie przeszla. Popraw ponizej bledy:\n\n"
        for filepath, errs in validation["errors"].items():
            error_msg += f"**{filepath}**:\n"
            for e in errs:
                error_msg += f"  - {e}\n"
            error_msg += "\n"
        if validation.get("warnings"):
            error_msg += "**Ostrzezenia:**\n"
            for filepath, warns in validation["warnings"].items():
                error_msg += f"{filepath}:\n"
                for w in warns:
                    error_msg += f"  - {w}\n"
        error_msg += "\nPonawiam generowanie z informacja o bledach (maks. 2 proby)."

        state = load_state(chat_id, source)
        tid = task_id or get_active_task_id(chat_id, source)
        task = None
        if state and tid and state.get("tasks"):
            task = state["tasks"].get(tid)
        elif state and not state.get("tasks"):
            task = state
        retry_count = (task or {}).get("retry_count", 0)

        if retry_count < 2:
            update_operation_status(
                OperationStatus.DIFF_READY,
                chat_id,
                source,
                task_id=task_id,
                validation_errors=validation["errors"],
                retry_count=retry_count + 1,
            )
            log_event(EventType.DIFF_GENERATED, f"[GENERATE] Validation failed for {task_id}, retrying ({retry_count + 1}/2)", task_id=task_id)
            return await generate_changes(
                user_input, chat_id, source, plan, smart_context, call_claude, task_id
            )
        else:
            log_event(EventType.DIFF_GENERATED, f"[GENERATE] Max validation retries exceeded for {task_id}", task_id=task_id)
            return (
                f"Nie udalo sie wygenerowac poprawnego kodu po {retry_count + 1} probach.\n\n"
                f"Ostatnie bledy walidacji:\n{error_msg}\n\n"
                f"Sprobuj inaczej sformulowac zadanie lub podziel je na mniejsze.",
                False,
                None,
                None,
            )

    # Validation passed: clear retry state
    update_operation_status(
        OperationStatus.DIFF_READY,
        chat_id,
        source,
        task_id=task_id,
        validation_errors={},
        retry_count=0,
    )
    if validation.get("warnings"):
        warning_count = sum(len(w) for w in validation["warnings"].values())
        log_event(EventType.DIFF_GENERATED, f"[GENERATE] Validation passed with {warning_count} warnings for {task_id}", task_id=task_id)
    else:
        log_event(EventType.DIFF_GENERATED, f"[GENERATE] Validation passed cleanly for {task_id}", task_id=task_id)

    summary = create_change_summary(diffs)

    diff_preview = ""
    for path, diff in diffs.items():
        diff_preview += f"\n\n--- {path} ---\n"
        diff_preview += format_diff_for_display(diff, max_lines=30)

    set_awaiting_response(True, "approval", chat_id, source, task_id=task_id)

    return (
        f"**PLAN:** {plan.get('understood_intent', 'Zmiany w plikach')}\n\n"
        f"{summary}\n"
        f"{diff_preview}\n\n"
        f"**Potwierdzasz zmiany? (Norbi?)**",
        True,
        "approval",
        None
    )
