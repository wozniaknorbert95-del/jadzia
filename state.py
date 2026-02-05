"""
state.py — Persystencja stanu i zarządzanie operacjami

NAPRAWIONE:
- Absolutne ścieżki do plików stanu
- Weryfikacja zapisu store_new_contents()
- Dodatkowe logowanie debug
"""

import json
import time
import os
from pathlib import Path
from typing import Optional, Dict, List
from contextlib import contextmanager
from datetime import datetime

# ============================================================
# NAPRAWKA #1: ABSOLUTNE ŚCIEŻKI
# ============================================================

# Stara wersja (BŁ ĄD):
# DATA_DIR = Path("data")  # ← względna do CWD!

# Nowa wersja (POPRAWKA):
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

STATE_FILE = DATA_DIR / ".agent_state.json"
LOCK_FILE = DATA_DIR / ".agent.lock"


class OperationStatus:
    PENDING = "pending"
    PLANNING = "planning"
    FILES_READ = "files_read"
    DIFF_READY = "diff_ready"
    APPROVED = "approved"
    WRITING = "writing"
    WRITTEN = "written"
    COMMITTED = "committed"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


def save_state(state: dict) -> None:
    """Zapisuje stan do pliku"""
    state["updated_at"] = datetime.now().isoformat()
    try:
        STATE_FILE.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    except Exception as e:
        print(f"[STATE ERROR] Nie mozna zapisac stanu: {e}")


def load_state() -> Optional[dict]:
    """Ładuje stan z pliku"""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
        except Exception:
            return None
    return None


def clear_state() -> None:
    """Czyści stan"""
    if STATE_FILE.exists():
        try:
            archive_state()
            STATE_FILE.unlink()
        except Exception as e:
            print(f"[STATE ERROR] Nie mozna wyczyścić stanu: {e}")


def archive_state() -> None:
    """Archiwizuje stan"""
    state = load_state()
    if state:
        try:
            archive_file = DATA_DIR / f"state_archive_{int(time.time())}.json"
            archive_file.write_text(
                json.dumps(state, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception:
            pass


def has_pending_operation() -> bool:
    """Sprawdza czy jest niezakończona operacja"""
    state = load_state()
    if not state:
        return False
    
    terminal_states = {
        OperationStatus.COMPLETED,
        OperationStatus.FAILED,
        OperationStatus.CANCELLED
    }
    
    return state.get("status") not in terminal_states


def get_pending_operation_summary() -> Optional[str]:
    """Zwraca podsumowanie niezakończonej operacji"""
    state = load_state()
    if not state or not has_pending_operation():
        return None
    
    return f"""
NIEZAKONCZONA OPERACJA

Status: {state.get('status')}
Polecenie: {state.get('user_input', 'nieznane')}
Pliki do zmiany: {', '.join(state.get('files_to_modify', []))}
"""


class LockError(Exception):
    pass


@contextmanager
def agent_lock(timeout: int = 30):
    """Context manager dla wyłącznego dostępu"""
    lock_acquired = False
    
    try:
        start = time.time()
        
        while True:
            try:
                if LOCK_FILE.exists():
                    lock_age = time.time() - LOCK_FILE.stat().st_mtime
                    if lock_age > 300:
                        LOCK_FILE.unlink()
                    else:
                        raise BlockingIOError("Lock exists")
                
                LOCK_FILE.write_text(str(os.getpid()), encoding="utf-8")
                lock_acquired = True
                break
                
            except BlockingIOError:
                if time.time() - start > timeout:
                    raise LockError("Agent jest zajety inna operacja.")
                time.sleep(0.5)
            except Exception as e:
                if time.time() - start > timeout:
                    raise LockError(f"Nie mozna uzyskac blokady: {e}")
                time.sleep(0.5)
        
        yield
        
    finally:
        if lock_acquired and LOCK_FILE.exists():
            try:
                LOCK_FILE.unlink()
            except Exception:
                pass


def is_locked() -> bool:
    if not LOCK_FILE.exists():
        return False
    try:
        lock_age = time.time() - LOCK_FILE.stat().st_mtime
        if lock_age > 300:
            return False
        return True
    except Exception:
        return False


def force_unlock() -> bool:
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
        return True
    except Exception:
        return False


def create_operation(user_input: str) -> dict:
    """Tworzy nową operację"""
    state = {
        "id": f"op_{int(time.time())}",
        "status": OperationStatus.PENDING,
        "user_input": user_input,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "plan": None,
        "files_to_modify": [],
        "files_read": {},
        "diffs": {},
        "new_contents": {},
        "files_written": [],
        "files_pending": [],
        "backups": {},
        "commit_hash": None,
        "deploy_result": None,
        "errors": [],
        "awaiting_response": False,
        "awaiting_type": None,
    }
    save_state(state)
    return state


def update_operation_status(status: str, **kwargs) -> dict:
    """Aktualizuje status operacji"""
    state = load_state()
    if not state:
        raise RuntimeError("Brak aktywnej operacji")
    
    state["status"] = status
    state["updated_at"] = datetime.now().isoformat()
    
    for key, value in kwargs.items():
        state[key] = value
    
    save_state(state)
    return state


def add_error(error: str) -> None:
    state = load_state()
    if state:
        state.setdefault("errors", []).append({
            "timestamp": datetime.now().isoformat(),
            "error": str(error)
        })
        save_state(state)


def mark_file_written(path: str, backup_path: Optional[str] = None) -> None:
    state = load_state()
    if state:
        if path not in state.get("files_written", []):
            state.setdefault("files_written", []).append(path)
        
        if backup_path:
            state.setdefault("backups", {})[path] = backup_path
        
        pending = state.get("files_pending", [])
        if path in pending:
            pending.remove(path)
        state["files_pending"] = pending
        
        save_state(state)


def get_backups() -> Dict[str, str]:
    state = load_state()
    return state.get("backups", {}) if state else {}


def set_awaiting_response(awaiting: bool, response_type: Optional[str] = None) -> None:
    state = load_state()
    if state:
        state["awaiting_response"] = awaiting
        state["awaiting_type"] = response_type
        save_state(state)


def get_operation_id() -> Optional[str]:
    state = load_state()
    return state.get("id") if state else None


def get_current_status() -> Optional[str]:
    state = load_state()
    return state.get("status") if state else None


# ============================================================
# NAPRAWKA #2: WERYFIKACJA ZAPISU
# ============================================================

def store_diffs(diffs: Dict[str, str]) -> None:
    """Zapisuje wygenerowane diffy"""
    state = load_state()
    if state:
        state["diffs"] = diffs
        save_state(state)
        print(f"[DEBUG] store_diffs: zapisano {len(diffs)} diffow")


def get_stored_diffs() -> Dict[str, str]:
    """Pobiera zapisane diffy"""
    state = load_state()
    diffs = state.get("diffs", {}) if state else {}
    print(f"[DEBUG] get_stored_diffs: znaleziono {len(diffs)} diffow")
    return diffs


def store_new_contents(contents: Dict[str, str]) -> bool:
    """
    Zapisuje nowe zawartości plików z weryfikacją.
    
    Returns:
        True jeśli zapis się powiódł, False w przeciwnym razie
    """
    state = load_state()
    if not state:
        print(f"[ERROR] store_new_contents: Brak stanu!")
        return False
    
    # Zapisz
    state["new_contents"] = contents
    save_state(state)
    
    print(f"[DEBUG] store_new_contents: zapisano {len(contents)} plikow")
    print(f"[DEBUG] klucze: {list(contents.keys())}")
    
    # ============================================================
    # WERYFIKACJA - sprawdź czy dane faktycznie się zapisały
    # ============================================================
    verify_state = load_state()
    if not verify_state:
        print(f"[ERROR] Weryfikacja: nie można wczytać stanu!")
        return False
    
    saved_keys = list(verify_state.get("new_contents", {}).keys())
    expected_keys = list(contents.keys())
    
    if set(saved_keys) != set(expected_keys):
        print(f"[ERROR] Weryfikacja nieudana!")
        print(f"  Oczekiwano: {expected_keys}")
        print(f"  Zapisano:   {saved_keys}")
        return False
    
    # Sprawdź czy zawartość się zgadza
    for key in expected_keys:
        original_len = len(contents[key])
        saved_len = len(verify_state["new_contents"][key])
        
        if original_len != saved_len:
            print(f"[ERROR] Niezgodność długości dla {key}:")
            print(f"  Oryginał: {original_len} znaków")
            print(f"  Zapisano: {saved_len} znaków")
            return False
    
    print(f"[OK] Weryfikacja zapisanych treści: SUKCES")
    return True


def get_stored_contents() -> Dict[str, str]:
    """Pobiera zapisane nowe zawartości"""
    state = load_state()
    contents = state.get("new_contents", {}) if state else {}
    print(f"[DEBUG] get_stored_contents: znaleziono {len(contents)} plikow")
    print(f"[DEBUG] klucze: {list(contents.keys())}")
    
    if contents:
        # Dodatkowa weryfikacja przy odczycie
        for key, value in contents.items():
            if not isinstance(value, str):
                print(f"[WARNING] Plik {key} ma nieprawidłowy typ: {type(value)}")
            elif len(value) == 0:
                print(f"[WARNING] Plik {key} jest pusty!")
    
    return contents
