"""
Rest of tools: rollback, health_check, health_check_wordpress, test_ssh_connection, deploy, git_*, cleanup.
Uses ssh_pure for SSH I/O and guardrails for get_safe_path.
"""

import os
import time
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv
load_dotenv()

from agent.guardrails import get_safe_path
from agent.state import get_backups
from agent.log import log_event, log_error, EventType
from agent.tools.ssh_pure import (
    ConnectionError,
    with_retry,
    read_file_ssh_bytes,
    write_file_ssh_bytes,
    exec_command_ssh,
)

# Config from env
HOST = os.getenv("SSH_HOST") or os.getenv("CYBERFOLKS_HOST", "")
PORT = int(os.getenv("SSH_PORT") or os.getenv("CYBERFOLKS_PORT") or 22)
USER = os.getenv("SSH_USER") or os.getenv("CYBERFOLKS_USER", "")
PASSWORD = os.getenv("SSH_PASSWORD", "")
KEY_PATH_RAW = os.getenv("SSH_KEY_PATH") or os.getenv("CYBERFOLKS_KEY_PATH", "") or None
KEY_PATH = KEY_PATH_RAW if KEY_PATH_RAW and os.path.exists(KEY_PATH_RAW) else None
BASE_PATH = os.getenv("BASE_PATH") or os.getenv("CYBERFOLKS_BASE_PATH", "/home/user/public_html")
LOCAL_REPO_PATH = Path(os.getenv("LOCAL_REPO_PATH", "./repo"))
SHOP_URL = os.getenv("SHOP_URL", "")


def test_ssh_connection() -> tuple:
    """Test SSH connection."""
    if not HOST or not USER:
        return False, "Brak konfiguracji SSH w .env"
    try:
        success, stdout, _ = exec_command_ssh(HOST, PORT, USER, PASSWORD, "echo 'OK'", KEY_PATH)
        if success and "OK" in stdout:
            return True, "Polaczenie SSH dziala"
        return False, f"Nieoczekiwana odpowiedz: {stdout}"
    except Exception as e:
        return False, f"Blad polaczenia: {e}"


def rollback(operation_id: Optional[str] = None, chat_id: str = "default", source: str = "http") -> Dict[str, Any]:
    """Restore files from backups."""
    backups = get_backups(chat_id, source)
    if not backups:
        return {"status": "error", "msg": "Brak backupow do przywrocenia", "restored": []}
    restored = []
    errors = []
    try:
        for original_path, backup_path in backups.items():
            if not backup_path:
                continue
            try:
                content = read_file_ssh_bytes(HOST, PORT, USER, PASSWORD, backup_path, KEY_PATH)
                full_original = get_safe_path(BASE_PATH, original_path)
                write_file_ssh_bytes(HOST, PORT, USER, PASSWORD, full_original, content, KEY_PATH)
                restored.append(original_path)
            except Exception as e:
                errors.append(f"{original_path}: {e}")
        log_event(
            EventType.ROLLBACK,
            f"Rollback: przywrocono {len(restored)} plikow",
            data={"restored": restored, "errors": errors},
            operation_id=operation_id,
        )
        if errors:
            return {
                "status": "partial",
                "msg": f"Przywrocono {len(restored)}, bledy: {len(errors)}",
                "restored": restored,
                "errors": errors,
            }
        return {"status": "ok", "msg": f"Przywrocono {len(restored)} plikow", "restored": restored}
    except Exception as e:
        return {"status": "error", "msg": str(e), "restored": []}


def health_check() -> Dict[str, Any]:
    """Check if site is up."""
    if not SHOP_URL:
        return {"status": "warning", "msg": "Brak SHOP_URL w konfiguracji"}
    try:
        import httpx
        start = time.time()
        response = httpx.get(SHOP_URL, timeout=30, follow_redirects=True)
        response_time = time.time() - start
        log_event(
            EventType.HEALTH_CHECK,
            f"Health check: {response.status_code} ({response_time:.2f}s)",
            data={"status_code": response.status_code, "response_time": response_time, "url": SHOP_URL},
        )
        if response.status_code == 200:
            return {"status": "ok", "msg": f"Strona OK ({response_time:.2f}s)", "response_time": response_time}
        return {"status": "warning", "msg": f"Strona zwraca {response.status_code}", "response_time": response_time}
    except Exception as e:
        return {"status": "error", "msg": f"Blad: {e}"}


async def health_check_wordpress(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Performs HTTP health check on WordPress site.

    Args:
        url: Full WordPress homepage URL (e.g., https://zzpackage.flexgrafik.nl)
        timeout: Request timeout in seconds

    Returns:
        {
            "healthy": bool,           # True if status 200-299
            "status_code": int|None,   # HTTP status code
            "response_time": float,    # Time in seconds
            "error": str|None          # Error message if failed
        }
    """
    import httpx

    result: Dict[str, Any] = {
        "healthy": False,
        "status_code": None,
        "response_time": 0.0,
        "error": None,
    }
    try:
        start = time.perf_counter()
        async with httpx.AsyncClient(follow_redirects=True, timeout=float(timeout)) as client:
            response = await client.get(url)
        result["response_time"] = time.perf_counter() - start
        result["status_code"] = response.status_code
        if 200 <= response.status_code < 300:
            result["healthy"] = True
            return result
        result["error"] = f"HTTP {response.status_code}"
        return result
    except httpx.TimeoutException as e:
        result["error"] = f"Timeout: {e}"
        return result
    except httpx.ConnectError as e:
        result["error"] = f"Connection error: {e}"
        return result
    except Exception as e:
        result["error"] = str(e)
        return result


def deploy(operation_id: Optional[str] = None) -> Dict[str, str]:
    """Deploy (verify health)."""
    log_event(EventType.DEPLOY_START, "Rozpoczeto deploy", operation_id=operation_id)
    try:
        health = health_check()
        if health["status"] == "ok":
            log_event(EventType.DEPLOY_SUCCESS, "Deploy zakonczony sukcesem", data=health, operation_id=operation_id)
            return {"status": "ok", "msg": "Zmiany zapisane, strona dziala"}
        log_event(
            EventType.DEPLOY_SUCCESS,
            f"Deploy z ostrzezeniem: {health['msg']}",
            data=health,
            operation_id=operation_id,
        )
        return {"status": "warning", "msg": health["msg"]}
    except Exception as e:
        log_event(EventType.DEPLOY_FAILED, f"Deploy blad: {e}", operation_id=operation_id)
        return {"status": "error", "msg": str(e)}


def git_status() -> str:
    """Local git status."""
    if not LOCAL_REPO_PATH.exists():
        return "Brak lokalnego repozytorium"
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=LOCAL_REPO_PATH,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout or "Brak zmian"
    except Exception as e:
        return f"Blad git: {e}"


def git_commit(message: str, operation_id: Optional[str] = None) -> Optional[str]:
    """Local git commit."""
    from agent.guardrails import sanitize_commit_message
    if not LOCAL_REPO_PATH.exists():
        log_error("Brak lokalnego repozytorium dla git commit")
        return None
    safe_message = sanitize_commit_message(message)
    try:
        subprocess.run(["git", "add", "-A"], cwd=LOCAL_REPO_PATH, check=True, timeout=30)
        subprocess.run(
            ["git", "commit", "-m", safe_message],
            cwd=LOCAL_REPO_PATH,
            capture_output=True,
            text=True,
            timeout=30,
        )
        hash_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=LOCAL_REPO_PATH,
            capture_output=True,
            text=True,
            timeout=30,
        )
        commit_hash = hash_result.stdout.strip()
        log_event(
            EventType.GIT_COMMIT,
            f"Commit: {commit_hash[:8]} - {safe_message}",
            data={"hash": commit_hash, "message": safe_message},
            operation_id=operation_id,
        )
        return commit_hash
    except Exception as e:
        log_error(f"Blad git commit: {e}")
        return None


def cleanup_old_backups(max_age_days: int = 7) -> int:
    """Remove backup files older than max_age_days."""
    max_age_seconds = max_age_days * 24 * 60 * 60
    now = time.time()
    deleted = 0
    try:
        cmd = f"find {BASE_PATH} -name '*.backup.*' -type f 2>/dev/null"
        success, stdout, _ = exec_command_ssh(HOST, PORT, USER, PASSWORD, cmd, KEY_PATH)
        for backup_path in stdout.strip().split("\n"):
            if not backup_path:
                continue
            try:
                ts_str = backup_path.split(".backup.")[-1]
                ts = int(ts_str)
                if now - ts > max_age_seconds:
                    # Remove via SSH: we need a remove command. ssh_pure doesn't have remove_file_ssh.
                    # Original used conn.sftp.remove(backup_path). So we need either exec_command_ssh("rm ...") or add remove to pure.
                    exec_command_ssh(HOST, PORT, USER, PASSWORD, f"rm -f '{backup_path}'", KEY_PATH)
                    deleted += 1
            except (ValueError, IOError):
                continue
        if deleted > 0:
            log_event(EventType.FILE_WRITE, f"Cleanup: usunieto {deleted} starych backupow")
    except Exception:
        pass
    return deleted
