import json
import sqlite3
from typing import Optional

from agent.db import (
    db_create_or_update_session,
    db_delete_session,
    db_get_session,
    db_get_tasks_for_session,
    db_set_active_task,
)
from agent.log import log_event

from agent.state._config import (
    BACKUPS_DIR,
    LEGACY_STATE_FILE,
    MIGRATION_MARKER,
    OperationStatus,
    _log,
)
from agent.state._helpers import (
    _check_invariants,
    _is_new_format,
    _prepare_db_task,
    _resolve_task_id,
    _get_task_payload,
    migrate_state_to_multitask,
)
from agent.state.locks import LockError, agent_lock


def _sync_to_sqlite(chat_id: str, source: str, state: dict) -> None:
    from agent.db import (
        _exec_create_or_update_session,
        _exec_create_task,
        _exec_set_active_task,
        _exec_update_task,
        _exec_update_task_queue,
        db_transaction_with_retry,
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


def migrate_legacy_state() -> None:
    if MIGRATION_MARKER.exists():
        return
    if LEGACY_STATE_FILE.exists():
        try:
            with open(LEGACY_STATE_FILE, 'r', encoding='utf-8') as f:
                legacy_state = json.load(f)
            if not _is_new_format(legacy_state):
                legacy_state = migrate_state_to_multitask(legacy_state)
            _sync_to_sqlite("default", "http", legacy_state)
            backup_path = LEGACY_STATE_FILE.with_suffix('.json.migrated')
            LEGACY_STATE_FILE.rename(backup_path)
            _log.info("Migrated legacy state to SQLite (http/default)")
        except Exception as e:
            _log.warning("Migration failed: %s", e)
    MIGRATION_MARKER.touch()


migrate_legacy_state()


def save_state(state: dict, chat_id: str = "default", source: str = "http") -> None:
    _check_invariants(state, chat_id, source)
    try:
        _sync_to_sqlite(chat_id, source, state)
        log_event("state_save", f"[STATE] Saved state for {chat_id} ({source})")
    except Exception as e:
        log_event("state_error", f"[STATE] Save failed for {chat_id} ({source}): {e}")
        raise RuntimeError(f"Failed to save state for {source}_{chat_id}: {e}")


def _load_state_from_sqlite(chat_id: str, source: str = "http") -> Optional[dict]:
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

        if not active_task_id and state["tasks"]:
            queue = state.get("task_queue") or []
            candidate = queue[0] if queue else None
            if candidate:
                db_set_active_task(chat_id, source, candidate)
                state["active_task_id"] = candidate
                active_task_id = candidate
                _log.debug("[SQLITE] Recovery: set active_task_id=%s for %s/%s", candidate, source, chat_id)

        _log.debug("[SQLITE] Loaded state chat_id=%s source=%s tasks=%s active_task_id=%s", chat_id, source, len(state["tasks"]), active_task_id or "None")
        log_event("sqlite_read", f"[SQLITE] Loaded state for {chat_id}/{source}: {len(state['tasks'])} tasks")
        return state

    except Exception as e:
        log_event("sqlite_error", f"[SQLITE] Error loading state: {e}")
        return None


def load_state(chat_id: str = "default", source: str = "http") -> Optional[dict]:
    try:
        state = _load_state_from_sqlite(chat_id, source)
        if state:
            return state
        db_create_or_update_session(chat_id, source)
        return _load_state_from_sqlite(chat_id, source)
    except Exception as e:
        log_event("sqlite_error", f"[SQLITE] Read failed for {chat_id}/{source}: {e}")
        return None


def clear_state(chat_id: str = "default", source: str = "http") -> None:
    try:
        with agent_lock(chat_id=chat_id, source=source):
            try:
                db_delete_session(chat_id, source)
            except Exception as e:
                _log.warning("[chat_id=%s] Error clearing SQLite state for %s_%s: %s", chat_id, source, chat_id, e)
    except LockError:
        raise


def archive_state(chat_id: str = "default", source: str = "http") -> None:
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
        _log.warning("Error archiving state: %s", e)


def has_pending_operation(
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> bool:
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
    state = load_state(chat_id, source)
    if not state:
        return None
    tid = _resolve_task_id(chat_id, source, task_id)
    target = _get_task_payload(state, tid, chat_id, source) or (state if not _is_new_format(state) else None)
    if not target or not target.get("awaiting_response"):
        return None
    return f"Operation {target.get('id', 'unknown')} | Status: {target.get('status', 'unknown')} | Awaiting: {target.get('awaiting_type', 'unknown')}"
