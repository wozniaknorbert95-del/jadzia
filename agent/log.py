"""
log.py — Audit trail wszystkich operacji

Format: JSON Lines (.jsonl) — jeden JSON per linia
Łatwe do parsowania, appendowania i przeszukiwania
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Any, List

# ============================================================
# KONFIGURACJA
# ============================================================

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "agent.log"


# ============================================================
# TYPY ZDARZEŃ
# ============================================================

class EventType:
    OPERATION_START = "operation_start"
    OPERATION_STEP = "operation_step"  # used by routing.py for test_mode auto-approval log
    OPERATION_END = "operation_end"
    PLAN_CREATED = "plan_created"
    FILES_READ = "files_read"
    DIFF_GENERATED = "diff_generated"
    USER_APPROVED = "user_approved"
    USER_REJECTED = "user_rejected"
    FILE_BACKUP = "file_backup"
    FILE_WRITE = "file_write"
    GIT_COMMIT = "git_commit"
    DEPLOY_START = "deploy_start"
    DEPLOY_SUCCESS = "deploy_success"
    DEPLOY_FAILED = "deploy_failed"
    HEALTH_CHECK = "health_check"
    ROLLBACK = "rollback"
    ERROR = "error"


# ============================================================
# FUNKCJE LOGOWANIA
# ============================================================

def log_event(
    event_type: str,
    message: str,
    data: Optional[dict] = None,
    operation_id: Optional[str] = None,
    task_id: Optional[str] = None,
    chat_id: Optional[str] = None,
) -> None:
    """
    Loguje zdarzenie do audit trail.
    task_id: ID zadania (opcjonalne, dla concurrent tasks).
    chat_id: przy podanym task_id i chat_id, w trybie dry_run dodawany jest prefix [DRY-RUN].
    """
    if chat_id and task_id:
        try:
            from agent.state import is_dry_run
            if is_dry_run(chat_id, task_id) and not message.strip().startswith("[DRY-RUN]"):
                message = "[DRY-RUN] " + message
        except Exception:
            pass
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "message": message,
        "operation_id": operation_id,
        "task_id": task_id,
        "data": data
    }
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[LOG ERROR] Nie można zapisać logu: {e}")


def log_change(
    action: str,
    files: List[str],
    user_input: str,
    diff_preview: str,
    operation_id: Optional[str] = None,
    task_id: Optional[str] = None,
) -> None:
    """Loguje zmianę plików (convenience wrapper)."""
    log_event(
        event_type=EventType.FILE_WRITE,
        message=f"Zapisano {len(files)} plikow",
        data={
            "action": action,
            "files": files,
            "user_input": user_input[:200],
            "diff_preview": diff_preview[:500]
        },
        operation_id=operation_id,
        task_id=task_id,
    )


def log_error(
    error: str,
    context: Optional[dict] = None,
    operation_id: Optional[str] = None,
    task_id: Optional[str] = None,
) -> None:
    """Loguje błąd."""
    log_event(
        event_type=EventType.ERROR,
        message=error,
        data=context,
        operation_id=operation_id,
        task_id=task_id,
    )


# ============================================================
# ODCZYT LOGÓW
# ============================================================

def get_recent_logs(limit: int = 50) -> List[dict]:
    """Zwraca ostatnie N wpisów"""
    if not LOG_FILE.exists():
        return []
    
    try:
        lines = LOG_FILE.read_text(encoding="utf-8").strip().split("\n")
        recent = lines[-limit:] if len(lines) > limit else lines
        
        return [json.loads(line) for line in recent if line]
    except Exception as e:
        print(f"[LOG ERROR] Nie można odczytać logów: {e}")
        return []


def get_logs_for_operation(operation_id: str) -> List[dict]:
    """Zwraca wszystkie logi dla danej operacji"""
    if not LOG_FILE.exists():
        return []
    
    logs = []
    try:
        for line in LOG_FILE.read_text(encoding="utf-8").strip().split("\n"):
            if not line:
                continue
            entry = json.loads(line)
            if entry.get("operation_id") == operation_id:
                logs.append(entry)
    except Exception as e:
        print(f"[LOG ERROR] Błąd odczytu: {e}")
    
    return logs


def get_logs_by_type(event_type: str, limit: int = 100) -> List[dict]:
    """Zwraca logi określonego typu"""
    if not LOG_FILE.exists():
        return []
    
    logs = []
    try:
        for line in LOG_FILE.read_text(encoding="utf-8").strip().split("\n"):
            if not line:
                continue
            entry = json.loads(line)
            if entry.get("event_type") == event_type:
                logs.append(entry)
                if len(logs) >= limit:
                    break
    except Exception:
        pass
    
    return logs


def search_logs(query: str, limit: int = 50) -> List[dict]:
    """Proste wyszukiwanie w logach"""
    if not LOG_FILE.exists():
        return []
    
    query_lower = query.lower()
    logs = []
    
    try:
        for line in LOG_FILE.read_text(encoding="utf-8").strip().split("\n"):
            if not line:
                continue
            if query_lower in line.lower():
                logs.append(json.loads(line))
                if len(logs) >= limit:
                    break
    except Exception:
        pass
    
    return logs


# ============================================================
# MAINTENANCE
# ============================================================

def rotate_logs(max_size_mb: int = 10) -> bool:
    """Rotuje logi gdy przekroczą rozmiar"""
    if not LOG_FILE.exists():
        return False
    
    try:
        size_mb = LOG_FILE.stat().st_size / (1024 * 1024)
        
        if size_mb > max_size_mb:
            archive_path = LOGS_DIR / f"agent_{int(datetime.now(timezone.utc).timestamp())}.log"
            LOG_FILE.rename(archive_path)
            return True
    except Exception as e:
        print(f"[LOG ERROR] Nie można zrotować logów: {e}")
    
    return False


def get_log_stats() -> dict:
    """Zwraca statystyki logów"""
    if not LOG_FILE.exists():
        return {"entries": 0, "size_kb": 0}
    
    try:
        lines = LOG_FILE.read_text(encoding="utf-8").strip().split("\n")
        size_kb = LOG_FILE.stat().st_size / 1024
        
        return {
            "entries": len([l for l in lines if l]),
            "size_kb": round(size_kb, 2)
        }
    except Exception:
        return {"entries": 0, "size_kb": 0}