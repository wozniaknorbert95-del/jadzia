"""
Pure SSH/SFTP I/O — no guardrails, state, or logging.
All connection params (host, port, username, password) are passed explicitly.
"""

import asyncio
import os
import stat
import time
from functools import wraps
from typing import Tuple, List, Optional, Callable, Dict, Any

from dotenv import load_dotenv


def with_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """Decorator adding retry with exponential backoff (sync)."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_error = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    if attempt == max_attempts:
                        raise
                    try:
                        from agent.log import log_event
                        log_event(
                            "retry",
                            f"[RETRY] Attempt {attempt}/{max_attempts} failed: {str(e)}. Retrying in {current_delay}s...",
                        )
                    except Exception:
                        pass
                    time.sleep(current_delay)
                    current_delay *= backoff
            raise last_error
        return wrapper
    return decorator


def async_with_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """Decorator adding retry with exponential backoff (async)."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            last_error = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    if attempt == max_attempts:
                        raise
                    try:
                        from agent.log import log_event
                        log_event(
                            "retry",
                            f"[RETRY] Attempt {attempt}/{max_attempts} failed: {str(e)}. Retrying in {current_delay}s...",
                        )
                    except Exception:
                        pass
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            raise last_error
        return wrapper
    return decorator


class ConnectionError(Exception):
    """Błąd połączenia z serwerem"""
    pass


class SSHConnection:
    """Context manager for SSH connection. All params passed explicitly (no env)."""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        key_path: Optional[str] = None,
        timeout: int = 30,
    ):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._key_path = key_path
        self._timeout = timeout
        self._ssh = None
        self._sftp = None

    def __enter__(self):
        import paramiko
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connect_kwargs = {
            "hostname": self._host,
            "port": self._port,
            "username": self._username,
            "timeout": self._timeout,
        }
        if self._key_path:
            connect_kwargs["key_filename"] = self._key_path
        if self._password:
            connect_kwargs["password"] = self._password
        if not connect_kwargs.get("key_filename") and not connect_kwargs.get("password"):
            raise ValueError("Provide key_path or password")
        self._ssh.connect(**connect_kwargs)
        self._sftp = self._ssh.open_sftp()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._sftp:
            try:
                self._sftp.close()
            except Exception:
                pass
        if self._ssh:
            try:
                self._ssh.close()
            except Exception:
                pass

    @property
    def sftp(self):
        return self._sftp

    @property
    def ssh(self):
        return self._ssh

    def exec_command(self, cmd: str, timeout: int = 30) -> Tuple[str, str]:
        stdin, stdout, stderr = self._ssh.exec_command(cmd, timeout=timeout)
        return stdout.read().decode("utf-8", errors="replace"), stderr.read().decode("utf-8", errors="replace")


def _conn_kwargs(host, port, username, password, key_path):
    return {"host": host, "port": port, "username": username, "password": password, "key_path": key_path}


def get_ssh_client(timeout: int = 30) -> Optional[Any]:
    """
    Create and return a connected paramiko.SSHClient using config from .env.
    Reads SSH_HOST, SSH_PORT, SSH_USER, SSH_KEY_PATH, SSH_PASSWORD (with CYBERFOLKS_* fallbacks).
    Returns None if config is missing, invalid, or connection fails.
    Caller is responsible for closing the client (client.close()).
    """
    load_dotenv()
    host = os.getenv("SSH_HOST") or os.getenv("CYBERFOLKS_HOST", "")
    port_raw = os.getenv("SSH_PORT") or os.getenv("CYBERFOLKS_PORT") or "22"
    user = os.getenv("SSH_USER") or os.getenv("CYBERFOLKS_USER", "")
    password = os.getenv("SSH_PASSWORD", "")
    key_path_raw = os.getenv("SSH_KEY_PATH") or os.getenv("CYBERFOLKS_KEY_PATH", "") or None
    key_path = key_path_raw if key_path_raw and os.path.exists(key_path_raw) else None

    if not host or not user:
        return None
    if not key_path and not password:
        return None
    try:
        port = int(port_raw)
    except (TypeError, ValueError):
        return None

    try:
        import paramiko
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connect_kwargs = {
            "hostname": host,
            "port": port,
            "username": user,
            "timeout": timeout,
        }
        if key_path:
            connect_kwargs["key_filename"] = key_path
        if password:
            connect_kwargs["password"] = password
        client.connect(**connect_kwargs)
        return client
    except Exception:
        return None


def read_file_ssh(
    host: str,
    port: int,
    username: str,
    password: str,
    path: str,
    key_path: Optional[str] = None,
) -> str:
    """Read file content from server as string. path = full path on server."""
    raw = read_file_ssh_bytes(host, port, username, password, path, key_path)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def read_file_ssh_bytes(
    host: str,
    port: int,
    username: str,
    password: str,
    path: str,
    key_path: Optional[str] = None,
) -> bytes:
    """Read file content from server as raw bytes. path = full path on server."""
    with SSHConnection(host, port, username, password, key_path) as conn:
        with conn.sftp.open(path, "r") as f:
            return f.read()


def write_file_ssh(
    host: str,
    port: int,
    username: str,
    password: str,
    path: str,
    content: str,
    key_path: Optional[str] = None,
) -> bool:
    """Write string content to file on server (UTF-8). path = full path. Returns True on success."""
    with SSHConnection(host, port, username, password, key_path) as conn:
        with conn.sftp.open(path, "w") as f:
            f.write(content.encode("utf-8"))
    return True


def write_file_ssh_bytes(
    host: str,
    port: int,
    username: str,
    password: str,
    path: str,
    content: bytes,
    key_path: Optional[str] = None,
) -> bool:
    """Write raw bytes to file on server. path = full path. Returns True on success."""
    with SSHConnection(host, port, username, password, key_path) as conn:
        with conn.sftp.open(path, "wb") as f:
            f.write(content)
    return True


def get_path_type_ssh(
    host: str,
    port: int,
    username: str,
    password: str,
    path: str,
    key_path: Optional[str] = None,
) -> str:
    """Returns 'file', 'directory', 'not_found', or 'error'. path = full path on server."""
    try:
        with SSHConnection(host, port, username, password, key_path) as conn:
            stat_result = conn.sftp.stat(path)
            if stat.S_ISDIR(stat_result.st_mode):
                return "directory"
            if stat.S_ISREG(stat_result.st_mode):
                return "file"
            return "other"
    except FileNotFoundError:
        return "not_found"
    except Exception:
        return "error"


def exec_command_ssh(
    host: str,
    port: int,
    username: str,
    password: str,
    command: str,
    key_path: Optional[str] = None,
) -> Tuple[bool, str, str]:
    """Execute command over SSH. Returns (success, stdout, stderr)."""
    try:
        with SSHConnection(host, port, username, password, key_path) as conn:
            stdout, stderr = conn.exec_command(command)
            success = len(stderr.strip()) == 0 or len(stdout.strip()) > 0
            return success, stdout, stderr
    except Exception as e:
        return False, "", str(e)


def exec_command_ssh_result(
    host: str,
    port: int,
    username: str,
    password: str,
    command: str,
    key_path: Optional[str] = None,
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Execute command over SSH. Returns dict with stdout, stderr, exit_code.
    """
    try:
        with SSHConnection(host, port, username, password, key_path, timeout=timeout) as conn:
            stdin, stdout, stderr = conn._ssh.exec_command(command, timeout=timeout)
            stdout_text = stdout.read().decode("utf-8", errors="replace")
            stderr_text = stderr.read().decode("utf-8", errors="replace")
            exit_code = stdout.channel.recv_exit_status()
            return {
                "stdout": stdout_text,
                "stderr": stderr_text,
                "exit_code": exit_code,
            }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1,
        }


@with_retry(max_attempts=2)
def list_directory_ssh(
    host: str,
    port: int,
    username: str,
    password: str,
    path: str,
    recursive: bool = False,
    key_path: Optional[str] = None,
) -> Tuple[bool, List[str], str]:
    """
    List directory on server. path = full path on server.
    Returns (success, lines, error_message). Lines are ls -la output or find output.
    """
    try:
        with SSHConnection(host, port, username, password, key_path) as conn:
            if recursive:
                cmd = f"find {path} -type f 2>/dev/null | head -100"
            else:
                cmd = f"ls -la {path} 2>/dev/null"
            stdout, stderr = conn.exec_command(cmd)
            if stderr.strip() and not stdout.strip():
                return False, [], stderr.strip()
            lines = [l.strip() for l in stdout.strip().split("\n") if l.strip()]
            return True, lines, ""
    except Exception as e:
        return False, [], str(e)
