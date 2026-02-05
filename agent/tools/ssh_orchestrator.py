"""
SSH orchestrator: pure SSH I/O + guardrails + state + logging.
Reads config from env. Exposes read_file, write_file, list_files, list_directory, get_path_type, exec_ssh_command.
Also SSHOrchestrator class with verify_deployment for self-healing.
"""

import asyncio
import os
import time
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

from dotenv import load_dotenv
load_dotenv()

from agent.guardrails import validate_operation, validate_content, check_wordpress_safety, OperationType, get_safe_path
from agent.state import mark_file_written
from agent.log import log_event, log_error, EventType


class SecurityError(Exception):
    """Raised when security validation fails."""
    pass


class SSHOrchestrator:
    """Orchestrator with deployment verification (self-healing)."""

    def log_event(self, message: str, **kwargs) -> None:
        """Delegate to agent.log.log_event for [VERIFICATION] and other events."""
        log_event(EventType.FILE_WRITE, message, **kwargs)

    async def verify_deployment(self, operation_id: str, base_url: str) -> Dict[str, Any]:
        """
        Verifies deployment health. Does not trigger rollback; that is done in the approval node.

        Steps:
        1. Wait 2 seconds (PHP opcache clear time)
        2. Call health_check_wordpress(base_url)
        3. Log verification result with [VERIFICATION] prefix
        4. Return health report

        Args:
            operation_id: Current operation ID (for logging)
            base_url: WordPress site URL

        Returns:
            Same dict as health_check_wordpress() + {"auto_rollback_triggered": False}
        """
        from agent.tools.rest import health_check_wordpress

        await asyncio.sleep(2)
        health = await health_check_wordpress(base_url, timeout=10)
        health["auto_rollback_triggered"] = False

        if health["healthy"]:
            self.log_event(
                f"[VERIFICATION] SUCCESS for {operation_id} (HTTP {health.get('status_code', 'N/A')}, {health.get('response_time', 0):.2f}s)",
                operation_id=operation_id,
            )
        else:
            self.log_event(
                f"[VERIFICATION] FAILED for {operation_id}: {health.get('error', 'unknown')}",
                operation_id=operation_id,
            )
        return health

    async def run_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Executes a shell command via SSH.

        Args:
            command: Shell command to execute
            timeout: Command timeout in seconds

        Returns:
            {"stdout": str, "stderr": str, "exit_code": int}
        """
        try:
            from agent.tools.ssh_pure import exec_command_ssh_result

            result = await asyncio.to_thread(
                exec_command_ssh_result,
                HOST,
                PORT,
                USER,
                PASSWORD,
                command,
                KEY_PATH,
                timeout,
            )
            self.log_event(
                f"[SSH] Command executed: {command[:50]}... (exit: {result.get('exit_code', 'unknown')})"
            )
            return result
        except Exception as e:
            self.log_event(f"[SSH] Command failed: {str(e)}")
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
            }


from agent.tools.ssh_pure import (
    read_file_ssh,
    read_file_ssh_bytes,
    write_file_ssh,
    write_file_ssh_bytes,
    list_directory_ssh,
    exec_command_ssh,
    get_path_type_ssh,
    with_retry,
)

# Config from env (same vars as original tools.py)
HOST = os.getenv("SSH_HOST") or os.getenv("CYBERFOLKS_HOST", "")
PORT = int(os.getenv("SSH_PORT") or os.getenv("CYBERFOLKS_PORT") or 22)
USER = os.getenv("SSH_USER") or os.getenv("CYBERFOLKS_USER", "")
PASSWORD = os.getenv("SSH_PASSWORD", "")
KEY_PATH_RAW = os.getenv("SSH_KEY_PATH") or os.getenv("CYBERFOLKS_KEY_PATH", "") or None
KEY_PATH = KEY_PATH_RAW if KEY_PATH_RAW and os.path.exists(KEY_PATH_RAW) else None
BASE_PATH = os.getenv("BASE_PATH") or os.getenv("CYBERFOLKS_BASE_PATH", "/home/user/public_html")


def _config():
    return {
        "host": HOST,
        "port": PORT,
        "username": USER,
        "password": PASSWORD,
        "key_path": KEY_PATH if KEY_PATH and os.path.exists(KEY_PATH) else None,
    }


def get_path_type(path: str) -> str:
    """Check if path is file, directory, or not found. path is relative to BASE_PATH."""
    full_path = get_safe_path(BASE_PATH, path)
    return get_path_type_ssh(HOST, PORT, USER, PASSWORD, full_path, KEY_PATH)


@with_retry(max_attempts=3, delay=1.0, backoff=2.0)
def read_file(path: str) -> str:
    """Read file from server. Validates operation, then pure SSH read."""
    allowed, msg, _ = validate_operation(OperationType.READ, [path])
    if not allowed:
        raise PermissionError(msg)
    full_path = get_safe_path(BASE_PATH, path)
    path_type = get_path_type_ssh(HOST, PORT, USER, PASSWORD, full_path, KEY_PATH)
    if path_type == "directory":
        raise IsADirectoryError(
            f"'{path}' jest katalogiem, nie plikiem. Uzyj list_directory() aby wylistowac zawartosc."
        )
    if path_type == "not_found":
        raise FileNotFoundError(f"Plik nie istnieje: {path}")
    if path_type == "error":
        raise IOError(f"Nie mozna sprawdzic sciezki: {path}")
    content = read_file_ssh(HOST, PORT, USER, PASSWORD, full_path, KEY_PATH)
    log_event(EventType.FILES_READ, f"Odczyt: {path}", data={"path": path})
    return content


@with_retry(max_attempts=3, delay=1.0, backoff=2.0)
def write_file(
    path: str,
    content: str,
    operation_id: Optional[str] = None,
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> Optional[str]:
    """Write file to server with backup. Validates operation and content, then pure SSH write. PHP files get security check."""
    allowed, msg, _ = validate_operation(OperationType.WRITE, [path])
    if not allowed:
        raise PermissionError(msg)
    valid, msg = validate_content(content, path)
    if not valid:
        raise ValueError(msg)

    if path.endswith(".php"):
        log_event(
            EventType.FILE_WRITE,
            f"[SECURITY] Validating PHP code in {path}",
            operation_id=operation_id,
            task_id=task_id,
        )
        safety_result = check_wordpress_safety(content, path)
        if not safety_result.get("safe", True):
            error_msg = f"PHP Security validation failed: {safety_result.get('reason', 'unknown')}"
            log_error(error_msg, context={"chat_id": chat_id, "path": path}, operation_id=operation_id, task_id=task_id)
            raise SecurityError(error_msg)
        log_event(
            EventType.FILE_WRITE,
            f"[SECURITY] PHP validation passed for {path}",
            operation_id=operation_id,
            task_id=task_id,
        )

    full_path = get_safe_path(BASE_PATH, path)
    backup_path = f"{full_path}.backup.{int(time.time())}"
    try:
        current_content = read_file_ssh_bytes(HOST, PORT, USER, PASSWORD, full_path, KEY_PATH)
        write_file_ssh_bytes(HOST, PORT, USER, PASSWORD, backup_path, current_content, KEY_PATH)
        log_event(EventType.FILE_BACKUP, f"Backup: {path}", operation_id=operation_id, task_id=task_id)
    except FileNotFoundError:
        backup_path = None
    write_file_ssh(HOST, PORT, USER, PASSWORD, full_path, content, KEY_PATH)
    log_event(
        EventType.FILE_WRITE,
        f"Zapisano: {path}",
        data={"size": len(content)},
        operation_id=operation_id,
        task_id=task_id,
    )
    mark_file_written(path, backup_path, chat_id, source, task_id=task_id)
    return backup_path


@with_retry(max_attempts=2)
def exec_ssh_command(command: str) -> Tuple[bool, str, str]:
    """Execute command over SSH using env config."""
    return exec_command_ssh(HOST, PORT, USER, PASSWORD, command, KEY_PATH)


@with_retry(max_attempts=2)
def list_directory(path: str = "", recursive: bool = False) -> Tuple[bool, List[str], str]:
    """List directory. Returns (success, lines, error_message)."""
    if path:
        full_path = get_safe_path(BASE_PATH, path)
    else:
        full_path = BASE_PATH.rstrip("/")
    return list_directory_ssh(HOST, PORT, USER, PASSWORD, full_path, recursive=recursive, key_path=KEY_PATH)


@with_retry(max_attempts=3)
def list_files(pattern: str = "*", directory: str = "") -> List[str]:
    """List files on server matching pattern. Returns relative paths."""
    base = BASE_PATH
    if directory:
        base = f"{base.rstrip('/')}/{directory.lstrip('/')}"
    cmd = f"find {base} -name '{pattern}' -type f 2>/dev/null | head -100"
    success, stdout, _ = exec_command_ssh(HOST, PORT, USER, PASSWORD, cmd, KEY_PATH)
    files = stdout.strip().split("\n")
    relative = [
        f.replace(BASE_PATH.rstrip("/") + "/", "")
        for f in files
        if f and f.startswith(BASE_PATH)
    ]
    return [f for f in relative if f]


def file_exists(path: str) -> bool:
    """Check if file exists on server."""
    return get_path_type(path) == "file"


def directory_exists(path: str) -> bool:
    """Check if directory exists on server."""
    return get_path_type(path) == "directory"
