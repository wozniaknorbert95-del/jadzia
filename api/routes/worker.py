"""Worker task API endpoints — task creation, status, input submission."""

import asyncio
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import verify_jwt
from core.models import (
    WorkerTaskCreateResponse,
    WorkerTaskInputRequest,
    WorkerTaskRequest,
    WorkerTasksCleanupRequest,
    WorkerTasksCleanupResponse,
)
from agent.state import (
    LockError,
    OperationStatus,
    add_task_to_queue,
    find_session_by_task_id,
    find_task_by_id,
    get_active_task_id,
    get_current_status,
    load_state,
    update_operation_status,
)

_log = logging.getLogger("api.routes.worker")
router = APIRouter(prefix="/worker", tags=["worker"])


def _task_api_status(internal_status: str) -> str:
    """Map internal status to worker API status."""
    if internal_status == OperationStatus.DIFF_READY:
        return "diff_ready"
    if internal_status == OperationStatus.COMPLETED:
        return "completed"
    if internal_status in (OperationStatus.FAILED, OperationStatus.ROLLED_BACK):
        return "error"
    return "in_progress"


def _task_response_from_payload(task_id: str, task_payload: dict, position_in_queue: int = 0) -> dict:
    """Build worker GET response from task payload."""
    internal_status = task_payload.get("status", "")
    return {
        "task_id": task_id,
        "status": _task_api_status(internal_status),
        "position_in_queue": position_in_queue,
        "awaiting_input": task_payload.get("awaiting_response", False),
        "input_type": task_payload.get("awaiting_type"),
        "response": task_payload.get("last_response", ""),
        "operation": {
            "id": task_payload.get("id"),
            "plan": task_payload.get("plan"),
            "diffs": task_payload.get("diffs", {}),
            "user_input": task_payload.get("user_input", "")[:100],
            "files_to_modify": task_payload.get("files_to_modify", []),
            "created_at": task_payload.get("created_at"),
            "awaiting_response": task_payload.get("awaiting_response", False),
        },
        "dry_run": task_payload.get("dry_run", False),
        "test_mode": task_payload.get("test_mode", False),
    }


async def _resolve_session_for_task(task_id: str):
    """Resolve (chat_id, source) for task_id from DB."""
    from agent.db import db_get_task

    task = db_get_task(task_id)
    if task:
        return (task["chat_id"], task["source"])
    await asyncio.sleep(0.25)
    task = db_get_task(task_id)
    if task:
        return (task["chat_id"], task["source"])
    return None


@router.post("/task", response_model=WorkerTaskCreateResponse)
async def worker_create_task(
    request: WorkerTaskRequest,
    dry_run: bool = Query(False, description="Preview mode — don't write files"),
    _auth=Depends(verify_jwt),
):
    """Create a new task (Quick ACK). Enqueues and returns immediately."""
    chat_id = request.chat_id
    source = "telegram" if (request.chat_id or "").startswith("telegram_") else "http"
    task_id = str(uuid.uuid4())
    test_mode = request.test_mode
    try:
        position = add_task_to_queue(
            chat_id,
            task_id,
            request.instruction,
            source,
            dry_run=dry_run,
            webhook_url=request.webhook_url,
            test_mode=test_mode,
        )
        _log.info("[task_id=%s] worker_create_task chat_id=%s source=%s position=%s", task_id, chat_id, source, position)
        return WorkerTaskCreateResponse(
            task_id=task_id,
            status="queued",
            position_in_queue=position,
            chat_id=chat_id,
            dry_run=dry_run,
            test_mode=test_mode,
        )
    except LockError:
        raise HTTPException(status_code=503, detail="Session locked, try again")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}")
async def worker_get_task(task_id: str, _auth=Depends(verify_jwt)):
    """Get task status by task_id."""

    session = find_session_by_task_id(task_id)
    if not session:
        _log.warning("[task_id=%s] GET /worker/task: not found in DB", task_id)
        raise HTTPException(status_code=404, detail="Task not found")
    chat_id, source = session
    task_payload = find_task_by_id(chat_id, task_id, source)
    if not task_payload:
        raise HTTPException(status_code=404, detail="Task not found")
    state = load_state(chat_id, source)
    position_in_queue = 0
    if state and state.get("active_task_id") == task_id:
        position_in_queue = 0
    elif state and state.get("task_queue"):
        try:
            position_in_queue = 1 + state["task_queue"].index(task_id)
        except ValueError:
            position_in_queue = 0
    return _task_response_from_payload(task_id, task_payload, position_in_queue)


@router.post("/task/{task_id}/input")
async def worker_task_input(
    task_id: str,
    body: WorkerTaskInputRequest,
    _auth=Depends(verify_jwt),
):
    """Submit user input for a task."""
    from agent.db import db_get_task

    session = find_session_by_task_id(task_id)
    if not session:
        session = await _resolve_session_for_task(task_id)
    if not session:
        task_after = db_get_task(task_id)
        row_info = (f"chat_id={task_after['chat_id']!r} source={task_after['source']!r}" if task_after else "no row")
        _log.warning("[worker_task_input] 404 task_id=%s db_get_task_after_retry=%s %s", task_id, task_after is not None, row_info)
        raise HTTPException(status_code=404, detail="Task not found")
    chat_id, source = session
    active_id = get_active_task_id(chat_id, source)
    if active_id != task_id:
        if active_id is None:
            row = db_get_task(task_id)
            if row and row.get("chat_id") == chat_id and row.get("source") == source:
                pass
            else:
                raise HTTPException(status_code=400, detail="Task is queued; input only accepted for the active task")
        else:
            raise HTTPException(status_code=400, detail="Task is queued; input only accepted for the active task")

    if body.approval is True:
        user_message = "tak"
    elif body.approval is False:
        user_message = "nie"
    elif body.answer is not None:
        user_message = body.answer
    else:
        raise HTTPException(status_code=400, detail="Provide either 'approval' (true/false) or 'answer' (string)")

    try:
        from core.agent import process_message

        response_text, awaiting_input, input_type = await process_message(
            user_input=user_message,
            chat_id=chat_id,
            task_id=task_id,
        )
        current_status = get_current_status(chat_id, source, task_id=task_id)
        if current_status is not None:
            update_operation_status(
                current_status,
                chat_id,
                source,
                task_id=task_id,
                last_response=response_text,
            )
        task_payload = find_task_by_id(chat_id, task_id, source)
        if not task_payload:
            task_row = db_get_task(task_id)
            if task_row:
                if task_row.get("chat_id") != chat_id or task_row.get("source") != source:
                    _log.warning("[task_id=%s] worker_task_input: db row has chat_id=%r source=%r expected chat_id=%r source=%r", task_id, task_row.get("chat_id"), task_row.get("source"), chat_id, source)
                task_payload = dict(task_row)
                if "operation_id" in task_payload and "id" not in task_payload:
                    task_payload["id"] = task_payload.get("operation_id")
            else:
                _log.error("[task_id=%s] worker_task_input: task state lost after process_message", task_id)
                raise HTTPException(status_code=404, detail="Task state lost after process_message")
        state = load_state(chat_id, source)
        position_in_queue = 0
        if state and state.get("task_queue") and task_id in state["task_queue"]:
            position_in_queue = 1 + state["task_queue"].index(task_id)
        return _task_response_from_payload(task_id, task_payload, position_in_queue)
    except HTTPException:
        raise
    except Exception as e:
        _log.error("[worker_task_input] unhandled exception task_id=%s: %s", task_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/cleanup", response_model=WorkerTasksCleanupResponse)
async def worker_tasks_cleanup(
    body: WorkerTasksCleanupRequest,
    _auth=Depends(verify_jwt),
):
    """Mark selected worker tasks as failed (cleanup stuck in_progress tasks)."""
    try:
        from agent.db import db_mark_tasks_failed

        reason = body.reason or "manual_cleanup"
        result = db_mark_tasks_failed(body.task_ids, reason)
        return WorkerTasksCleanupResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
