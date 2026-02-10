"""
api.py — FastAPI endpoints dla JADZIA
"""

# ============================================================
# DODANE: wczytanie pliku .env
# ============================================================
from dotenv import load_dotenv
load_dotenv()

import os
import jwt
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json
import logging
import uuid
import asyncio

# Ensure logs directory exists at startup
Path("logs").mkdir(exist_ok=True)

_log_worker = logging.getLogger("interfaces.api.worker")
JWT_SECRET = os.getenv("JWT_SECRET")

from agent.agent import process_message
from agent.state import (
    load_state,
    clear_state,
    force_unlock,
    find_session_by_task_id,
    find_task_by_id,
    get_current_status,
    get_active_task_id,
    add_task_to_queue,
    update_operation_status,
    create_operation,
    mark_task_completed,
    clear_active_task_and_advance,
    get_next_task_from_queue,
    agent_lock,
    LockError,
    OperationStatus,
    USE_SQLITE_STATE,
    cleanup_old_sessions,
    add_error,
    is_locked,
)
from agent.alerts import send_alert
from agent.tools import rollback, health_check, test_ssh_connection
from agent.db import db_health_check, db_get_dashboard_metrics, db_get_worker_health_session_counts, db_mark_tasks_failed, db_list_all_sessions, db_get_task
from agent.circuit_breaker import get_breaker, get_all_breakers, CircuitOpenError
from agent.log import get_recent_logs
from agent.agent import get_cost_stats, reset_cost_stats

from interfaces.telegram_api import router as telegram_router

# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="JADZIA API",
    description="AI Agent do zarzadzania sklepem internetowym",
    version="1.0.0"
)

if os.getenv("TELEGRAM_BOT_ENABLED", "") == "1":
    app.include_router(telegram_router)

# Global metrics for worker health (updated on startup and by webhooks)
health_metrics = {
    "startup_time": None,
    "last_success": None,
    "total_tasks": 0,
    "failed_tasks": 0,
    "errors_last_hour": [],
    "last_deployment_verification": {
        "timestamp": None,
        "healthy": None,
        "auto_rollback_count": 0,
    },
}


# ============================================================
# MODELE
# ============================================================

class ChatRequest(BaseModel):
    message: str
    chat_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    awaiting_input: bool
    input_type: Optional[str] = None


class StatusResponse(BaseModel):
    status: str
    operation: Optional[dict] = None


class RollbackResponse(BaseModel):
    status: str
    restored: List[str] = []
    errors: List[str] = []
    message: str


# Worker task API (FAZA 1)
class WorkerTaskRequest(BaseModel):
    instruction: str
    chat_id: str
    webhook_url: Optional[str] = None
    test_mode: bool = False


class WorkerTaskCreateResponse(BaseModel):
    task_id: str
    status: str  # "queued" | "processing"
    position_in_queue: int  # 0 = processing, >0 = queued
    chat_id: Optional[str] = None
    dry_run: bool = False
    test_mode: bool = False


class WorkerTaskInputRequest(BaseModel):
    approval: Optional[bool] = None
    answer: Optional[str] = None


class WorkerTasksCleanupRequest(BaseModel):
    task_ids: List[str]
    reason: Optional[str] = None


class WorkerTasksCleanupResponse(BaseModel):
    updated: List[str]
    skipped_terminal: List[str]
    not_found: List[str]


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "agent": "JADZIA",
        "version": "1.0.0",
        "message": "Agent gotowy do pracy"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Główny endpoint do komunikacji z agentem.
    
    Używany przez n8n do przekazywania wiadomości z Telegram.
    """
    try:
        response, awaiting_input, input_type = await process_message(
            user_input=request.message,
            chat_id=request.chat_id
        )
        
        return ChatResponse(
            response=response,
            awaiting_input=awaiting_input,
            input_type=input_type
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status", response_model=StatusResponse)
async def status():
    """
    Zwraca aktualny status agenta i operacji (default session).
    """
    state = load_state("default", "http")
    if not state:
        return StatusResponse(status="idle", operation=None)
    if state.get("tasks"):
        tasks = state.get("tasks") or {}
        active_id = state.get("active_task_id")
        task_payload = tasks.get(active_id) if active_id else None
        if not task_payload and tasks:
            task_payload = next(iter(tasks.values()))
        if task_payload:
            return StatusResponse(
                status=task_payload.get("status", "unknown"),
                operation={
                    "id": task_payload.get("id"),
                    "user_input": task_payload.get("user_input", "")[:100],
                    "created_at": task_payload.get("created_at"),
                    "files_to_modify": task_payload.get("files_to_modify", []),
                    "files_written": task_payload.get("written_files", {}),
                    "awaiting_response": task_payload.get("awaiting_response", False),
                },
            )
    return StatusResponse(
        status=state.get("status", "unknown"),
        operation={
            "id": state.get("id"),
            "user_input": state.get("user_input", "")[:100],
            "created_at": state.get("created_at"),
            "files_to_modify": state.get("files_to_modify", []),
            "files_written": state.get("written_files", state.get("files_written", [])),
            "awaiting_response": state.get("awaiting_response", False),
        },
    )


@app.post("/rollback", response_model=RollbackResponse)
async def do_rollback():
    """
    Wykonuje rollback ostatnich zmian.
    """
    try:
        result = rollback()
        if result.get("status") == "ok":
            send_alert("rollback_executed", None, result.get("msg", "OK"))
        else:
            send_alert("rollback_failed", None, result.get("msg", "Rollback failed"))
        clear_state()
        return RollbackResponse(
            status=result.get("status", "error"),
            restored=result.get("restored", []),
            errors=result.get("errors", []),
            message=result.get("msg", "Rollback wykonany")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """
    Sprawdza health sklepu.
    """
    result = health_check()
    return result


@app.get("/logs")
async def logs(limit: int = 20):
    """
    Zwraca ostatnie logi.
    """
    return {"logs": get_recent_logs(limit=limit)}


@app.post("/clear")
async def clear(
    chat_id: Optional[str] = Query(None, description="Session chat_id (e.g. telegram_6746343970). Omit to clear default."),
    source: Optional[str] = Query(None, description="Session source: 'http' or 'telegram'. Omit to clear default."),
):
    """
    Clear session state and queue (emergency reset).
    Without params: clears (default, http). With chat_id/source: clears that session (e.g. Telegram queue).
    """
    cid = chat_id if chat_id is not None else "default"
    src = source if source is not None else "http"
    try:
        force_unlock(chat_id=cid, source=src)
        clear_state(chat_id=cid, source=src)
        return {"status": "ok", "message": f"Stan wyczyszczony dla {src}_{cid}"}
    except LockError:
        raise HTTPException(status_code=503, detail="Session locked, try again shortly")


@app.get("/test-ssh")
async def test_ssh():
    """
    Testuje połączenie SSH.
    """
    success, message = test_ssh_connection()
    return {
        "status": "ok" if success else "error",
        "message": message
    }


# ============================================================
# WORKER TASK API (FAZA 1)
# ============================================================

_jwt_warning_logged = False


async def verify_worker_jwt(request: Request):
    """
    When JWT_SECRET is set, require valid Authorization: Bearer <token>.
    When JWT_SECRET is not set, auth is disabled (backward compatible for dev/CI).
    """
    global _jwt_warning_logged
    if not JWT_SECRET:
        if not _jwt_warning_logged:
            _log_worker.warning(
                "[SECURITY] JWT_SECRET is not set — Worker API authentication is DISABLED. "
                "Set JWT_SECRET environment variable for production deployments."
            )
            print(
                "[SECURITY] WARNING: JWT_SECRET not set — all Worker API endpoints are unauthenticated!"
            )
            _jwt_warning_logged = True
        return None
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = auth[7:].strip()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def _task_api_status(internal_status: str) -> str:
    """Map internal status to worker API status."""
    if internal_status == OperationStatus.DIFF_READY:
        return "diff_ready"
    if internal_status == OperationStatus.COMPLETED:
        return "completed"
    if internal_status in (OperationStatus.FAILED, OperationStatus.ROLLED_BACK):
        return "error"
    return "in_progress"


def _task_response_from_task_payload(task_id: str, task_payload: dict, position_in_queue: int = 0) -> dict:
    """Build GET /worker/task/{task_id} response from task payload."""
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


@app.post("/worker/task", response_model=WorkerTaskCreateResponse)
async def worker_create_task(
    request: WorkerTaskRequest,
    dry_run: bool = Query(False, description="Preview mode - don't write files"),
    _auth=Depends(verify_worker_jwt),
):
    """
    Create a new task (Quick ACK). Always enqueues and returns immediately.
    Worker loop picks up the task and runs process_message in background.
    For Telegram: the same chat_id (and thus source) must be used by the webhook
    when resolving the task for approval (get_jadzia_chat_id(request.user_id)).
    """
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
        print(f"[task_id={task_id}] worker_create_task (quick_ack) chat_id={chat_id} source={source} position_in_queue={position}")
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


@app.get("/worker/task/{task_id}")
async def worker_get_task(task_id: str, _auth=Depends(verify_worker_jwt)):
    """
    Get task status by task_id. Returns status, position_in_queue, awaiting_input, operation.
    """
    session = find_session_by_task_id(task_id)
    if not session:
        print(f"[task_id={task_id}] GET /worker/task: task not found in DB")
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
    print(f"[task_id={task_id}] worker_get_task status={task_payload.get('status')} position_in_queue={position_in_queue}")
    return _task_response_from_task_payload(task_id, task_payload, position_in_queue)


async def _resolve_session_for_task(task_id: str):
    """
    Resolve (chat_id, source) for task_id: try db_get_task first (direct read), then retry once after short delay.
    Returns (chat_id, source) or None.
    """
    task = db_get_task(task_id)
    if task:
        return (task["chat_id"], task["source"])
    await asyncio.sleep(0.25)
    task = db_get_task(task_id)
    if task:
        return (task["chat_id"], task["source"])
    return None


@app.post("/worker/task/{task_id}/input")
async def worker_task_input(
    task_id: str, body: WorkerTaskInputRequest, _auth=Depends(verify_worker_jwt)
):
    """
    Submit user input for a task. Only the active task can receive input.
    """
    session = find_session_by_task_id(task_id)
    if not session:
        session = await _resolve_session_for_task(task_id)
    if not session:
        task_after = db_get_task(task_id)
        row_info = (f"chat_id={task_after['chat_id']!r} source={task_after['source']!r}" if task_after else "no row")
        print(f"[worker_task_input] 404 task_id={task_id} db_get_task_after_retry={task_after is not None} {row_info}")
        raise HTTPException(status_code=404, detail="Task not found")
    chat_id, source = session
    active_id = get_active_task_id(chat_id, source)
    if active_id != task_id:
        # Recovery: when active_task_id is None (e.g. ghost-cleared), allow input if task exists in this session
        if active_id is None:
            row = db_get_task(task_id)
            if row and row.get("chat_id") == chat_id and row.get("source") == source:
                pass  # allow request (recovery path)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Task is queued; input only accepted for the active task",
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Task is queued; input only accepted for the active task",
            )

    # ── Idempotency guard: reject input for tasks in terminal states ──
    # This prevents double-submit of approvals from triggering duplicate writes.
    # Only blocks terminal tasks (completed/failed/rolled_back). Non-terminal tasks
    # may legitimately receive input even if not yet in awaiting state.
    task_check = find_task_by_id(chat_id, task_id, source)
    if not task_check:
        task_check = db_get_task(task_id)
    if task_check:
        task_status = task_check.get("status", "")
        if task_status in TERMINAL_STATUSES:
            print(f"[task_id={task_id}] worker_task_input: REJECTED (task already terminal: {task_status})")
            return _task_response_from_task_payload(task_id, task_check, 0)

    if body.approval is True:
        user_message = "tak"
    elif body.approval is False:
        user_message = "nie"
    elif body.answer is not None:
        user_message = body.answer
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide either 'approval' (true/false) or 'answer' (string)",
        )

    input_kind = "approval" if body.approval is not None else "answer"
    try:
        response_text, awaiting_input, input_type = await process_message(
            user_input=user_message,
            chat_id=chat_id,
            task_id=task_id,
        )
        # Diagnostic: is task still in DB right after process_message?
        _row = db_get_task(task_id)
        print(f"[worker_task_input] after process_message task_id={task_id} chat_id={chat_id!r} source={source!r} db_get_task={'yes' if _row else 'no'} row_source={_row.get('source') if _row else None}")
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
            # Fallback: state view may miss the task after process_message; read directly from DB
            task_row = db_get_task(task_id)
            if task_row:
                # Use row even if chat_id/source differ (diagnostic: log mismatch)
                if task_row.get("chat_id") != chat_id or task_row.get("source") != source:
                    print(f"[task_id={task_id}] worker_task_input: db row has chat_id={task_row.get('chat_id')!r} source={task_row.get('source')!r} expected chat_id={chat_id!r} source={source!r}")
                task_payload = dict(task_row)
                if "operation_id" in task_payload and "id" not in task_payload:
                    task_payload["id"] = task_payload.get("operation_id")
                print(f"[task_id={task_id}] worker_task_input: using db_get_task fallback after process_message")
            else:
                print(f"[task_id={task_id}] worker_task_input: task state lost after process_message db_get_task=None (task_id not in tasks table)")
                raise HTTPException(
                    status_code=404,
                    detail="Task state lost after process_message — task_id no longer in DB. Re-submit with /zadanie.",
                )
        state = load_state(chat_id, source)
        position_in_queue = 0
        if state and state.get("task_queue") and task_id in state["task_queue"]:
            position_in_queue = 1 + state["task_queue"].index(task_id)
        print(f"[task_id={task_id}] worker_task_input input_type={input_kind} result status={task_payload.get('status')}")
        return _task_response_from_task_payload(task_id, task_payload, position_in_queue)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/worker/tasks/cleanup", response_model=WorkerTasksCleanupResponse)
async def worker_tasks_cleanup(
    body: WorkerTasksCleanupRequest, _auth=Depends(verify_worker_jwt)
):
    """
    Manually mark selected worker tasks as failed (without deleting them).
    Used to clean up stuck in_progress tasks.
    """
    try:
        reason = body.reason or "manual_cleanup"
        result = db_mark_tasks_failed(body.task_ids, reason)
        return WorkerTasksCleanupResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/worker/health")
async def get_worker_health():
    """Health check endpoint for monitoring (Director V4)."""
    active_sessions = 0
    total_tasks = 0
    active_tasks = 0
    queued_tasks = 0

    if USE_SQLITE_STATE:
        try:
            active_sessions, total_tasks, active_tasks, queued_tasks = db_get_worker_health_session_counts()
        except Exception:
            # DB unavailable: fall back to JSON scan for rollback compatibility
            sessions_dir = Path("data/sessions")
            if sessions_dir.exists():
                for session_file in sessions_dir.glob("*.json"):
                    try:
                        with open(session_file, encoding="utf-8") as f:
                            state = json.load(f)
                        if state.get("tasks"):
                            active_sessions += 1
                            total_tasks += len(state["tasks"])
                            if state.get("active_task_id"):
                                active_tasks += 1
                            queued_tasks += len(state.get("task_queue", []))
                    except Exception:
                        pass
    else:
        sessions_dir = Path("data/sessions")
        if sessions_dir.exists():
            for session_file in sessions_dir.glob("*.json"):
                try:
                    with open(session_file, encoding="utf-8") as f:
                        state = json.load(f)
                    if state.get("tasks"):
                        active_sessions += 1
                        total_tasks += len(state["tasks"])
                        if state.get("active_task_id"):
                            active_tasks += 1
                        queued_tasks += len(state.get("task_queue", []))
                except Exception:
                    pass

    ssh_status = "unknown"
    try:
        success, _ = await asyncio.to_thread(test_ssh_connection)
        ssh_status = "ok" if success else "error"
    except Exception:
        ssh_status = "error"

    now = datetime.now(timezone.utc)
    recent_errors = []
    for e in health_metrics.get("errors_last_hour", []):
        try:
            ts = datetime.fromisoformat(e["timestamp"])
            if (now - ts).total_seconds() < 3600:
                recent_errors.append(e)
        except Exception:
            pass
    health_metrics["errors_last_hour"] = recent_errors

    uptime_seconds = 0
    if health_metrics.get("startup_time"):
        try:
            start = datetime.fromisoformat(health_metrics["startup_time"])
            uptime_seconds = int((now - start).total_seconds())
        except Exception:
            pass

    # Determine overall status considering circuit breakers
    breakers = get_all_breakers()
    any_circuit_open = any(b["state"] == "open" for b in breakers.values())
    if ssh_status != "ok" or any_circuit_open:
        status = "degraded"
    else:
        status = "healthy"
    last_ver = health_metrics.get("last_deployment_verification") or {}
    return {
        "status": status,
        "uptime_seconds": uptime_seconds,
        "active_sessions": active_sessions,
        "active_tasks": active_tasks,
        "queue_length": queued_tasks,
        "total_tasks": total_tasks,
        "ssh_connection": ssh_status,
        "sqlite_connection": db_health_check(),
        "last_success": health_metrics.get("last_success"),
        "errors_last_hour": len(recent_errors),
        "failed_tasks_total": health_metrics.get("failed_tasks", 0),
        "last_deployment_verification": {
            "timestamp": last_ver.get("timestamp"),
            "healthy": last_ver.get("healthy"),
            "auto_rollback_count": last_ver.get("auto_rollback_count", 0),
        },
        "circuit_breakers": breakers,
    }


def _dashboard_empty_response(sqlite_required: bool = False, error: Optional[str] = None) -> dict:
    """Response when USE_SQLITE_STATE is False or DB error."""
    out = {
        "total_tasks": 0,
        "by_status": {"completed": 0, "error": 0, "in_progress": 0, "diff_ready": 0},
        "test_mode_tasks": 0,
        "production_tasks": 0,
        "recent_tasks": [],
        "errors_last_24h": 0,
        "avg_duration_seconds": None,
    }
    if sqlite_required:
        out["sqlite_required"] = True
    if error:
        out["error"] = error
    return out


@app.get("/worker/dashboard")
async def get_worker_dashboard(_auth=Depends(verify_worker_jwt)):
    """Dashboard metrics for tasks (requires USE_SQLITE_STATE)."""
    if not USE_SQLITE_STATE:
        return _dashboard_empty_response(sqlite_required=True)

    try:
        raw = db_get_dashboard_metrics()
    except Exception:
        return _dashboard_empty_response(error="db_unavailable")

    by_status = {"completed": 0, "error": 0, "in_progress": 0, "diff_ready": 0}
    for item in raw["by_status_raw"]:
        api_status = _task_api_status(item["status"])
        by_status[api_status] = by_status.get(api_status, 0) + item["count"]

    recent_tasks = []
    for row in raw["recent_tasks_raw"]:
        created = row["created_at"]
        end_ts = row["completed_at"] or row["updated_at"]
        if created and end_ts:
            try:
                start = datetime.fromisoformat(created.replace("Z", "+00:00"))
                end = datetime.fromisoformat(end_ts.replace("Z", "+00:00"))
                duration_seconds = round((end - start).total_seconds(), 1)
            except Exception:
                duration_seconds = 0.0
        else:
            duration_seconds = 0.0

        recent_tasks.append({
            "task_id": row["task_id"],
            "status": _task_api_status(row["status"]),
            "test_mode": bool(row["test_mode"]),
            "dry_run": bool(row["dry_run"]),
            "created_at": created or "",
            "duration_seconds": duration_seconds,
        })

    return {
        "total_tasks": raw["total_tasks"],
        "by_status": by_status,
        "test_mode_tasks": raw["test_mode_tasks"],
        "production_tasks": raw["production_tasks"],
        "recent_tasks": recent_tasks,
        "errors_last_24h": raw["errors_last_24h"],
        "avg_duration_seconds": raw["avg_duration_seconds"],
    }


# ============================================================
# WORKER LOOP (queue processor)
# ============================================================

TERMINAL_STATUSES = (OperationStatus.COMPLETED, OperationStatus.FAILED, OperationStatus.ROLLED_BACK)

WORKER_TASK_TIMEOUT_SECONDS = int(os.getenv("WORKER_TASK_TIMEOUT_SECONDS", "600") or "600")
WORKER_STALE_TASK_MINUTES = int(os.getenv("WORKER_STALE_TASK_MINUTES", "15") or "15")
# Awaiting user response (plan approval, answer_questions, etc.). Default 24h; set 0 to disable.
WORKER_AWAITING_TIMEOUT_MINUTES = int(os.getenv("WORKER_AWAITING_TIMEOUT_MINUTES", "1440") or "1440")


async def _run_task_with_timeout(
    user_input: str,
    chat_id: str,
    source: str,
    task_id: str,
    timeout_sec: int,
) -> None:
    """
    Run process_message with a global timeout. On TimeoutError or CancelledError,
    mark task as FAILED and advance queue so the next task can run.
    """
    try:
        # Load per-task flags persisted at enqueue time
        state = await asyncio.to_thread(load_state, chat_id, source)
        task_data = ((state or {}).get("tasks") or {}).get(task_id, {}) if state else {}
        dry_run = bool(task_data.get("dry_run", False))
        test_mode = bool(task_data.get("test_mode", False))
        webhook_url = task_data.get("webhook_url") or None
        result = await asyncio.wait_for(
            process_message(
                user_input,
                chat_id=chat_id,
                source=source,
                task_id=task_id,
                dry_run=dry_run,
                webhook_url=webhook_url,
                test_mode=test_mode,
                push_to_telegram=True,
                auto_advance=False,  # worker loop owns queue advancement
            ),
            timeout=float(timeout_sec),
        )

        # Unpack result
        response_text, awaiting_input, input_type = result

        # If task is one-shot (no user input needed), mark as completed
        if not awaiting_input:
            # Check current status — don't overwrite FAILED with COMPLETED
            try:
                current = await asyncio.to_thread(
                    get_current_status, chat_id, source, task_id
                )
                if current and current in TERMINAL_STATUSES:
                    print(f"  [worker_loop] task {task_id} already terminal ({current}), skipping COMPLETED overwrite")
                    # Still advance queue so next task can run
                    await asyncio.to_thread(mark_task_completed, chat_id, task_id, source)
                else:
                    await asyncio.to_thread(
                        update_operation_status,
                        OperationStatus.COMPLETED,
                        chat_id,
                        source,
                        task_id=task_id,
                    )
                    # Advance queue
                    await asyncio.to_thread(
                        mark_task_completed,
                        chat_id,
                        task_id,
                        source
                    )
                    print(f"  [worker_loop] task {task_id} completed (one-shot)")
            except Exception as e:
                print(f"  [worker_loop] failed to mark task completed: {e}")
    except asyncio.TimeoutError:
        reason = f"worker_timeout: process_message timed out after {timeout_sec}s"
        print(f"  [worker_loop] FAILED_SET task_id={task_id} chat_id={chat_id} source={source} reason={reason}")
        try:
            await asyncio.to_thread(add_error, reason, chat_id, source, task_id)
            await asyncio.to_thread(
                update_operation_status,
                OperationStatus.FAILED,
                chat_id,
                source,
                task_id=task_id,
            )
            await asyncio.to_thread(mark_task_completed, chat_id, task_id, source)
            task_payload = find_task_by_id(chat_id, task_id, source)
            wh_url = (task_payload or {}).get("webhook_url")
            if wh_url:
                from interfaces.webhooks import notify_webhook
                await notify_webhook(wh_url, task_id, "failed", {"error": f"Task timed out after {timeout_sec}s"})
            # Push timeout error to Telegram
            if str(chat_id).startswith("telegram_"):
                try:
                    from interfaces.telegram_api import send_awaiting_response_to_telegram
                    await send_awaiting_response_to_telegram(
                        chat_id,
                        f"❌ Zadanie przekroczyło limit czasu ({timeout_sec}s). Spróbuj ponownie z `/zadanie ...`",
                        task_id=task_id, status="failed", awaiting_input=False,
                    )
                except Exception as push_err:
                    print(f"  [worker_loop] failed to push timeout to Telegram: {push_err}")
        except Exception as e:
            print(f"  [worker_loop] failed to mark task_id={task_id} FAILED after timeout: {e}")
            import traceback
            traceback.print_exc()
    except CircuitOpenError as coe:
        reason = f"circuit_breaker_open: {coe}"
        print(f"  [worker_loop] FAILED_SET task_id={task_id} chat_id={chat_id} source={source} reason={reason}")
        try:
            await asyncio.to_thread(add_error, reason, chat_id, source, task_id)
            await asyncio.to_thread(
                update_operation_status,
                OperationStatus.FAILED,
                chat_id,
                source,
                task_id=task_id,
            )
            await asyncio.to_thread(mark_task_completed, chat_id, task_id, source)
            if str(chat_id).startswith("telegram_"):
                try:
                    from interfaces.telegram_api import send_awaiting_response_to_telegram
                    await send_awaiting_response_to_telegram(
                        chat_id,
                        "❌ Połączenie SSH jest niestabilne (circuit breaker aktywny). Zadanie wstrzymane — spróbuj ponownie za kilka minut.",
                        task_id=task_id, status="failed", awaiting_input=False,
                    )
                except Exception as push_err:
                    print(f"  [worker_loop] failed to push circuit-open to Telegram: {push_err}")
        except Exception as e:
            print(f"  [worker_loop] failed to mark task_id={task_id} FAILED after circuit-open: {e}")
    except asyncio.CancelledError:
        reason = "worker_cancelled: process_message task was cancelled"
        print(f"  [worker_loop] FAILED_SET task_id={task_id} chat_id={chat_id} source={source} reason={reason}")
        try:
            await asyncio.to_thread(add_error, reason, chat_id, source, task_id)
            await asyncio.to_thread(
                update_operation_status,
                OperationStatus.FAILED,
                chat_id,
                source,
                task_id=task_id,
            )
            await asyncio.to_thread(mark_task_completed, chat_id, task_id, source)
            # Push cancel error to Telegram
            if str(chat_id).startswith("telegram_"):
                try:
                    from interfaces.telegram_api import send_awaiting_response_to_telegram
                    await send_awaiting_response_to_telegram(
                        chat_id,
                        "❌ Zadanie zostało anulowane. Spróbuj ponownie z `/zadanie ...`",
                        task_id=task_id, status="failed", awaiting_input=False,
                    )
                except Exception as push_err:
                    print(f"  [worker_loop] failed to push cancel to Telegram: {push_err}")
        except Exception as e:
            print(f"  [worker_loop] failed to mark task_id={task_id} FAILED after cancel: {e}")
            import traceback
            traceback.print_exc()
        raise


def _parse_timestamp_to_utc(ts_str: str) -> Optional[datetime]:
    """
    Parse ISO timestamp string to timezone-aware UTC datetime.
    Handles:
    - Aware timestamps (with Z or offset) → converted to UTC.
    - Naive timestamps (no tz info) → treated as server local time, converted to UTC.
    Returns None on parse failure.
    """
    if not ts_str or not ts_str.strip():
        return None
    ts_str = ts_str.strip()
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            # Naive: assume server local time and convert to UTC
            dt = dt.astimezone(timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt
    except (ValueError, TypeError) as e:
        print(f"  [worker_loop] _parse_timestamp_to_utc failed for {ts_str!r}: {e}")
        return None


def _safe_age_minutes(dt_utc: datetime) -> float:
    """
    Calculate age in minutes from a UTC-aware datetime.
    If age is negative (clock skew / stale local timestamps), clamp to 0 and log warning.
    """
    age = datetime.now(timezone.utc) - dt_utc
    if age.total_seconds() < 0:
        print(f"  [worker_loop] WARNING negative_age: timestamp={dt_utc.isoformat()} now={datetime.now(timezone.utc).isoformat()} age_sec={age.total_seconds():.1f} — clamped to 0")
        return 0.0
    return age.total_seconds() / 60.0


def _worker_loop_done_callback(task: asyncio.Task, chat_id: str, source: str, task_id: str) -> None:
    """Log exceptions from process_message when run by worker_loop."""
    try:
        exc = task.exception()
        if exc is not None:
            print(f"  [worker_loop] process_message failed chat_id={chat_id} source={source} task_id={task_id}: {exc}")
            import traceback
            traceback.print_exception(type(exc), exc, exc.__traceback__)
    except asyncio.CancelledError:
        pass


async def _worker_loop():
    """Background loop: advance queues when active task is terminal or missing; run next task via process_message.
    Uses intelligent backoff: short sleep (1-2s) when there was active work, gradual backoff up to 30s when idle."""
    base_interval = int(os.getenv("WORKER_LOOP_INTERVAL_SECONDS", "15") or "0")
    if base_interval <= 0:
        print("  [worker_loop] disabled (WORKER_LOOP_INTERVAL_SECONDS <= 0)")
        return
    busy_sleep = int(os.getenv("WORKER_LOOP_BUSY_SLEEP_SECONDS", "2") or "2")
    max_idle_sleep = 30
    idle_backoff_sec = min(base_interval, max_idle_sleep)
    iter_num = 0
    while True:
        iter_num += 1
        had_work = False
        try:
            print(f"  [worker_loop] iteration {iter_num} start")
            try:
                sessions = await asyncio.to_thread(db_list_all_sessions)
            except Exception as e:
                print(f"  [worker_loop] db_list_all_sessions failed: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(idle_backoff_sec)
                continue
            if not sessions:
                print(f"  [worker_loop] no sessions found")
            else:
                _log_worker.debug("  [worker_loop] sessions count=%s list=%s", len(sessions), sessions)
            # Load all session states in parallel to avoid blocking the loop on SQLite I/O
            states = await asyncio.gather(*[asyncio.to_thread(load_state, c, s) for (c, s) in sessions])
            for ((chat_id, source), state) in zip(sessions, states):
                try:
                    if not state:
                        print(f"  [worker_loop] session {source}/{chat_id}: no state, skip")
                        continue
                    queue = state.get("task_queue") or []
                    # INFO only for sessions that have active work (tasks or queue)
                    if queue or state.get("active_task_id"):
                        _log_worker.info(
                            "  [worker_loop] session %s/%s has active work tasks=%s queue_len=%s",
                            source, chat_id, len(state.get("tasks") or {}), len(queue),
                        )
                    active_id = state.get("active_task_id")
                    next_task_id = None
                    if not queue:
                        # Empty queue: check if active task needs attention.
                        task = (state.get("tasks") or {}).get(active_id) if active_id else None
                        status = (task or {}).get("status") if task else None

                        # Ghost active_task_id: task data missing from state → clear only if not in DB (avoid false ghost)
                        if active_id and task is None:
                            row = db_get_task(active_id)
                            if row and row.get("chat_id") == chat_id and row.get("source") == source:
                                print(f"  [worker_loop] session {source}/{chat_id}: active_id={active_id} missing from state but exists in DB, skip clear")
                                continue
                            print(f"  [worker_loop] session {source}/{chat_id}: ghost active_task_id={active_id} (task data missing), clearing")
                            try:
                                await asyncio.to_thread(clear_active_task_and_advance, chat_id, source)
                                had_work = True
                            except Exception as e:
                                print(f"  [worker_loop] session {source}/{chat_id}: failed to clear ghost active_task_id: {e}")
                            continue

                        # Only recover truly stuck tasks (status=queued).
                        # For tasks already in progress or awaiting input, let them be.
                        if active_id and status == "queued":
                            next_task_id = active_id
                            print(f"  [worker_loop] session {source}/{chat_id}: recovery run for queued active_id={active_id} (empty queue)")
                        elif active_id and status and status in TERMINAL_STATUSES:
                            # Terminal but not cleaned up — advance queue
                            next_task_id = await asyncio.to_thread(
                                mark_task_completed, chat_id, active_id, source
                            )
                            print(f"  [worker_loop] session {source}/{chat_id}: terminal active_id={active_id} cleaned up => next_task_id={next_task_id}")
                        else:
                            # Active task in progress / awaiting input / no active task — skip
                            continue
                    elif active_id:
                        task = (state.get("tasks") or {}).get(active_id)
                        status = (task or {}).get("status")
                        print(f"  [worker_loop] session {source}/{chat_id}: active_id={active_id} status={status} queue_len={len(queue)}")

                        # Ghost active_task_id: task data missing → clear only if not in DB (avoid false ghost)
                        if task is None:
                            row = db_get_task(active_id)
                            if row and row.get("chat_id") == chat_id and row.get("source") == source:
                                print(f"  [worker_loop] session {source}/{chat_id}: active_id={active_id} missing from state but exists in DB, skip clear")
                                continue
                            print(f"  [worker_loop] session {source}/{chat_id}: ghost active_task_id={active_id} (task data missing, queue has {len(queue)} items), clearing")
                            try:
                                next_task_id = await asyncio.to_thread(clear_active_task_and_advance, chat_id, source)
                                had_work = True
                                print(f"  [worker_loop] session {source}/{chat_id}: ghost cleared => next_task_id={next_task_id}")
                            except Exception as e:
                                print(f"  [worker_loop] session {source}/{chat_id}: failed to clear ghost: {e}")
                                continue
                        elif status in TERMINAL_STATUSES:
                            next_task_id = await asyncio.to_thread(
                                mark_task_completed, chat_id, active_id, source
                            )
                            print(f"  [worker_loop] session {source}/{chat_id}: mark_task_completed => next_task_id={next_task_id}")
                        else:
                            task_dict = task or {}
                            status_val = task_dict.get("status", "")
                            # FIX: queued task = ready to process, pick it up immediately
                            if status_val == "queued":
                                next_task_id = active_id
                                print(f"  [worker_loop] session {source}/{chat_id}: active task {active_id} is queued, will process")
                            # If session is actively being processed (lock held), skip stale/awaiting checks.
                            # This prevents marking long-running tasks as FAILED while process_message is still running.
                            elif await asyncio.to_thread(is_locked, chat_id, source):
                                print(f"  [worker_loop] session {source}/{chat_id}: locked, skipping stale/timeout checks")
                                # No next_task_id => we effectively wait for the running task to progress/finish.
                                continue
                            # Awaiting-timeout: only for PLANNING + awaiting_response (user never responded).
                            # Uses created_at for age; threshold WORKER_AWAITING_TIMEOUT_MINUTES so we don't
                            # block the queue indefinitely. Mark FAILED and advance; RUNNING/COMPLETED/FAILED unchanged.
                            if status_val == "planning" and task_dict.get("awaiting_response", False):
                                awaiting_threshold = WORKER_AWAITING_TIMEOUT_MINUTES
                                awaiting_timed_out = False
                                aw_ts_str = (task_dict.get("created_at") or "").strip()
                                aw_field_used = "created_at" if aw_ts_str else "updated_at"
                                if not aw_ts_str:
                                    aw_ts_str = (task_dict.get("updated_at") or "").strip()
                                    print(f"  [worker_loop] session {source}/{chat_id} awaiting timeout check: created_at missing, using updated_at")
                                aw_dt = _parse_timestamp_to_utc(aw_ts_str) if aw_ts_str else None
                                if aw_dt and awaiting_threshold > 0:
                                    aw_age_minutes = _safe_age_minutes(aw_dt)
                                    if aw_age_minutes > awaiting_threshold:
                                        awaiting_timed_out = True
                                    else:
                                        print(f"  [worker_loop] session {source}/{chat_id} awaiting timeout check: using {aw_field_used} age_minutes={aw_age_minutes:.1f} threshold={awaiting_threshold} (not timed out)")
                                elif not aw_ts_str:
                                    print(f"  [worker_loop] session {source}/{chat_id} awaiting timeout check: no timestamp, cannot determine age")
                                elif awaiting_threshold <= 0:
                                    print(f"  [worker_loop] session {source}/{chat_id} awaiting timeout check: WORKER_AWAITING_TIMEOUT_MINUTES={awaiting_threshold}, disabled")
                                if awaiting_timed_out:
                                    reason = f"worker_awaiting_timeout: field={aw_field_used} value={aw_ts_str} threshold={awaiting_threshold}min"
                                    print(f"  [worker_loop] FAILED_SET task_id={active_id} chat_id={chat_id} source={source} reason={reason}")
                                    try:
                                        await asyncio.to_thread(add_error, reason, chat_id, source, active_id)
                                        await asyncio.to_thread(
                                            update_operation_status,
                                            OperationStatus.FAILED,
                                            chat_id,
                                            source,
                                            task_id=active_id,
                                        )
                                        next_task_id = await asyncio.to_thread(
                                            mark_task_completed, chat_id, active_id, source
                                        )
                                        print(f"  [worker_loop] session {source}/{chat_id}: awaiting timeout cleared => next_task_id={next_task_id}")
                                    except Exception as e:
                                        print(f"  [worker_loop] session {source}/{chat_id}: failed to clear awaiting timeout task: {e}")
                                        import traceback
                                        traceback.print_exc()
                            # Stale check only for non-awaiting (planning+awaiting use awaiting timeout only, not 15min stale).
                            if next_task_id is None and not (status_val == "planning" and task_dict.get("awaiting_response", False)):
                                # Stale-task check: if active task not terminal and too old, mark FAILED and advance.
                                # For PLANNING we use created_at (set once); for other statuses updated_at.
                                stale_minutes = WORKER_STALE_TASK_MINUTES
                                is_stale = False
                                if status_val == "planning":
                                    ts_str = (task_dict.get("created_at") or "").strip()
                                    field_used = "created_at" if ts_str else "updated_at"
                                    if not ts_str:
                                        ts_str = (task_dict.get("updated_at") or "").strip()
                                        print(f"  [worker_loop] session {source}/{chat_id} stale check: status=planning created_at missing, using updated_at")
                                else:
                                    ts_str = (task_dict.get("updated_at") or "").strip()
                                    field_used = "updated_at"
                                dt_utc = _parse_timestamp_to_utc(ts_str) if ts_str else None
                                if dt_utc and stale_minutes > 0:
                                    age_minutes = _safe_age_minutes(dt_utc)
                                    if age_minutes > stale_minutes:
                                        is_stale = True
                                    else:
                                        print(f"  [worker_loop] session {source}/{chat_id} stale check: status={status_val} using {field_used} age_minutes={age_minutes:.1f} threshold={stale_minutes} (not stale)")
                                elif not ts_str:
                                    print(f"  [worker_loop] session {source}/{chat_id} stale check: no timestamp, cannot determine age")
                                elif stale_minutes <= 0:
                                    print(f"  [worker_loop] session {source}/{chat_id} stale check: WORKER_STALE_TASK_MINUTES={stale_minutes}, disabled")
                                if is_stale:
                                    reason = f"worker_stale_task: field={field_used} value={ts_str} threshold={stale_minutes}min status={status_val}"
                                    print(f"  [worker_loop] FAILED_SET task_id={active_id} chat_id={chat_id} source={source} reason={reason}")
                                    try:
                                        await asyncio.to_thread(add_error, reason, chat_id, source, active_id)
                                        await asyncio.to_thread(
                                            update_operation_status,
                                            OperationStatus.FAILED,
                                            chat_id,
                                            source,
                                            task_id=active_id,
                                        )
                                        next_task_id = await asyncio.to_thread(
                                            mark_task_completed, chat_id, active_id, source
                                        )
                                        print(f"  [worker_loop] session {source}/{chat_id}: stale task cleared => next_task_id={next_task_id}")
                                    except Exception as e:
                                        print(f"  [worker_loop] session {source}/{chat_id}: failed to clear stale task: {e}")
                                        import traceback
                                        traceback.print_exc()
                            if next_task_id is None:
                                print(f"  [worker_loop] session {source}/{chat_id}: active task not terminal, waiting")
                    else:
                        next_task_id = await asyncio.to_thread(
                            get_next_task_from_queue, chat_id, source
                        )
                        print(f"  [worker_loop] session {source}/{chat_id}: get_next_task_from_queue => next_task_id={next_task_id}")
                    if not next_task_id:
                        continue
                    had_work = True  # we have a task to run or to consider (lock/user_input may still skip)
                    # Race condition guard: skip if session is already locked (another process_message running)
                    if await asyncio.to_thread(is_locked, chat_id, source):
                        print(f"  [worker_loop] session {source}/{chat_id} task_id={next_task_id}: session locked, skip this iteration")
                        continue
                    state2 = await asyncio.to_thread(load_state, chat_id, source)
                    user_input = ((state2 or {}).get("tasks") or {}).get(next_task_id, {}).get("user_input") or ""
                    if not user_input:
                        print(f"  [worker_loop] session {source}/{chat_id} task_id={next_task_id}: user_input empty, skip")
                        continue
                    timeout_sec = WORKER_TASK_TIMEOUT_SECONDS
                    print(f"  [worker_loop] session {source}/{chat_id} task_id={next_task_id}: starting process_message (push_to_telegram=True, timeout={timeout_sec}s) user_input_len={len(user_input)}")
                    t = asyncio.create_task(
                        _run_task_with_timeout(
                            user_input,
                            chat_id=chat_id,
                            source=source,
                            task_id=next_task_id,
                            timeout_sec=timeout_sec,
                        )
                    )
                    t.add_done_callback(lambda _t, c=chat_id, s=source, tid=next_task_id: _worker_loop_done_callback(_t, c, s, tid))
                except LockError as e:
                    print(f"  [worker_loop] session {source}/{chat_id}: LockError (session busy), skip: {e}")
                except Exception as e:
                    print(f"  [worker_loop] session {source}/{chat_id}: {type(e).__name__}: {e}")
                    import traceback
                    traceback.print_exc()
            if had_work:
                sleep_sec = busy_sleep
                idle_backoff_sec = busy_sleep  # reset backoff for next idle phase
            else:
                sleep_sec = idle_backoff_sec
                idle_backoff_sec = min(idle_backoff_sec + 1, max_idle_sleep)
            print(f"  [worker_loop] iteration {iter_num} end, sleeping {sleep_sec}s")
            await asyncio.sleep(sleep_sec)
        except asyncio.CancelledError:
            print("  [worker_loop] cancelled, exit")
            break
        except Exception as e:
            print(f"  [worker_loop] iteration failed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(idle_backoff_sec)


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup():
    """Inicjalizacja przy starcie"""
    from pathlib import Path
    from interfaces.webhooks import set_health_metrics
    Path("data").mkdir(exist_ok=True)
    health_metrics["startup_time"] = datetime.now(timezone.utc).isoformat()
    set_health_metrics(health_metrics)
    try:
        removed = cleanup_old_sessions(days=7)
        if removed > 0:
            print(f"  [startup] cleanup_old_sessions: removed {removed} session(s)")
    except Exception as e:
        print(f"  [startup] cleanup_old_sessions failed: {e}")
    worker_interval = int(os.getenv("WORKER_LOOP_INTERVAL_SECONDS", "15") or "0")
    if worker_interval > 0:
        asyncio.create_task(_worker_loop())
        print(f"  [startup] worker_loop started (interval={worker_interval}s)")
    print("=" * 50)
    print("  JADZIA API uruchomiona")
    print("  Endpoints: /chat, /status, /rollback, /health")
    print("=" * 50)


# ============================================================
# MAIN
# ============================================================

# ============================================================
# ENDPOINT DO MONITORINGU KOSZTÓW
# Dodaj do interfaces/api.py
# ============================================================

from agent.agent import get_cost_stats, reset_cost_stats

@app.get("/costs")
async def get_costs():
    """Zwraca statystyki użycia i kosztów."""
    stats = get_cost_stats()
    
    # Dodaj user-friendly format
    return {
        "usage": {
            "input_tokens": stats["total_input_tokens"],
            "output_tokens": stats["total_output_tokens"],
            "cached_tokens": stats["total_cached_tokens"],
            "total_tokens": stats["total_input_tokens"] + stats["total_output_tokens"]
        },
        "costs": {
            "total_usd": f"${stats['total_cost_usd']:.4f}",
            "savings_from_cache_usd": f"${stats['estimated_savings_from_cache']:.4f}",
            "cost_per_1k_tokens": f"${(stats['total_cost_usd'] / ((stats['total_input_tokens'] + stats['total_output_tokens']) / 1000)):.4f}" if stats['total_input_tokens'] > 0 else "$0.00"
        },
        "optimization": {
            "cache_hit_rate": f"{(stats['total_cached_tokens'] / max(stats['total_input_tokens'], 1)) * 100:.1f}%",
            "enabled_features": ["prompt_caching", "file_truncation"]
        }
    }


@app.post("/costs/reset")
async def reset_costs():
    """Resetuje statystyki kosztów."""
    reset_cost_stats()
    return {"status": "ok", "message": "Statystyki kosztów zresetowane"}


@app.get("/costs/estimate")
async def estimate_cost(tokens: int = 1000):
    """Oszacowanie kosztu dla danej liczby tokenów."""
    input_cost = (tokens / 1_000_000) * 3.0
    output_cost = (tokens / 1_000_000) * 15.0
    cached_cost = (tokens / 1_000_000) * 0.30
    
    return {
        "tokens": tokens,
        "costs": {
            "without_cache": f"${input_cost + output_cost:.4f}",
            "with_cache_90%": f"${(input_cost * 0.1) + output_cost + (cached_cost * 0.9):.4f}",
            "savings": f"${(input_cost * 0.9) - (cached_cost * 0.9):.4f}"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)