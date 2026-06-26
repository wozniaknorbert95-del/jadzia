import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from agent.state._config import OperationStatus, _log


def _is_new_format(state: dict) -> bool:
    return state is not None and "tasks" in state


def _check_invariants(state: dict, chat_id: str, source: str) -> None:
    if not state or not _is_new_format(state):
        return
    tasks = state.get("tasks") or {}
    active_id = state.get("active_task_id")
    queue = state.get("task_queue") or []

    if active_id and active_id not in tasks:
        _log.warning("[INVARIANT] %s/%s: active_task_id=%s not in tasks (ghost). Auto-clearing.", source, chat_id, active_id)
        state["active_task_id"] = None

    valid_queue = [tid for tid in queue if tid in tasks]
    if len(valid_queue) != len(queue):
        removed = set(queue) - set(valid_queue)
        _log.warning("[INVARIANT] %s/%s: task_queue contained orphan ids %s. Auto-removed.", source, chat_id, removed)
        state["task_queue"] = valid_queue


def _prepare_db_task(task_id: str, task_data: dict, chat_id: str, source: str) -> dict:
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


def migrate_state_to_multitask(state: dict) -> dict:
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


def _resolve_task_id(chat_id: str, source: str, task_id: Optional[str]) -> Optional[str]:
    if task_id:
        return task_id
    from agent.state.tasks import get_active_task_id
    return get_active_task_id(chat_id, source)


def _get_task_payload(state: dict, task_id: Optional[str], chat_id: str, source: str) -> Optional[dict]:
    if not task_id:
        from agent.state.tasks import get_active_task_id
        task_id = get_active_task_id(chat_id, source)
    if not task_id:
        return None
    if _is_new_format(state) and task_id in state.get("tasks", {}):
        return state["tasks"][task_id]
    if not _is_new_format(state) and state.get("task_id") == task_id:
        return state
    return None
