import threading
import time
from contextlib import contextmanager
from pathlib import Path

import filelock

from agent.state._config import LOCKS_DIR, SESSIONS_DIR, _log

_lock_holding: threading.local = threading.local()


def _get_holding() -> set:
    if not hasattr(_lock_holding, "keys"):
        _lock_holding.keys = set()
    return _lock_holding.keys


class LockError(Exception):
    pass


def get_session_filename(chat_id: str, source: str = "http") -> str:
    safe_chat_id = "".join(c for c in chat_id if c.isalnum() or c in "-_")
    return f"{safe_chat_id}.json"


def get_session_path(chat_id: str, source: str = "http") -> Path:
    return SESSIONS_DIR / get_session_filename(chat_id, source)


def get_lock_path(chat_id: str, source: str = "http") -> Path:
    return LOCKS_DIR / get_session_filename(chat_id, source).replace(".json", ".lock")


@contextmanager
def agent_lock(
    timeout: int = 30,
    chat_id: str = "default",
    source: str = "http",
):
    key = chat_id
    holding = _get_holding()
    if key in holding:
        yield
        return
    lock_file = get_lock_path(chat_id, source)
    lock = filelock.FileLock(lock_file, timeout=timeout)
    try:
        with lock.acquire(timeout=timeout):
            if lock_file.exists():
                mtime = lock_file.stat().st_mtime
                age = time.time() - mtime
                if age > 300:
                    _log.warning("Removing stale lock for %s (age: %.0fs)", chat_id, age)
                    lock_file.unlink()
            holding.add(key)
            try:
                yield
            finally:
                holding.discard(key)
    except filelock.Timeout:
        raise LockError(f"Could not acquire lock for {chat_id} within {timeout}s")
    finally:
        try:
            if lock_file.exists():
                lock_file.unlink()
        except Exception:
            pass


def is_locked(chat_id: str = "default", source: str = "http") -> bool:
    lock_file = get_lock_path(chat_id, source)
    if not lock_file.exists():
        return False
    mtime = lock_file.stat().st_mtime
    age = time.time() - mtime
    return age < 300


def force_unlock(chat_id: str = "default", source: str = "http") -> bool:
    lock_file = get_lock_path(chat_id, source)
    if lock_file.exists():
        try:
            lock_file.unlink()
            return True
        except Exception as e:
            _log.warning("Failed to force unlock: %s", e)
            return False
    return False
