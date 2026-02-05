"""
agent.py — Główna logika agenta JADZIA

NAPRAWIONE:
- Obsługa stanu (state deadlock)
- Obsługa komend informacyjnych (listowanie plików)
- Poprawna interpretacja odpowiedzi użytkownika
"""

import os
import json
import asyncio
from typing import Optional, Tuple, Dict, List
from dotenv import load_dotenv

load_dotenv()

from .prompt import (
    get_system_prompt,
    get_planner_prompt,
    get_coder_prompt,
    get_approval_prompt,
    get_error_recovery_prompt,
    get_simple_response_prompt
)
from .tools import (
    list_files, read_file, write_file,
    deploy, health_check, rollback,
    test_ssh_connection,
    list_directory, exec_ssh_command, get_path_type
)
from .diff import generate_diff, format_diff_for_display, create_change_summary
from .guardrails import validate_operation, OperationType
from .state import (
    agent_lock, LockError,
    load_state, save_state, clear_state,
    create_operation, update_operation_status,
    has_pending_operation, get_pending_operation_summary,
    OperationStatus, set_awaiting_response,
    store_diffs, get_stored_diffs,
    store_new_contents, get_stored_contents,
    get_operation_id, add_error
)
from .log import log_event, log_error, EventType
from .context import get_minimal_context
from .helpers import clean_code_for_file  # NAPRAWKA #3

# ============================================================
# KONFIGURACJA
# ============================================================

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096
TIMEOUT = 120

# OPTYMALIZACJA POZIOM 1
MAX_FILE_SIZE = 10000  # Max znakow pliku do wyslania
ENABLE_PROMPT_CACHING = True  # Prompt caching (90% taniej)
TOKEN_STATS = {"input": 0, "output": 0, "cached": 0, "cost": 0.0}  # Monitoring


# ============================================================
# CLAUDE API CLIENT
# ============================================================

def get_claude_client():
    """Tworzy klienta Anthropic"""
    if not ANTHROPIC_API_KEY:
        raise ValueError("Brak ANTHROPIC_API_KEY w .env")
    
    from anthropic import Anthropic
    return Anthropic(api_key=ANTHROPIC_API_KEY)


# ============================================================
# NOWA FUNKCJA call_claude Z OPTYMALIZACJAMI
# Zastąp starą funkcję (linie 70-100) tą wersją
# ============================================================

async def call_claude(
    messages: List[Dict],
    system: Optional[str] = None,
    timeout: int = TIMEOUT,
    use_caching: bool = True
) -> str:
    """
    Wywołuje Claude API z optymalizacjami POZIOM 1.
    
    OPTYMALIZACJE:
    - Prompt caching dla system promptu (90% taniej dla powtórzeń)
    - Monitoring tokenów i kosztów
    """
    try:
        client = get_claude_client()
        loop = asyncio.get_event_loop()
        
        def _call():
            # Przygotuj system prompt z cachingiem
            system_content = system or get_system_prompt()
            
            if ENABLE_PROMPT_CACHING and use_caching:
                # Format z prompt caching (linia 85 dokumentacji Anthropic)
                system_param = [{
                    "type": "text",
                    "text": system_content,
                    "cache_control": {"type": "ephemeral"}  # CACHE!
                }]
            else:
                # Zwykły format
                system_param = system_content
            
            # Wywołanie API
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=system_param,
                messages=messages
            )
            
            # MONITORING: Zlicz tokeny i koszt
            usage = response.usage
            TOKEN_STATS["input"] += usage.input_tokens
            TOKEN_STATS["output"] += usage.output_tokens
            
            # Zlicz cached tokeny (jeśli są)
            if hasattr(usage, 'cache_read_input_tokens'):
                TOKEN_STATS["cached"] += usage.cache_read_input_tokens
            
            # Oblicz koszt (Sonnet 4: $3/M input, $15/M output, $0.30/M cached)
            input_cost = (usage.input_tokens / 1_000_000) * 3.0
            output_cost = (usage.output_tokens / 1_000_000) * 15.0
            cached_cost = 0
            if hasattr(usage, 'cache_read_input_tokens'):
                cached_cost = (usage.cache_read_input_tokens / 1_000_000) * 0.30
            
            call_cost = input_cost + output_cost + cached_cost
            TOKEN_STATS["cost"] += call_cost
            
            # DEBUG log
            print(f"[COST] Wywołanie: ${call_cost:.4f} | "
                  f"Input: {usage.input_tokens} | "
                  f"Output: {usage.output_tokens} | "
                  f"Cached: {getattr(usage, 'cache_read_input_tokens', 0)}")
            
            return response.content[0].text
        
        result = await asyncio.wait_for(
            loop.run_in_executor(None, _call),
            timeout=timeout
        )
        
        return result
    
    except asyncio.TimeoutError:
        raise RuntimeError(f"Claude nie odpowiedzial w ciagu {timeout} sekund")
    except Exception as e:
        raise RuntimeError(f"Blad Claude API: {e}")


def get_cost_stats() -> dict:
    """Zwraca statystyki użycia i kosztów."""
    return {
        "total_input_tokens": TOKEN_STATS["input"],
        "total_output_tokens": TOKEN_STATS["output"],
        "total_cached_tokens": TOKEN_STATS["cached"],
        "total_cost_usd": round(TOKEN_STATS["cost"], 4),
        "estimated_savings_from_cache": round(
            (TOKEN_STATS["cached"] / 1_000_000) * (3.0 - 0.30), 4
        ) if TOKEN_STATS["cached"] > 0 else 0
    }


def reset_cost_stats():
    """Resetuje statystyki (np. na początku dnia)."""
    TOKEN_STATS["input"] = 0
    TOKEN_STATS["output"] = 0
    TOKEN_STATS["cached"] = 0
    TOKEN_STATS["cost"] = 0.0


# ============================================================
# GŁÓWNA FUNKCJA PROCESS_MESSAGE
# ============================================================

async def process_message(
    user_input: str,
    chat_id: str
) -> Tuple[str, bool, Optional[str]]:
    """Główna funkcja przetwarzająca wiadomość użytkownika."""
    
    try:
        try:
            with agent_lock(timeout=5):
                return await _process_message_internal(user_input, chat_id)
        except LockError:
            return (
                "Agent jest zajety inna operacja. Poczekaj chwile i sprobuj ponownie.",
                False,
                None
            )
    
    except Exception as e:
        log_error(str(e))
        return await handle_error(e, chat_id)


async def _process_message_internal(
    user_input: str,
    chat_id: str
) -> Tuple[str, bool, Optional[str]]:
    """Wewnętrzna logika przetwarzania"""
    
    lower_input = user_input.strip().lower()
    
    # Sprawdź specjalne komendy
    if lower_input in ["/status", "status"]:
        return await handle_status_command()
    
    if lower_input in ["/rollback", "rollback", "cofnij"]:
        return await handle_rollback_command()
    
    if lower_input in ["/clear", "clear", "anuluj"]:
        return await handle_clear_command()
    
    if lower_input in ["/help", "help", "pomoc"]:
        return handle_help_command()
    
    if lower_input in ["/test", "test"]:
        return await handle_test_command()
    
    # Sprawdź czy to odpowiedź T/N
    if lower_input in ["t", "tak", "yes", "y", "ok", "dawaj", "+", "potwierdz"]:
        state = load_state()
        if state and state.get("awaiting_response"):
            return await handle_approval(state, True)
        else:
            return ("Nie ma zadnej operacji do potwierdzenia.", False, None)
    
    if lower_input in ["n", "nie", "no", "stop", "anuluj", "-", "cancel"]:
        state = load_state()
        if state and state.get("awaiting_response"):
            return await handle_approval(state, False)
        else:
            return ("Nie ma zadnej operacji do anulowania.", False, None)
    
    # Sprawdź czy czekamy na odpowiedź
    state = load_state()
    if state and state.get("awaiting_response"):
        return await handle_user_response(user_input, state, chat_id)
    
    # Sprawdź czy jest niezakończona operacja
    if has_pending_operation():
        state = load_state()
        if state:
            # Jeśli czeka na odpowiedź, pokaż ponownie
            if state.get("status") == OperationStatus.DIFF_READY:
                diffs = get_stored_diffs()
                if diffs:
                    summary = create_change_summary(diffs)
                    set_awaiting_response(True, "approval")
                    return (
                        f"Masz oczekujace zmiany:\n\n{summary}\n\n**Potwierdzasz? [T/N]**",
                        True,
                        "approval"
                    )
        
        summary = get_pending_operation_summary()
        return (
            f"{summary}\n\nWpisz T aby kontynuowac lub N aby anulowac.",
            True,
            "continue_operation"
        )
    
    # Nowa operacja
    return await handle_new_operation(user_input, chat_id)


# ============================================================
# OBSŁUGA ZATWIERDZENIA (NAPRAWIONE!)
# ============================================================

async def handle_approval(state: Dict, approved: bool) -> Tuple[str, bool, Optional[str]]:
    """Obsługuje zatwierdzenie lub odrzucenie zmian"""
    
    awaiting_type = state.get("awaiting_type", "")
    operation_id = state.get("id")
    
    if not approved:
        # Odrzucono
        clear_state()
        log_event(EventType.USER_REJECTED, "Uzytkownik odrzucil zmiany", operation_id=operation_id)
        return ("Zmiany odrzucone. Operacja anulowana.", False, None)
    
    # Zatwierdzono
    if awaiting_type == "approval":
        return await execute_approved_changes(state)
    
    elif awaiting_type == "deploy_approval":
        return await execute_deploy(state)
    
    elif awaiting_type == "continue_operation":
        return await resume_operation(state)
    
    else:
        # Nieznany typ - spróbuj wykonać zmiany
        if get_stored_contents():
            return await execute_approved_changes(state)
        else:
            clear_state()
            return ("Brak zmian do wykonania.", False, None)


# ============================================================
# OBSŁUGA NOWEJ OPERACJI
# ============================================================

async def handle_new_operation(
    user_input: str,
    chat_id: str
) -> Tuple[str, bool, Optional[str]]:
    """Obsługuje nowe polecenie"""
    
    # Sprawdź czy to polecenie informacyjne (listowanie, sprawdzanie)
    info_keywords = ["wylistuj", "pokaz", "lista", "sprawdz", "ile", "jakie", "co jest", "ls", "dir"]
    is_info_request = any(kw in user_input.lower() for kw in info_keywords)
    
    if is_info_request:
        return await handle_info_request(user_input)
    
    # Utwórz operację
    operation = create_operation(user_input)
    operation_id = operation["id"]
    
    log_event(
        EventType.OPERATION_START,
        f"Nowa operacja: {user_input[:100]}",
        operation_id=operation_id
    )
    
    try:
        # 1. PLANOWANIE
        update_operation_status(OperationStatus.PLANNING)
        
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
            plan=plan,
            files_to_modify=plan.get("files_to_modify", [])
        )
        
        log_event(
            EventType.PLAN_CREATED,
            f"Plan utworzony: {len(plan.get('files_to_modify', []))} plikow",
            data=plan,
            operation_id=operation_id
        )
        
        # Jeśli są pytania od Claude
        if plan.get("questions") and len(plan.get("questions", [])) > 0:
            questions_text = "\n".join(f"- {q}" for q in plan["questions"])
            set_awaiting_response(True, "answer_questions")
            return (
                f"Mam pytania zanim zacznę:\n\n{questions_text}\n\nProszę o odpowiedź.",
                True,
                "answer_questions"
            )
        
        # Jeśli brak plików do modyfikacji - prosta odpowiedź
        if not plan.get("files_to_modify") and not plan.get("files_to_read"):
            clear_state()
            simple_prompt = get_simple_response_prompt(user_input)
            response = await call_claude([{"role": "user", "content": simple_prompt}])
            return (response, False, None)
        
        # 2. CZYTANIE PLIKÓW I GENEROWANIE ZMIAN
        return await read_and_generate_changes(plan, user_input, operation_id)
    
    except Exception as e:
        add_error(str(e))
        update_operation_status(OperationStatus.FAILED)
        raise


# ============================================================
# OBSŁUGA ŻĄDAŃ INFORMACYJNYCH (NOWE!)
# ============================================================

async def handle_info_request(user_input: str) -> Tuple[str, bool, Optional[str]]:
    """Obsługuje żądania informacyjne (listowanie plików itp.)"""
    
    lower_input = user_input.lower()
    
    # Wyciągnij ścieżkę jeśli podana
    path = ""
    
    # Szukaj ścieżki w poleceniu
    path_indicators = ["w ", "z ", "folder ", "katalog ", "directory ", "path "]
    for indicator in path_indicators:
        if indicator in lower_input:
            idx = lower_input.find(indicator) + len(indicator)
            rest = user_input[idx:].strip()
            # Weź pierwszą część jako ścieżkę
            path = rest.split()[0] if rest else ""
            break
    
    # Jeśli mowa o child theme
    if "child" in lower_input or "hello-elementor-child" in lower_input:
        path = "wp-content/themes/hello-elementor-child"
    elif "theme" in lower_input or "motyw" in lower_input:
        path = "wp-content/themes"
    elif "plugin" in lower_input or "wtyczk" in lower_input:
        path = "wp-content/plugins"
    
    # Wykonaj listowanie
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

# ============================================================
# FUNKCJA DO SKRACANIA DŁUGICH PLIKÓW
# Dodaj do agent.py przed funkcją read_and_generate_changes
# ============================================================

def truncate_file_content(content: str, max_size: int = MAX_FILE_SIZE) -> tuple[str, bool]:
    """
    Skraca zawartość pliku jeśli jest za długa.
    
    STRATEGIA:
    - Jeśli plik < max_size: zwróć cały
    - Jeśli plik > max_size: zwróć początek + koniec + info o skróceniu
    
    Returns:
        (skrócona_zawartość, czy_skrócono)
    """
    if len(content) <= max_size:
        return content, False
    
    # Ile zostawić na początku i końcu
    chunk_size = max_size // 2 - 100  # -100 na komunikat
    
    start = content[:chunk_size]
    end = content[-chunk_size:]
    
    # Oblicz ile znaków pominięto
    skipped = len(content) - (chunk_size * 2)
    skipped_lines = content[chunk_size:-chunk_size].count('\n')
    
    truncated = (
        f"{start}\n\n"
        f"[... POMINIĘTO {skipped} znaków ({skipped_lines} linii) ...]\n\n"
        f"{end}"
    )
    
    return truncated, True


def smart_truncate_for_task(content: str, task: str, file_path: str) -> str:
    """
    Inteligentne skracanie - próbuje znaleźć relevantny fragment.
    
    PRZYKŁADY:
    - Zadanie: "dodaj hook" → szukaj sekcji z hooks
    - Zadanie: "zmień funkcję calculate" → szukaj tej funkcji
    - Zadanie: "zmień CSS dla .button" → szukaj .button
    """
    # Jeśli plik jest krótki, zwróć cały
    if len(content) <= MAX_FILE_SIZE:
        return content
    
    # Próbuj znaleźć relevantny fragment
    task_lower = task.lower()
    
    # Szukaj funkcji
    if "function" in task_lower or "funkcj" in task_lower:
        # Wyciągnij nazwę funkcji z zadania
        import re
        func_match = re.search(r'funkcj[ęa]\s+(\w+)|function\s+(\w+)', task, re.IGNORECASE)
        if func_match:
            func_name = func_match.group(1) or func_match.group(2)
            # Szukaj tej funkcji w pliku
            func_pos = content.find(f"function {func_name}")
            if func_pos == -1:
                func_pos = content.find(f"def {func_name}")  # Python
            
            if func_pos != -1:
                # Wyciągnij kontekst wokół funkcji
                start = max(0, func_pos - 500)
                end = min(len(content), func_pos + MAX_FILE_SIZE - 500)
                return content[start:end]
    
    # Szukaj CSS selectora
    if file_path.endswith('.css') or file_path.endswith('.scss'):
        import re
        selector_match = re.search(r'\.([\w-]+)|\#([\w-]+)', task)
        if selector_match:
            selector = selector_match.group(0)
            selector_pos = content.find(selector)
            if selector_pos != -1:
                start = max(0, selector_pos - 500)
                end = min(len(content), selector_pos + MAX_FILE_SIZE - 500)
                return content[start:end]
    
    # Fallback: zwykłe skrócenie
    truncated, _ = truncate_file_content(content, MAX_FILE_SIZE)
    return truncated



async def read_and_generate_changes(
    plan: Dict,
    user_input: str,
    operation_id: str
) -> Tuple[str, bool, Optional[str]]:
    """Czyta pliki i generuje zmiany"""
    
    update_operation_status(OperationStatus.FILES_READ)
    
    files_to_read = plan.get("files_to_read", []) + plan.get("files_to_modify", [])
    files_to_read = list(set(files_to_read))
    
    # Przeczytaj pliki
    file_contents = {}
    errors = []
    
    for path in files_to_read:
        try:
            # Sprawdź typ ścieżki
            path_type = get_path_type(path)
            
            if path_type == "directory":
                # To katalog - wylistuj zawartość
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
    
    # Jeśli wszystkie błędy - zwróć informację
    if errors and not file_contents:
        clear_state()
        return (
            f"Nie udalo sie przeczytac plikow:\n" + "\n".join(errors),
            False, None
        )
    
    # Generuj zmiany dla każdego pliku (tylko pliki, nie katalogi)
    files_to_modify = [f for f in plan.get("files_to_modify", []) 
                       if f in file_contents and not file_contents[f].startswith("[KATALOG]")]
    
    if not files_to_modify:
        clear_state()
        # Pokaż wyniki odczytu
        result = "**Wyniki analizy:**\n\n"
        for path, content in file_contents.items():
            if content.startswith("[KATALOG]"):
                result += f"📁 **{path}**\n{content}\n\n"
            else:
                result += f"📄 **{path}** ({len(content)} znakow)\n"
        
        if errors:
            result += "\n**Bledy:**\n" + "\n".join(errors)
        
        return (result, False, None)
    
    new_contents = {}
    diffs = {}
    
    for path in files_to_modify:
        old_content_full = file_contents[path]

        # OPTYMALIZACJA: Skróć długie pliki
        old_content = smart_truncate_for_task(
            old_content_full,
            task=plan.get('understood_intent', user_input),
            file_path=path
        )
        
        if len(old_content) < len(old_content_full):
            print(f"[OPTYM] Skrócono plik {path}: "
                  f"{len(old_content_full)} → {len(old_content)} znaków "
                  f"(oszczędność: {len(old_content_full) - len(old_content)})")
        
        coder_prompt = get_coder_prompt(
            file_path=path,
            current_content=old_content,
            task_description=f"{plan.get('understood_intent', user_input)}\n\nKroki: {plan.get('steps', [])}",
            conventions=get_minimal_context()
        )
        
        new_content = await call_claude([{"role": "user", "content": coder_prompt}])
        
        # NAPRAWKA #3: Wyczyść markdown code blocks
        new_content_cleaned = clean_code_for_file(new_content, path)
        new_contents[path] = new_content_cleaned
        
        # Użyj wyczyszczonej wersji do diff
        diff = generate_diff(old_content, new_content_cleaned, path)
        diffs[path] = diff
    
    # Zapisz do stanu z weryfikacją (NAPRAWKA #2)
    store_diffs(diffs)
    
    if not store_new_contents(new_contents):
        add_error("Nie udalo sie zapisac nowych zawartosci do stanu!")
        return (
            "Blad wewnetrzny: nie mozna zapisac zmian do stanu. Sprobuj ponownie.",
            False, None
        )
    
    update_operation_status(OperationStatus.DIFF_READY)
    
    log_event(
        EventType.DIFF_GENERATED,
        f"Wygenerowano diffy dla {len(diffs)} plikow",
        operation_id=operation_id
    )
    
    # Pokaż użytkownikowi
    summary = create_change_summary(diffs)
    
    diff_preview = ""
    for path, diff in diffs.items():
        diff_preview += f"\n\n--- {path} ---\n"
        diff_preview += format_diff_for_display(diff, max_lines=30)
    
    set_awaiting_response(True, "approval")
    
    return (
        f"**PLAN:** {plan.get('understood_intent', 'Zmiany w plikach')}\n\n"
        f"{summary}\n"
        f"{diff_preview}\n\n"
        f"**Potwierdzasz zmiany? [T/N]**",
        True,
        "approval"
    )


# ============================================================
# OBSŁUGA ODPOWIEDZI UŻYTKOWNIKA
# ============================================================

async def handle_user_response(
    user_input: str,
    state: Dict,
    chat_id: str
) -> Tuple[str, bool, Optional[str]]:
    """Obsługuje odpowiedź użytkownika"""
    
    awaiting_type = state.get("awaiting_type", "")
    
    # Interpretuj odpowiedź
    approval_prompt = get_approval_prompt(user_input)
    interpretation = await call_claude([{"role": "user", "content": approval_prompt}])
    interpretation = interpretation.strip().lower()
    
    # Obsłuż różne typy odpowiedzi
    if interpretation == "approve":
        return await handle_approval(state, True)
    
    elif interpretation == "reject":
        return await handle_approval(state, False)
    
    elif interpretation == "question":
        # Użytkownik zadaje pytanie
        set_awaiting_response(True, awaiting_type)  # Zachowaj typ
        
        response = await call_claude([
            {"role": "user", "content": state.get("user_input", "")},
            {"role": "assistant", "content": "Przygotowalem zmiany..."},
            {"role": "user", "content": user_input}
        ])
        return (f"{response}\n\n**Potwierdzasz zmiany? [T/N]**", True, awaiting_type)
    
    else:
        # Nierozpoznana odpowiedź
        set_awaiting_response(True, awaiting_type)
        return (
            "Nie zrozumialem. Wpisz **T** aby zatwierdzic lub **N** aby odrzucic.",
            True, 
            awaiting_type
        )


# ============================================================
# WYKONANIE ZMIAN
# ============================================================

async def execute_approved_changes(state: Dict) -> Tuple[str, bool, Optional[str]]:
    """Zapisuje zatwierdzone zmiany"""
    
    operation_id = state.get("id")
    new_contents = get_stored_contents()
    
    if not new_contents:
        clear_state()
        return ("Brak zmian do zapisania.", False, None)
    
    log_event(EventType.USER_APPROVED, "Uzytkownik zatwierdzil zmiany", operation_id=operation_id)
    
    update_operation_status(OperationStatus.WRITING)
    
    written = []
    errors = []
    
    for path, content in new_contents.items():
        try:
            write_file(path, content, operation_id)
            written.append(path)
        except Exception as e:
            errors.append(f"{path}: {e}")
            add_error(f"Blad zapisu {path}: {e}")
    
    if errors and not written:
        update_operation_status(OperationStatus.FAILED)
        clear_state()
        return (
            f"Blad zapisu plikow:\n" + "\n".join(errors),
            False, None
        )
    
    update_operation_status(OperationStatus.WRITTEN, files_written=written)
    
    # Pytaj o deploy
    set_awaiting_response(True, "deploy_approval")
    
    msg = f"✅ Zapisano {len(written)} plikow:\n"
    msg += "\n".join(f"- {f}" for f in written)
    
    if errors:
        msg += f"\n\n⚠️ Bledy:\n" + "\n".join(errors)
    
    msg += "\n\n**Wykonac deploy (sprawdzic czy strona dziala)? [T/N]**"
    
    return (msg, True, "deploy_approval")


async def execute_deploy(state: Dict) -> Tuple[str, bool, Optional[str]]:
    """Wykonuje deploy"""
    
    operation_id = state.get("id")
    update_operation_status(OperationStatus.DEPLOYING)
    
    result = deploy(operation_id)
    
    update_operation_status(OperationStatus.COMPLETED, deploy_result=result)
    clear_state()
    
    log_event(EventType.OPERATION_END, "Operacja zakonczona", operation_id=operation_id)
    
    if result["status"] == "ok":
        return (f"✅ Deploy zakonczony!\n{result['msg']}", False, None)
    else:
        return (
            f"⚠️ Deploy z ostrzezeniem:\n{result['msg']}\n\nUzyj /rollback jesli cos nie dziala.",
            False, None
        )


async def resume_operation(state: Dict) -> Tuple[str, bool, Optional[str]]:
    """Wznawia przerwaną operację"""
    
    status = state.get("status")
    
    if status == OperationStatus.DIFF_READY:
        diffs = get_stored_diffs()
        if diffs:
            summary = create_change_summary(diffs)
            set_awaiting_response(True, "approval")
            return (f"Kontynuuje...\n\n{summary}\n\n**Potwierdzasz? [T/N]**", True, "approval")
    
    if status == OperationStatus.WRITTEN:
        set_awaiting_response(True, "deploy_approval")
        return ("Pliki zapisane. **Wykonac deploy? [T/N]**", True, "deploy_approval")
    
    clear_state()
    return ("Nie mozna wznowic operacji. Zaczynam od nowa.", False, None)


# ============================================================
# KOMENDY SPECJALNE
# ============================================================

async def handle_status_command() -> Tuple[str, bool, Optional[str]]:
    """Obsługuje /status"""
    state = load_state()
    
    if not state:
        return ("✅ Agent jest gotowy. Brak aktywnych operacji.", False, None)
    
    return (
        f"**STATUS AGENTA**\n\n"
        f"ID: {state.get('id', 'brak')}\n"
        f"Status: {state.get('status', 'nieznany')}\n"
        f"Polecenie: {state.get('user_input', 'brak')[:100]}\n"
        f"Pliki do zmiany: {len(state.get('files_to_modify', []))}\n"
        f"Pliki zapisane: {len(state.get('files_written', []))}\n"
        f"Oczekuje odpowiedzi: {state.get('awaiting_response', False)}\n"
        f"Typ odpowiedzi: {state.get('awaiting_type', 'brak')}",
        False, None
    )


async def handle_rollback_command() -> Tuple[str, bool, Optional[str]]:
    """Obsługuje /rollback"""
    result = rollback()
    clear_state()
    
    if result["status"] == "ok":
        return (f"✅ Rollback zakonczony.\nPrzywrocono: {', '.join(result.get('restored', []))}", False, None)
    else:
        return (f"⚠️ Rollback: {result['msg']}", False, None)


async def handle_clear_command() -> Tuple[str, bool, Optional[str]]:
    """Obsługuje /clear"""
    clear_state()
    return ("✅ Stan wyczyszczony. Agent gotowy do nowych polecen.", False, None)


def handle_help_command() -> Tuple[str, bool, Optional[str]]:
    """Obsługuje /help"""
    return (
        "**JADZIA - Pomoc**\n\n"
        "Jestem asystentem do zarzadzania sklepem internetowym.\n\n"
        "**Komendy:**\n"
        "/status - sprawdz status agenta\n"
        "/rollback - cofnij ostatnie zmiany\n"
        "/clear - wyczysc stan (awaryjne)\n"
        "/test - test polaczenia SSH\n"
        "/help - ta pomoc\n\n"
        "**Przyklady polecen:**\n"
        "- 'Zmien kolor przyciskow na niebieski'\n"
        "- 'Wylistuj pliki w motywie child'\n"
        "- 'Dodaj baner promocyjny na stronie glownej'\n"
        "- 'Popraw tekst w stopce'\n\n"
        "**Odpowiedzi:**\n"
        "- T / tak - zatwierdz zmiany\n"
        "- N / nie - odrzuc zmiany\n\n"
        "Zawsze pokazuje zmiany przed zapisaniem i czekam na Twoja zgode.",
        False, None
    )


async def handle_test_command() -> Tuple[str, bool, Optional[str]]:
    """Obsługuje /test"""
    success, msg = test_ssh_connection()
    if success:
        return (f"✅ Test SSH: OK\n{msg}", False, None)
    else:
        return (f"❌ Test SSH: BLAD\n{msg}", False, None)


# ============================================================
# OBSŁUGA BŁĘDÓW
# ============================================================

async def handle_error(
    error: Exception,
    chat_id: str
) -> Tuple[str, bool, Optional[str]]:
    """Obsługuje błędy"""
    
    error_msg = str(error)
    
    try:
        state = load_state()
        recovery_prompt = get_error_recovery_prompt(
            error_message=error_msg,
            context=f"Chat: {chat_id}",
            operation_state=state.get("status", "nieznany") if state else "brak operacji"
        )
        
        response = await call_claude([{"role": "user", "content": recovery_prompt}])
        return (response, False, None)
    
    except Exception:
        return (
            f"❌ Wystapil blad: {error_msg}\n\n"
            "Mozesz:\n"
            "- /rollback - cofnac zmiany\n"
            "- /clear - wyczysc stan\n"
            "- /status - sprawdz status",
            False, None
        )


# ============================================================
# HELPERS
# ============================================================

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
        "questions": [],
        "risks": []
    }

def get_cost_stats() -> dict:
    """Zwraca statystyki użycia i kosztów."""
    return {
        "total_input_tokens": TOKEN_STATS["input"],
        "total_output_tokens": TOKEN_STATS["output"],
        "total_cached_tokens": TOKEN_STATS["cached"],
        "total_cost_usd": round(TOKEN_STATS["cost"], 4),
        "estimated_savings_from_cache": round(
            (TOKEN_STATS["cached"] / 1_000_000) * (3.0 - 0.30), 4
        ) if TOKEN_STATS["cached"] > 0 else 0
    }


def reset_cost_stats():
    """Resetuje statystyki."""
    TOKEN_STATS["input"] = 0
    TOKEN_STATS["output"] = 0
    TOKEN_STATS["cached"] = 0
    TOKEN_STATS["cost"] = 0.0