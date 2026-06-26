import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple

from agent.db import (
    db_find_session_by_task_id,
    db_get_awaiting_approval_task,
    db_get_session,
    db_get_tasks_for_session,
    db_list_all_sessions,
    db_list_sessions_updated_before,
    db_delete_session,
    db_set_active_task,
)
from agent.log import log_event

from agent.state._config import (
    OperationStatus,
    TERMINAL_STATUSES,
    _log,
)
from agent.state._helpers import (
    _get_task_payload,
    _is_new_format,
    _resolve_task_id,
    migrate_state_to_multitask,
)
from agent.state.core import load_state, save_state
from agent.state.locks import LockError, agent_lock, get_session_filename, is_locked


def get_active_task_id(chat_id: str = "default", source: str = "http") -> Optional[str]:
    state = load_state(chat_id, source)
    if not state:
        _log.debug("[get_active_task_id] Looking for task for user chat_id=%s source=%s status=active ... Found: None (no state)", chat_id, source)
        return None
    if _is_new_format(state):
        active_id = state.get("active_task_id")
        tasks = state.get("tasks") or {}
        if active_id and active_id not in tasks:
            try:
                if db_find_session_by_task_id(active_id) is None:
                    db_set_active_task(chat_id, source, None)
                    _log.debug("[get_active_task_id] ghost active_task_id=%s cleared for %s/%s", active_id, source, chat_id)
            except Exception as e:
                log_event("sqlite_error", f"get_active_task_id clear ghost failed: {e}")
            _log.debug("[get_active_task_id] Looking for task for user chat_id=%s source=%s status=active ... Found: None (ghost cleared)", chat_id, source)
            return None
        _log.debug("[get_active_task_id] Looking for task for user chat_id=%s source=%s status=active ... Found: %s", chat_id, source, active_id or "None")
        return active_id
    result = state.get("task_id")
    _log.debug("[get_active_task_id] Looking for task for user chat_id=%s source=%s status=active ... Found: %s (legacy)", chat_id, source, result or "None")
    return result


def get_awaiting_approval_task_id(chat_id: str, source: str = "http") -> Optional[str]:
    task = db_get_awaiting_approval_task(chat_id, source)
    task_id = task["task_id"] if task else None
    _log.debug("[get_awaiting_approval_task_id] Looking for task for user chat_id=%s source=%s status=awaiting_approval ... Found: %s", chat_id, source, task_id or "None")
    return task_id


def find_task_by_id(chat_id: str, task_id: str, source: str = "http") -> Optional[dict]:
    state = load_state(chat_id, source)
    if not state:
        _log.debug("[find_task_by_id] Looking for task_id=%s chat_id=%s source=%s ... Found: False (no state)", task_id, chat_id, source)
        return None
    if _is_new_format(state) and task_id in state.get("tasks", {}):
        _log.debug("[find_task_by_id] Looking for task_id=%s chat_id=%s source=%s ... Found: True", task_id, chat_id, source)
        return state["tasks"][task_id]
    if not _is_new_format(state) and state.get("task_id") == task_id:
        _log.debug("[find_task_by_id] Looking for task_id=%s chat_id=%s source=%s ... Found: True (legacy)", task_id, chat_id, source)
        return state
    _log.debug("[find_task_by_id] Looking for task_id=%s chat_id=%s source=%s ... Found: False", task_id, chat_id, source)
    return None


def is_dry_run(chat_id: str, task_id: str, source: str = "http") -> bool:
    state = load_state(chat_id, source)
    task = state.get("tasks", {}).get(task_id, {}) if state else {}
    return task.get("dry_run", False)


def is_test_mode(chat_id: str, task_id: str, source: str = "http") -> bool:
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
            _log.debug("[task_id=%s] add_task_to_queue chat_id=%s position_in_queue=%s", task_id, chat_id, pos)
            return pos
    except LockError:
        raise


def get_next_task_from_queue(chat_id: str, source: str = "http") -> Optional[str]:
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
            _log.debug("[task_id=%s] get_next_task_from_queue chat_id=%s", task_id, chat_id)
            return task_id
    except LockError:
        raise


def mark_task_completed(chat_id: str, task_id: str, source: str = "http") -> Optional[str]:
    try:
        with agent_lock(chat_id=chat_id, source=source):
            state = load_state(chat_id, source)
            if not state or not _is_new_format(state):
                return None
            prev_status = "?"
            if task_id in state.get("tasks", {}):
                prev_status = state["tasks"][task_id].get("status", "")
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
            _log.debug("[task_id=%s] mark_task_completed chat_id=%s prev_status=%s next_task_id=%s", task_id, chat_id, prev_status, next_task_id)
            return next_task_id
    except LockError:
        raise


def clear_active_task_and_advance(chat_id: str, source: str = "http") -> Optional[str]:
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
            _log.info("[clear_active_task_and_advance] %s/%s: cleared ghost active_id=%s => next_task_id=%s", source, chat_id, old_active, next_task_id)
            return next_task_id or None
    except LockError:
        raise


def create_operation(
    user_input: str,
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
    dry_run: bool = False,
    test_mode: bool = False,
    webhook_url: Optional[str] = None,
) -> dict:
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
            _log.debug("[task_id=%s] create_operation chat_id=%s", task_id, chat_id)
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
    tid = _resolve_task_id(chat_id, source, task_id)
    try:
        with agent_lock(chat_id=chat_id, source=source):
            state = load_state(chat_id, source)
            if not state:
                try:
                    from agent.db import db_create_or_update_session
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
                if prev_status in TERMINAL_STATUSES and status not in TERMINAL_STATUSES:
                    _log.warning("[STATUS_GUARD] task_id=%s rejecting %s -> %s (terminal status protected)", tid, prev_status, status)
                    save_state(state, chat_id, source)
                    return state
                target["status"] = status
                target["updated_at"] = datetime.now(timezone.utc).isoformat()
                for key, value in kwargs.items():
                    target[key] = value
                if status == OperationStatus.FAILED:
                    _log.warning("[FAILED_SET] task_id=%s chat_id=%s source=%s prev_status=%s created_at=%s updated_at=%s awaiting_response=%s", tid, chat_id, source, prev_status, target.get("created_at", "?"), target.get("updated_at", "?"), target.get("awaiting_response", "?"))
            save_state(state, chat_id, source)
            if tid:
                _log.debug("[task_id=%s] update_operation_status status=%s", tid, status)
    except LockError:
        raise
    return state


def add_error(
    error: str,
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> None:
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
                    _log.debug("[task_id=%s] add_error", tid)
    except LockError:
        raise


def mark_file_written(
    path: str,
    backup_path: Optional[str] = None,
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> None:
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
                    _log.debug("[task_id=%s] set_awaiting_response awaiting=%s", tid, awaiting)
    except LockError:
        raise


def get_operation_id(
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> Optional[str]:
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
    state = load_state(chat_id, source)
    if not state:
        return None
    tid = _resolve_task_id(chat_id, source, task_id)
    target = _get_task_payload(state, tid, chat_id, source) or (state if not _is_new_format(state) else None)
    return target.get("status") if target else None


def store_diffs(
    diffs: Dict[str, str],
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> None:
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
                    _log.debug("[task_id=%s] store_diffs", tid)
    except LockError:
        raise


def get_stored_diffs(
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> Dict[str, str]:
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
    state = load_state(chat_id, source)
    if not state:
        return {}
    tid = _resolve_task_id(chat_id, source, task_id)
    target = _get_task_payload(state, tid, chat_id, source) or (state if not _is_new_format(state) else None)
    if not target:
        return {}
    contents = target.get("new_contents", {})
    return contents if isinstance(contents, dict) else {}


def cleanup_old_sessions(days: int = 7) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_iso = cutoff.isoformat()
    removed = 0

    try:
        for (chat_id, source) in db_list_sessions_updated_before(cutoff_iso):
            try:
                db_delete_session(chat_id, source)
                removed += 1
            except Exception as e:
                _log.warning("Error cleaning SQLite session %s_%s: %s", source, chat_id, e)
    except Exception as e:
        _log.warning("Error listing old sessions from SQLite: %s", e)

    return removed


def list_active_sessions() -> list:
    sessions = []

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
        _log.warning("Error listing sessions from SQLite: %s", e)

    return sessions


def find_session_by_task_id(task_id: str) -> Optional[Tuple[str, str]]:
    return db_find_session_by_task_id(task_id)


def set_pending_plan(
    plan_description: str,
    files_to_change: dict,
    diff_preview: str,
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> None:
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
                    _log.debug("[task_id=%s] set_pending_plan", tid)
    except LockError:
        raise


def get_pending_plan(
    chat_id: str = "default",
    source: str = "http",
    task_id: Optional[str] = None,
) -> Optional[dict]:
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
