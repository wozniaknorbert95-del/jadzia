"""
State Management - Session-Scoped Edition
==========================================

CHANGES FROM ORIGINAL:
- Session-scoped state files: data/sessions/{source}_{chat_id}.json
- Per-session locks: data/sessions/.locks/{source}_{chat_id}.lock
- Automatic migration from global state to first HTTP session
- Backward compatible API (added chat_id + source params)

MIGRATION STRATEGY:
1. First call to load_state() checks if old data/.agent_state.json exists
2. If yes → moves it to data/sessions/http_default.json
3. Creates migration marker: data/.migrated
"""

import json
import logging
import os
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Optional, Tuple
import uuid
import filelock

from agent.db import (
    db_create_or_update_session,
    db_create_task,
    db_update_task,
    db_set_active_task,
    db_update_task_queue,
    db_find_session_by_task_id,
    db_get_awaiting_approval_task,
    db_delete_session,
    db_list_all_sessions,
    db_list_sessions_updated_before,
    db_get_session,
    db_get_tasks_for_session,
)
from agent.log import log_event

# Phase 4: SQLite read switch
USE_SQLITE_STATE = os.getenv("USE_SQLITE_STATE", "0") == "1"

_log = logging.getLogger("agent.state")


# ═══════════════════════════════════════════════════════════════
# PATHS & CONFIGURATION
# ═══════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
SESSIONS_DIR = DATA_DIR / "sessions"
LOCKS_DIR = SESSIONS_DIR / ".locks"
BACKUPS_DIR = DATA_DIR / "backups"

# Legacy paths (for migration)
LEGACY_STATE_FILE = DATA_DIR / ".agent_state.json"
LEGACY_LOCK_FILE = DATA_DIR / ".agent.lock"
MIGRATION_MARKER = DATA_DIR / ".migrated"

# Ensure directories exist
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
LOCKS_DIR.mkdir(parents=True, exist_ok=True)
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)


def _check_invariants(state: dict, chat_id: str, source: str) -> None:
    """
    Validate state invariants before save. Logs warnings on violation
    and auto-repairs safe-to-fix issues (orphan queue entries, ghost active_task_id).
    """
    if not state or not _is_new_format(state):
        return
    tasks = state.get("tasks") or {}
    active_id = state.get("active_task_id")
    queue = state.get("task_queue") or []

    # INV-1: active_task_id must be empty or point to an existing task
    if active_id and active_id not in tasks:
        print(
            f"[INVARIANT] {source}/{chat_id}: active_task_id={active_id} "
            f"not in tasks (ghost). Auto-clearing."
        )
        state["active_task_id"] = None

    # INV-2: every task_id in task_queue must exist in tasks
    valid_queue = [tid for tid in queue if tid in tasks]
    if len(valid_queue) != len(queue):
        removed = set(queue) - set(valid_queue)
        print(
            f"[INVARIANT] {source}/{chat_id}: task_queue contained orphan ids "
            f"{removed}. Auto-removed."
        )
        state["task_queue"] = valid_queue

    # INV-3: terminal statuses should not be overwritten (log-only; enforcement in update_operation_status)
    # (checked at write-time in update_operation_status, not here)


def _prepare_db_task(task_id: str, task_data: dict, chat_id: str, source: str) -> dict:
    """Prepare task dict for DB from in-memory task_data."""
    return {
        "task_id": task_id,
        "chat_id": chat_id,
        "source": source,
        "operation_id": task_data.get("operation_id", task_data.get("id", "")),
        "status": task_data.get("status", "unknown"),
        "user_input": task_data.get("user_input"),
        "dry_run": task_data.get("dry_run", False),
        "test_mode": task_data.get("test_mode", False),
        "webhook_url": task_data.get("webhook_url"),
        "created_at": task_data.get("created_at"),
        "plan": task_data.get("plan"),
        "diffs": task_data.get("diffs"),
        "new_contents": task_data.get("new_contents"),
        "written_files": task_data.get("written_files"),
        "errors": task_data.get("errors", []),
        "pending_plan": task_data.get("pending_plan"),
        "validation_errors": task_data.get("validation_errors"),
        "retry_count": task_data.get("retry_count", 0),
        "deploy_result": task_data.get("deploy_result"),
        "awaiting_response": task_data.get("awaiting_response", False),
        "awaiting_type": task_data.get("awaiting_type"),
        "pending_plan_with_questions": task_data.get("pending_plan_with_questions"),
        "last_response": task_data.get("last_response"),
        "files_to_modify": task_data.get("files_to_modify"),
        "completed_at": task_data.get("completed_at"),
    }


def _sync_to_sqlite(chat_id: str, source: str, state: dict) -> None:
    """
    Synchronize state to SQLite atomically in a single transaction (session + tasks).
    Retries on 'database is locked'. Raises on failure so caller can propagate 500.
    Ensures readers never see active_task_id set without the corresponding task row updated.
    """
    from agent.db import (
        db_transaction_with_retry,
        _exec_create_or_update_session,
        _exec_set_active_task,
        _exec_update_task_queue,
        _exec_create_task,
        _exec_update_task,
    )

    try:
        tasks = state.get("tasks", {})
        task_queue = state.get("task_queue", [])
        active_task_id = state.get("active_task_id")

        def _sync_session_and_tasks(conn):
            _exec_create_or_update_session(conn, chat_id, source)
            _exec_set_active_task(conn, chat_id, source, active_task_id)
            _exec_update_task_queue(conn, chat_id, source, task_queue)
            for task_id, task_data in tasks.items():
                db_task = _prepare_db_task(task_id, task_data, chat_id, source)
                try:
                    _exec_create_task(conn, db_task)
                except sqlite3.IntegrityError:
                    _exec_update_task(conn, task_id, db_task)

        db_transaction_with_retry()(_sync_session_and_tasks)

        log_event("sqlite_sync", f"[SQLITE] State synced for {chat_id} ({source}): {len(tasks)} tasks")

    except Exception as e:
        log_event("sqlite_error", f"[SQLITE] Sync failed for {chat_id}: {e}")
        raise


# ═══════════════════════════════════════════════════════════════
# SESSION PATH MANAGEMENT
# ═══════════════════════════════════════════════════════════════

def get_session_filename(chat_id: str, source: str = "http") -> str:
    """
    Generate session-specific filename. One file per chat_id (source ignored for path).
    """
    # Sanitize chat_id (remove path separators, special chars)
    safe_chat_id = "".join(c for c in chat_id if c.isalnum() or c in "-_")
    return f"{safe_chat_id}.json"


def get_session_path(chat_id: str, source: str = "http") -> Path:
    """Get full path to session state file"""
    filename = get_session_filename(chat_id, source)
    return SESSIONS_DIR / filename


def get_lock_path(chat_id: str, source: str = "http") -> Path:
    """Get full path to session lock file (one lock per chat_id)."""
    filename = get_session_filename(chat_id, source).replace(".json", ".lock")
    return LOCKS_DIR / filename


# ═══════════════════════════════════════════════════════════════
# MIGRATION FROM GLOBAL STATE
# ═══════════════════════════════════════════════════════════════

def migrate_legacy_state() -> None:
    """
    One-time migration from global state to session-scoped state.
    Phase 5: Migrates directly to SQLite (no JSON write). Legacy file is renamed to .migrated.
    """
    if MIGRATION_MARKER.exists():
        return  # Already migrated

    if LEGACY_STATE_FILE.exists():
        try:
            with open(LEGACY_STATE_FILE, 'r', encoding='utf-8') as f:
                legacy_state = json.load(f)
            if not _is_new_format(legacy_state):
                legacy_state = migrate_state_to_multitask(legacy_state)
            _sync_to_sqlite("default", "http", legacy_state)
            backup_path = LEGACY_STATE_FILE.with_suffix('.json.migrated')
            LEGACY_STATE_FILE.rename(backup_path)
            print("✅ Migrated legacy state to SQLite (http/default)")
        except Exception as e:
            print(f"⚠️ Migration failed: {e}")
    MIGRATION_MARKER.touch()


# Run migration check on module import
migrate_legacy_state()


# ═══════════════════════════════════════════════════════════════
# OPERATION STATUS (unchanged)
# ═══════════════════════════════════════════════════════════════

class OperationStatus:
    """Stałe statusy operacji"""
    PLANNING = "planning"
    READING_FILES = "reading_files"
    GENERATING_CODE = "generating_code"
    DIFF_READY = "diff_ready"
    APPROVED = "approved"
    WRITING_FILES = "writing_files"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


TERMINAL_STATUSES = (OperationStatus.COMPLETED, OperationStatus.FAILED, OperationStatus.ROLLED_BACK)


# ═══════════════════════════════════════════════════════════════
# MULTI-TASK: migration and format helpers
# ═══════════════════════════════════════════════════════════════

def _is_new_format(state: dict) -> bool:
    """True if state uses tasks dict + active_task_id + task_queue."""
    return state is not None and "tasks" in state


def migrate_state_to_multitask(state: dict) -> dict:
    """
    Convert old flat state to new multi-task structure (in memory).
    Caller must save_state if persistence is desired.
    """
    if _is_new_format(state):
        return state
    task_id = state.get("task_id") or str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    task_payload = {
        "id": state.get("id", f"op_{int(time.time())}"),
        "operation_id": state.get("id", f"op_{int(time.time())}"),
        "status": state.get("status", OperationStatus.PLANNING),
        "pending_plan": state.get("pending_plan"),
        "user_input": state.get("user_input", ""),
        "created_at": state.get("created_at", now),
        "updated_at": state.get("updated_at", now),
        "plan": state.get("plan"),
        "files_to_modify": state.get("files_to_modify", []),
        "diffs": state.get("diffs", {}),
        "new_contents": state.get("new_contents", {}),
        "written_files": state.get("written_files", {}),
        "errors": state.get("errors", []),
        "awaiting_response": state.get("awaiting_response", False),
        "awaiting_type": state.get("awaiting_type"),
        "pending_plan_with_questions": state.get("pending_plan_with_questions"),
        "last_response": state.get("last_response"),
    }
    return {
        "chat_id": state.get("chat_id", "default"),
        "source": state.get("source", "http"),
        "tasks": {task_id: task_payload},
        "active_task_id": task_id,
        "task_queue": [],
    }


# ═══════════════════════════════════════════════════════════════
# CORE STATE OPERATIONS (refactored with session support)
# save_state: must be called only while holding agent_lock (Option B)
# ═══════════════════════════════════════════════════════════════

def save_state(state: dict, chat_id: str = "default", source: str = "http") -> None:
    """
    Save state to SQLite (Phase 5: sole source of truth).
    MUST be called only while holding agent_lock(chat_id=..., source=...).
    """
    # Auto-repair invariants before persisting
    _check_invariants(state, chat_id, source)
    try:
        _sync_to_sqlite(chat_id, source, state)
        log_event("state_save", f"[STATE] Saved state for {chat_id} ({source})")
    except Exception as e:
        log_event("state_error", f"[STATE] Save failed for {chat_id} ({source}): {e}")
        raise RuntimeError(f"Failed to save state for {source}_{chat_id}: {e}")


def _load_state_from_sqlite(chat_id: str, source: str = "http") -> Optional[dict]:
    """
    Load state from SQLite database.
    Returns dict in same format as JSON load_state() for compatibility.
    Multi-task format: {"tasks": {}, "active_task_id": "", "task_queue": []}
    Recovery: if session has no active_task_id but has non-terminal tasks, set active_task_id to first such task.
    """
    from agent.db import db_get_session, db_get_tasks_for_session

    try:
        session = db_get_session(chat_id, source)
        if not session:
            _log.debug("[SQLITE] Looking for session chat_id=%s source=%s ... Found: None", chat_id, source)
            return None

        tasks = db_get_tasks_for_session(chat_id, source)
        active_task_id = session.get("active_task_id") or ""

        state = {
            "tasks": {},
            "active_task_id": active_task_id,
            "task_queue": session.get("task_queue", []),
        }

        for task in tasks:
            task_id = task["task_id"]
            state["tasks"][task_id] = {**task, "id": task["operation_id"]}

        # Recovery: session has non-empty queue but no active_task_id — set from queue (do not recover from
        # "first non-terminal task" when queue is empty, that could undo a ghost clear)
        if not active_task_id and state["tasks"]:
            queue = state.get("task_queue") or []
            candidate = queue[0] if queue else None
            if candidate:
                db_set_active_task(chat_id, source, candidate)
                state["active_task_id"] = candidate
                active_task_id = candidate
                _log.debug("[SQLITE] Recovery: set active_task_id=%s for %s/%s", candidate, source, chat_id)

        _log.debug(
            "[SQLITE] Loaded state chat_id=%s source=%s tasks=%s active_task_id=%s",
            chat_id, source, len(state["tasks"]), active_task_id or "None",
        )
        log_event("sqlite_read", f"[SQLITE] Loaded state for {chat_id}/{source}: {len(state['tasks'])} tasks")
        return state

    except Exception as e:
        log_event("sqlite_error", f"[SQLITE] Error loading state: {e}")
        return None


def load_state(chat_id: str = "default", source: str = "http") -> Optional[dict]:
    """
    Load session state.
    Phase 5: Always try SQLite first (so server works with or without USE_SQLITE_STATE=1),
    then fall back to JSON for rollback compatibility.
    """
    try:
        state = _load_state_from_sqlite(chat_id, source)
        if state:
            return state
        # First load for this chat_id: create session row so later load_state never returns None
        db_create_or_update_session(chat_id, source)
        state = _load_state_from_sqlite(chat_id, source)
        if state:
            return state
        if USE_SQLITE_STATE:
            log_event("sqlite_read", "[SQLITE] No session found, falling back to JSON")
    except Exception as e:
        log_event("sqlite_error", f"[SQLITE] Read failed, falling back to JSON: {e}")

    state_file = get_session_path(chat_id, source)
    if not state_file.exists():
        return None
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
    except Exception as e:
        print(f"⚠️ [chat_id={chat_id}] Error loading state for {source}_{chat_id}: {e}")
        return None
    if state and not _is_new_format(state):
        state = migrate_state_to_multitask(state)
    return state


def clear_state(chat_id: str = "default", source: str = "http") -> None:
    """Clear session state (SQLite and optionally leftover JSON file). Uses FileLock. Phase 5: always clear SQLite."""
    try:
        with agent_lock(chat_id=chat_id, source=source):
            try:
                db_delete_session(chat_id, source)
            except Exception as e:
                print(f"⚠️ [chat_id={chat_id}] Error clearing SQLite state for {source}_{chat_id}: {e}")
            state_file = get_session_path(chat_id, source)
            if state_file.exists():
                try:
                    state_file.unlink()
                except Exception as e:
                    print(f"⚠️ [chat_id={chat_id}] Error clearing state file for {source}_{chat_id}: {e}")
    except LockError:
        raise


def archive_state(chat_id: str = "default", source: str = "http") -> None:
    """Archive current state to backups directory. Uses FileLock for consistent read."""
    try:
        with agent_lock(chat_id=chat_id, source=source):
            state = load_state(chat_id, source)
            if not state:
                return
            aid = state.get("active_task_id") or state.get("task_id")
            task_payload = (state.get("tasks") or {}).get(aid) if _is_new_format(state) else state
            operation_id = (task_payload or {}).get("id", "unknown")
            archive_dir = BACKUPS_DIR / operation_id
            archive_dir.mkdir(parents=True, exist_ok=True)
            archive_file = archive_dir / f"state_{source}_{chat_id}.json"
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
    except LockError:
        raise
    except Exception as e:
        print(f"⚠️ Error archiving state: {e}")


def has_pending_operation(
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> bool:
    """Check if task (active if task_id None) has pending operation."""
    state = load_state(chat_id, source)
    if not state:
        return False
    tid = _resolve_task_id(chat_id, source, task_id)
    target = _get_task_payload(state, tid, chat_id, source) or (state if not _is_new_format(state) else None)
    return target.get("awaiting_response", False) if target else False


def get_pending_operation_summary(
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> Optional[str]:
    """Get summary of pending operation for task (active if task_id None)."""
    state = load_state(chat_id, source)
    if not state:
        return None
    tid = _resolve_task_id(chat_id, source, task_id)
    target = _get_task_payload(state, tid, chat_id, source) or (state if not _is_new_format(state) else None)
    if not target or not target.get("awaiting_response"):
        return None
    return f"Operation {target.get('id', 'unknown')} | Status: {target.get('status', 'unknown')} | Awaiting: {target.get('awaiting_type', 'unknown')}"


# ═══════════════════════════════════════════════════════════════
# LOCK MANAGEMENT (session-scoped)
# ═══════════════════════════════════════════════════════════════

class LockError(Exception):
    """Raised when lock cannot be acquired"""
    pass


# Reentrant lock: same thread can acquire same session lock again (e.g. create_operation from route_user_input).
_agent_lock_holding: threading.local = threading.local()


def _get_holding() -> set:
    if not hasattr(_agent_lock_holding, "keys"):
        _agent_lock_holding.keys = set()
    return _agent_lock_holding.keys


@contextmanager
def agent_lock(
    timeout: int = 30,
    chat_id: str = "default",
    source: str = "http"
):
    """
    Session-scoped lock context manager (reentrant: same thread can re-enter).
    Lock is per chat_id (source ignored) so one session per chat_id.
    """
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
                    print(f"⚠️ Removing stale lock for {chat_id} (age: {age:.0f}s)")
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
    """
    Check if session is currently locked.
    
    Args:
        chat_id: Session identifier
        source: 'http' or 'telegram'
    
    Returns:
        True if lock file exists and is fresh (<5 min)
    """
    lock_file = get_lock_path(chat_id, source)
    
    if not lock_file.exists():
        return False
    
    # Check if lock is stale
    mtime = lock_file.stat().st_mtime
    age = time.time() - mtime
    
    return age < 300  # Fresh if younger than 5 minutes


def force_unlock(chat_id: str = "default", source: str = "http") -> bool:
    """
    Force remove lock file (emergency use only).
    
    Args:
        chat_id: Session identifier
        source: 'http' or 'telegram'
    
    Returns:
        True if lock was removed
    """
    lock_file = get_lock_path(chat_id, source)
    
    if lock_file.exists():
        try:
            lock_file.unlink()
            return True
        except Exception as e:
            print(f"⚠️ Failed to force unlock: {e}")
            return False
    
    return False


# ═══════════════════════════════════════════════════════════════
# MULTI-TASK: task lookup and queue (all writers use FileLock)
# ═══════════════════════════════════════════════════════════════

def get_active_task_id(chat_id: str = "default", source: str = "http") -> Optional[str]:
    """
    Return active_task_id (new format) or task_id (legacy), or None.
    If active_task_id is set but the task is not in state['tasks'] (ghost),
    clears the ghost in DB and returns None so callers don't get 404 on submit.
    """
    state = load_state(chat_id, source)
    if not state:
        print(f"[get_active_task_id] Looking for task for user chat_id={chat_id} source={source} status=active ... Found: None (no state)")
        return None
    if _is_new_format(state):
        active_id = state.get("active_task_id")
        tasks = state.get("tasks") or {}
        if active_id and active_id not in tasks:
            # Ghost: session has active_task_id but task not in tasks (e.g. never synced or deleted)
            try:
                from agent.db import db_find_session_by_task_id, db_set_active_task
                if db_find_session_by_task_id(active_id) is None:
                    db_set_active_task(chat_id, source, None)
                    print(f"[get_active_task_id] ghost active_task_id={active_id} cleared for {source}/{chat_id}")
            except Exception as e:
                log_event("sqlite_error", f"get_active_task_id clear ghost failed: {e}")
            print(f"[get_active_task_id] Looking for task for user chat_id={chat_id} source={source} status=active ... Found: None (ghost cleared)")
            return None
        print(f"[get_active_task_id] Looking for task for user chat_id={chat_id} source={source} status=active ... Found: {active_id or 'None'}")
        return active_id
    result = state.get("task_id")
    print(f"[get_active_task_id] Looking for task for user chat_id={chat_id} source={source} status=active ... Found: {result or 'None'} (legacy)")
    return result


def get_awaiting_approval_task_id(chat_id: str, source: str = "http") -> Optional[str]:
    """
    Return task_id for the task in this session that is awaiting approval
    (status=diff_ready, awaiting_response=True). Used as fallback for Telegram "TAK" flow.
    """
    task = db_get_awaiting_approval_task(chat_id, source)
    task_id = task["task_id"] if task else None
    print(f"[get_awaiting_approval_task_id] Looking for task for user chat_id={chat_id} source={source} status=awaiting_approval ... Found: {task_id or 'None'}")
    return task_id


def find_task_by_id(
    chat_id: str, task_id: str, source: str = "http"
) -> Optional[dict]:
    """
    Return task payload for task_id, or None.
    Logs task_id on lookup.
    """
    state = load_state(chat_id, source)
    if not state:
        print(f"[find_task_by_id] Looking for task_id={task_id} chat_id={chat_id} source={source} ... Found: False (no state)")
        return None
    if _is_new_format(state) and task_id in state.get("tasks", {}):
        print(f"[find_task_by_id] Looking for task_id={task_id} chat_id={chat_id} source={source} ... Found: True")
        return state["tasks"][task_id]
    if not _is_new_format(state) and state.get("task_id") == task_id:
        print(f"[find_task_by_id] Looking for task_id={task_id} chat_id={chat_id} source={source} ... Found: True (legacy)")
        return state
    print(f"[find_task_by_id] Looking for task_id={task_id} chat_id={chat_id} source={source} ... Found: False")
    return None


def is_dry_run(chat_id: str, task_id: str, source: str = "http") -> bool:
    """Check if task is in dry-run mode."""
    state = load_state(chat_id, source)
    task = state.get("tasks", {}).get(task_id, {}) if state else {}
    return task.get("dry_run", False)


def is_test_mode(chat_id: str, task_id: str, source: str = "http") -> bool:
    """Check if task is in test_mode."""
    state = load_state(chat_id, source)
    task = state.get("tasks", {}).get(task_id, {}) if state else {}
    return task.get("test_mode", False)


def add_task_to_queue(
    chat_id: str,
    task_id: str,
    instruction: str,
    source: str = "http",
    dry_run: bool = False,
    webhook_url: Optional[str] = None,
    test_mode: bool = False,
) -> int:
    """
    Append task to queue under lock. Creates minimal task entry.
    Returns position_in_queue (1-based: 1 = first in queue).
    """
    try:
        with agent_lock(chat_id=chat_id, source=source):
            state = load_state(chat_id, source)
            if not state:
                state = {
                    "chat_id": chat_id,
                    "source": source,
                    "tasks": {},
                    "active_task_id": None,
                    "task_queue": [],
                }
            if not _is_new_format(state):
                state = migrate_state_to_multitask(state)
            now = datetime.now(timezone.utc).isoformat()
            op_id = f"op_{int(time.time())}_{task_id[:8]}"
            state["tasks"][task_id] = {
                "id": op_id,
                "operation_id": op_id,
                "status": "queued",
                "user_input": instruction,
                "created_at": now,
                "updated_at": now,
                "awaiting_response": False,
                "awaiting_type": None,
                "dry_run": dry_run,
                "test_mode": test_mode,
                "webhook_url": webhook_url,
            }
            state.setdefault("task_queue", []).append(task_id)
            save_state(state, chat_id, source)
            pos = len(state["task_queue"])
            print(f"[task_id={task_id}] add_task_to_queue chat_id={chat_id} position_in_queue={pos}")
            return pos
    except LockError:
        raise


def get_next_task_from_queue(chat_id: str, source: str = "http") -> Optional[str]:
    """
    Pop first task from queue, set as active_task_id, save. Returns task_id or None.
    """
    try:
        with agent_lock(chat_id=chat_id, source=source):
            state = load_state(chat_id, source)
            if not state or not _is_new_format(state):
                return None
            queue = state.get("task_queue") or []
            if not queue:
                return None
            task_id = queue.pop(0)
            state["task_queue"] = queue
            state["active_task_id"] = task_id
            save_state(state, chat_id, source)
            print(f"[task_id={task_id}] get_next_task_from_queue chat_id={chat_id}")
            return task_id
    except LockError:
        raise


def mark_task_completed(chat_id: str, task_id: str, source: str = "http") -> Optional[str]:
    """
    Finalize task, clear active_task_id, pop next from queue and set active.
    Does NOT overwrite terminal statuses (FAILED/ROLLED_BACK → keeps them).
    Returns next task_id if any, else None.
    """
    try:
        with agent_lock(chat_id=chat_id, source=source):
            state = load_state(chat_id, source)
            if not state or not _is_new_format(state):
                return None
            prev_status = "?"
            if task_id in state.get("tasks", {}):
                prev_status = state["tasks"][task_id].get("status", "")
                # Don't overwrite terminal statuses — only mark COMPLETED if non-terminal
                if prev_status not in TERMINAL_STATUSES:
                    state["tasks"][task_id]["status"] = OperationStatus.COMPLETED
                state["tasks"][task_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
            state["active_task_id"] = None
            queue = state.get("task_queue") or []
            next_task_id = None
            if queue:
                next_task_id = queue.pop(0)
                state["task_queue"] = queue
                state["active_task_id"] = next_task_id
            save_state(state, chat_id, source)
            print(f"[task_id={task_id}] mark_task_completed chat_id={chat_id} prev_status={prev_status} next_task_id={next_task_id}")
            return next_task_id
    except LockError:
        raise


def clear_active_task_and_advance(chat_id: str, source: str = "http") -> Optional[str]:
    """
    Clear active_task_id (ghost cleanup) and advance queue to next task.
    Does NOT touch any task status — purely queue management.
    Returns next task_id if any, else None.
    """
    try:
        with agent_lock(chat_id=chat_id, source=source):
            state = load_state(chat_id, source)
            if not state or not _is_new_format(state):
                return None
            old_active = state.get("active_task_id")
            state["active_task_id"] = None
            queue = state.get("task_queue") or []
            next_task_id = None
            if queue:
                next_task_id = queue.pop(0)
                state["task_queue"] = queue
                state["active_task_id"] = next_task_id
            save_state(state, chat_id, source)
            print(f"[clear_active_task_and_advance] {source}/{chat_id}: cleared ghost active_id={old_active} => next_task_id={next_task_id}")
            return next_task_id or None
    except LockError:
        raise


def _resolve_task_id(
    chat_id: str, source: str, task_id: Optional[str]
) -> Optional[str]:
    """Resolve task_id: if given use it, else active task."""
    if task_id:
        return task_id
    return get_active_task_id(chat_id, source)


def _get_task_payload(state: dict, task_id: Optional[str], chat_id: str, source: str) -> Optional[dict]:
    """Return the dict to read/write for this task (task payload or legacy state)."""
    if not task_id:
        task_id = get_active_task_id(chat_id, source)
    if not task_id:
        return None
    if _is_new_format(state) and task_id in state.get("tasks", {}):
        return state["tasks"][task_id]
    if not _is_new_format(state) and state.get("task_id") == task_id:
        return state
    return None


# ═══════════════════════════════════════════════════════════════
# STATE MANIPULATION HELPERS (session-aware, with FileLock and task_id)
# ═══════════════════════════════════════════════════════════════

def create_operation(
    user_input: str,
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
    dry_run: bool = False,
    test_mode: bool = False,
    webhook_url: Optional[str] = None,
) -> dict:
    """
    Create new operation state (one task, set as active). Uses FileLock.
    If task_id is None, generates one. Always writes new multi-task format.
    """
    task_id = task_id or str(uuid.uuid4())
    operation_id = f"op_{int(time.time())}"
    now = datetime.now(timezone.utc).isoformat()
    task_payload = {
        "id": operation_id,
        "operation_id": operation_id,
        "status": OperationStatus.PLANNING,
        "pending_plan": None,
        "user_input": user_input,
        "created_at": now,
        "updated_at": now,
        "plan": None,
        "files_to_modify": [],
        "diffs": {},
        "new_contents": {},
        "written_files": {},
        "errors": [],
        "awaiting_response": False,
        "awaiting_type": None,
        "dry_run": dry_run,
        "test_mode": test_mode,
        "webhook_url": webhook_url,
    }
    try:
        with agent_lock(chat_id=chat_id, source=source):
            state = load_state(chat_id, source)
            if not state:
                state = {"chat_id": chat_id, "source": source, "tasks": {}, "active_task_id": None, "task_queue": []}
            elif not _is_new_format(state):
                state = migrate_state_to_multitask(state)
            state["tasks"][task_id] = task_payload
            state["active_task_id"] = task_id
            state.setdefault("task_queue", [])
            save_state(state, chat_id, source)
            print(f"[task_id={task_id}] create_operation chat_id={chat_id}")
    except LockError:
        raise
    return {"id": operation_id, "task_id": task_id, **task_payload}


def update_operation_status(
    status: str,
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
    **kwargs
) -> dict:
    """Update operation status (and optional task_id). Uses FileLock. Logs task_id."""
    tid = _resolve_task_id(chat_id, source, task_id)
    try:
        with agent_lock(chat_id=chat_id, source=source):
            state = load_state(chat_id, source)
            if not state:
                # Defensive: ensure session exists and retry (e.g. DB temporarily unavailable)
                try:
                    db_create_or_update_session(chat_id, source)
                    state = load_state(chat_id, source)
                except Exception:
                    pass
            if not state:
                raise RuntimeError(f"No state found for {source}_{chat_id}")
            target = _get_task_payload(state, tid, chat_id, source)
            if target is None and not _is_new_format(state):
                target = state
            if target is not None:
                prev_status = target.get("status", "unknown")
                # Guard: never overwrite terminal statuses with non-terminal ones
                if prev_status in TERMINAL_STATUSES and status not in TERMINAL_STATUSES:
                    print(
                        f"[STATUS_GUARD] task_id={tid} rejecting {prev_status} → {status} "
                        f"(terminal status protected)"
                    )
                    save_state(state, chat_id, source)
                    return state
                target["status"] = status
                target["updated_at"] = datetime.now(timezone.utc).isoformat()
                for key, value in kwargs.items():
                    target[key] = value
                # Diagnostic log when setting FAILED — high-value context for debugging
                if status == OperationStatus.FAILED:
                    print(
                        f"[FAILED_SET] task_id={tid} chat_id={chat_id} source={source} "
                        f"prev_status={prev_status} "
                        f"created_at={target.get('created_at', '?')} "
                        f"updated_at={target.get('updated_at', '?')} "
                        f"awaiting_response={target.get('awaiting_response', '?')}"
                    )
            save_state(state, chat_id, source)
            if tid:
                print(f"[task_id={tid}] update_operation_status status={status}")
    except LockError:
        raise
    return state


def add_error(
    error: str,
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> None:
    """Add error to operation state. Uses FileLock."""
    tid = _resolve_task_id(chat_id, source, task_id)
    try:
        with agent_lock(chat_id=chat_id, source=source):
            state = load_state(chat_id, source)
            if not state:
                return
            target = _get_task_payload(state, tid, chat_id, source) or (state if not _is_new_format(state) else None)
            if target:
                errors_list = target.get("errors")
                if errors_list is None or not isinstance(errors_list, list):
                    errors_list = []
                    target["errors"] = errors_list
                errors_list.append({"timestamp": datetime.now(timezone.utc).isoformat(), "message": error})
                save_state(state, chat_id, source)
                if tid:
                    print(f"[task_id={tid}] add_error")
    except LockError:
        raise


def mark_file_written(
    path: str,
    backup_path: Optional[str] = None,
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> None:
    """Mark file as successfully written. Uses FileLock."""
    tid = _resolve_task_id(chat_id, source, task_id)
    try:
        with agent_lock(chat_id=chat_id, source=source):
            state = load_state(chat_id, source)
            if not state:
                return
            target = _get_task_payload(state, tid, chat_id, source) or (state if not _is_new_format(state) else None)
            if target:
                written = target.get("written_files")
                if written is None or not isinstance(written, dict):
                    written = {}
                    target["written_files"] = written
                written[path] = {"timestamp": datetime.now(timezone.utc).isoformat(), "backup_path": backup_path}
                save_state(state, chat_id, source)
    except LockError:
        raise


def get_backups(
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> Dict[str, str]:
    """Get backup paths for written files (active task or legacy)."""
    state = load_state(chat_id, source)
    if not state:
        return {}
    tid = _resolve_task_id(chat_id, source, task_id)
    target = _get_task_payload(state, tid, chat_id, source) or (state if not _is_new_format(state) else None)
    written = target.get("written_files") if target else None
    if not written or not isinstance(written, dict):
        return {}
    return {path: info.get("backup_path") for path, info in written.items() if isinstance(info, dict) and info.get("backup_path")}


def set_awaiting_response(
    awaiting: bool,
    response_type: Optional[str] = None,
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> None:
    """Set awaiting_response flag. Uses FileLock."""
    tid = _resolve_task_id(chat_id, source, task_id)
    try:
        with agent_lock(chat_id=chat_id, source=source):
            state = load_state(chat_id, source)
            if not state:
                return
            target = _get_task_payload(state, tid, chat_id, source) or (state if not _is_new_format(state) else None)
            if target:
                target["awaiting_response"] = awaiting
                target["awaiting_type"] = response_type
                save_state(state, chat_id, source)
                if tid:
                    print(f"[task_id={tid}] set_awaiting_response awaiting={awaiting}")
    except LockError:
        raise


def get_operation_id(
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> Optional[str]:
    """Get operation ID for task (active if task_id None)."""
    state = load_state(chat_id, source)
    if not state:
        return None
    tid = _resolve_task_id(chat_id, source, task_id)
    target = _get_task_payload(state, tid, chat_id, source) or (state if not _is_new_format(state) else None)
    return target.get("id") if target else None


def get_current_status(
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> Optional[str]:
    """Get current operation status for task (active if task_id None)."""
    state = load_state(chat_id, source)
    if not state:
        return None
    tid = _resolve_task_id(chat_id, source, task_id)
    target = _get_task_payload(state, tid, chat_id, source) or (state if not _is_new_format(state) else None)
    return target.get("status") if target else None


# ═══════════════════════════════════════════════════════════════
# DIFF & CONTENT STORAGE (task-scoped, writers use FileLock)
# ═══════════════════════════════════════════════════════════════

def store_diffs(
    diffs: Dict[str, str],
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> None:
    """Store generated diffs. Uses FileLock."""
    tid = _resolve_task_id(chat_id, source, task_id)
    try:
        with agent_lock(chat_id=chat_id, source=source):
            state = load_state(chat_id, source)
            if not state:
                return
            target = _get_task_payload(state, tid, chat_id, source) or (state if not _is_new_format(state) else None)
            if target:
                target["diffs"] = diffs
                save_state(state, chat_id, source)
                if tid:
                    print(f"[task_id={tid}] store_diffs")
    except LockError:
        raise


def get_stored_diffs(
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> Dict[str, str]:
    """Get stored diffs for task (active if task_id None)."""
    state = load_state(chat_id, source)
    if not state:
        return {}
    tid = _resolve_task_id(chat_id, source, task_id)
    target = _get_task_payload(state, tid, chat_id, source) or (state if not _is_new_format(state) else None)
    return target.get("diffs", {}) if target else {}


def store_new_contents(
    contents: Dict[str, str],
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> bool:
    """Store new file contents. Uses FileLock."""
    tid = _resolve_task_id(chat_id, source, task_id)
    try:
        with agent_lock(chat_id=chat_id, source=source):
            state = load_state(chat_id, source)
            if not state:
                return False
            target = _get_task_payload(state, tid, chat_id, source) or (state if not _is_new_format(state) else None)
            if target:
                target["new_contents"] = contents
                save_state(state, chat_id, source)
                return True
            return False
    except LockError:
        raise


def get_stored_contents(
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> Dict[str, str]:
    """Get stored new contents for task (active if task_id None)."""
    state = load_state(chat_id, source)
    if not state:
        return {}
    tid = _resolve_task_id(chat_id, source, task_id)
    target = _get_task_payload(state, tid, chat_id, source) or (state if not _is_new_format(state) else None)
    if not target:
        return {}
    contents = target.get("new_contents", {})
    return contents if isinstance(contents, dict) else {}


# ═══════════════════════════════════════════════════════════════
# CLEANUP UTILITIES
# ═══════════════════════════════════════════════════════════════

def cleanup_old_sessions(days: int = 7) -> int:
    """
    Remove session files and/or SQLite sessions older than specified days.

    Args:
        days: Age threshold in days

    Returns:
        Number of sessions removed
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_iso = cutoff.isoformat()
    removed = 0

    if USE_SQLITE_STATE:
        try:
            for (chat_id, source) in db_list_sessions_updated_before(cutoff_iso):
                try:
                    db_delete_session(chat_id, source)
                    removed += 1
                except Exception as e:
                    print(f"⚠️ Error cleaning SQLite session {source}_{chat_id}: {e}")
        except Exception as e:
            print(f"⚠️ Error listing old sessions from SQLite: {e}")

    for session_file in SESSIONS_DIR.glob("*.json"):
        try:
            if session_file.parent != SESSIONS_DIR:
                continue
            mtime = datetime.fromtimestamp(session_file.stat().st_mtime)
            if mtime < cutoff:
                session_file.unlink()
                removed += 1
                lock_file = LOCKS_DIR / session_file.name.replace('.json', '.lock')
                if lock_file.exists():
                    lock_file.unlink()
        except Exception as e:
            print(f"⚠️ Error cleaning {session_file}: {e}")

    return removed


def list_active_sessions() -> list:
    """List all active sessions. Supports new format (active_task_id, task_queue)."""
    sessions = []

    if USE_SQLITE_STATE:
        try:
            for (chat_id, source) in db_list_all_sessions():
                session = db_get_session(chat_id, source)
                if not session:
                    continue
                tasks = db_get_tasks_for_session(chat_id, source)
                active_id = session.get("active_task_id")
                task_queue = session.get("task_queue", [])
                task_payload = None
                if active_id:
                    for t in tasks:
                        if t.get("task_id") == active_id:
                            task_payload = t
                            break
                sessions.append({
                    "filename": get_session_filename(chat_id, source),
                    "chat_id": chat_id,
                    "source": source,
                    "operation_id": (task_payload or {}).get("operation_id", (task_payload or {}).get("id", "unknown")),
                    "status": (task_payload or {}).get("status", "unknown"),
                    "created_at": (task_payload or {}).get("created_at", session.get("created_at", "unknown")),
                    "awaiting_response": (task_payload or {}).get("awaiting_response", False),
                    "active_task_id": active_id,
                    "task_queue_len": len(task_queue) if isinstance(task_queue, list) else 0,
                    "is_locked": is_locked(chat_id, source),
                })
        except Exception as e:
            print(f"⚠️ Error listing sessions from SQLite: {e}")
        return sessions

    for session_file in SESSIONS_DIR.glob("*.json"):
        try:
            state = json.loads(session_file.read_text(encoding='utf-8'))
            if not _is_new_format(state):
                state = migrate_state_to_multitask(state) if state else state
            chat_id = state.get("chat_id", "unknown")
            source = state.get("source", "http")
            active_id = state.get("active_task_id")
            task_payload = (state.get("tasks") or {}).get(active_id) if active_id else None
            sessions.append({
                "filename": session_file.name,
                "chat_id": chat_id,
                "source": source,
                "operation_id": (task_payload or {}).get("id", state.get("id", "unknown")),
                "status": (task_payload or {}).get("status", state.get("status", "unknown")),
                "created_at": (task_payload or {}).get("created_at", state.get("created_at", "unknown")),
                "awaiting_response": (task_payload or state).get("awaiting_response", False),
                "active_task_id": active_id,
                "task_queue_len": len(state.get("task_queue", [])),
                "is_locked": is_locked(chat_id, source),
            })
        except Exception as e:
            print(f"⚠️ Error reading {session_file}: {e}")
    return sessions


def find_session_by_task_id(task_id: str) -> Optional[Tuple[str, str]]:
    """
    Find (chat_id, source) for a session that has the given task_id.
    Phase 5: Always try SQLite first, then fall back to JSON scan.
    """
    if not task_id:
        return None

    try:
        result = db_find_session_by_task_id(task_id)
        if result:
            return result
    except Exception as e:
        log_event("sqlite_error", f"find_session_by_task_id failed: {e}")

    for session_file in SESSIONS_DIR.glob("*.json"):
        try:
            state = json.loads(session_file.read_text(encoding='utf-8'))
            if _is_new_format(state) and task_id in state.get("tasks", {}):
                print(f"[task_id={task_id}] find_session_by_task_id: {state.get('chat_id')} {state.get('source', 'http')}")
                return (state["chat_id"], state.get("source", "http"))
            if not _is_new_format(state) and state.get("task_id") == task_id:
                print(f"[task_id={task_id}] find_session_by_task_id (legacy): {state.get('chat_id')} {state.get('source', 'http')}")
                return (state["chat_id"], state.get("source", "http"))
        except Exception as e:
            print(f"⚠️ Error reading {session_file}: {e}")
    return None


# ═══════════════════════════════════════════════════════════════
# PENDING PLAN MANAGEMENT (task-scoped, writers use FileLock)
# ═══════════════════════════════════════════════════════════════

def set_pending_plan(
    plan_description: str,
    files_to_change: dict,
    diff_preview: str,
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> None:
    """Store pending plan awaiting user approval. Uses FileLock."""
    tid = _resolve_task_id(chat_id, source, task_id)
    try:
        with agent_lock(chat_id=chat_id, source=source):
            state = load_state(chat_id, source)
            if not state:
                return
            target = _get_task_payload(state, tid, chat_id, source) or (state if not _is_new_format(state) else None)
            if target:
                target["pending_plan"] = {
                    "description": plan_description,
                    "files_to_change": files_to_change,
                    "diff_preview": diff_preview,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                target["status"] = OperationStatus.DIFF_READY
                target["awaiting_response"] = True
                target["awaiting_type"] = "approval"
                save_state(state, chat_id, source)
                if tid:
                    print(f"[task_id={tid}] set_pending_plan")
    except LockError:
        raise


def get_pending_plan(
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> Optional[dict]:
    """Get pending plan for task (active if task_id None)."""
    state = load_state(chat_id, source)
    if not state:
        return None
    tid = _resolve_task_id(chat_id, source, task_id)
    target = _get_task_payload(state, tid, chat_id, source) or (state if not _is_new_format(state) else None)
    return target.get("pending_plan") if target else None


def clear_pending_plan(
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> None:
    """Clear pending plan after approval/rejection. Uses FileLock."""
    tid = _resolve_task_id(chat_id, source, task_id)
    try:
        with agent_lock(chat_id=chat_id, source=source):
            state = load_state(chat_id, source)
            if not state:
                return
            target = _get_task_payload(state, tid, chat_id, source) or (state if not _is_new_format(state) else None)
            if target:
                target["pending_plan"] = None
                target["awaiting_response"] = False
                target["awaiting_type"] = None
                save_state(state, chat_id, source)
    except LockError:
        raise