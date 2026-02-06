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
from datetime import datetime, timezone
import json
import uuid
import asyncio

# Ensure logs directory exists at startup
Path("logs").mkdir(exist_ok=True)

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
    agent_lock,
    LockError,
    OperationStatus,
    USE_SQLITE_STATE,
    cleanup_old_sessions,
)
from agent.alerts import send_alert
from agent.tools import rollback, health_check, test_ssh_connection
from agent.db import db_health_check, db_get_dashboard_metrics, db_get_worker_health_session_counts, db_mark_tasks_failed
from agent.log import get_recent_logs
from agent.agent import get_cost_stats, reset_cost_stats

from interfaces.telegram_api import router as telegram_router  # 🆕 NOWE (linia 1)

# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="JADZIA API",
    description="AI Agent do zarzadzania sklepem internetowym",
    version="1.0.0"
)

app.include_router(telegram_router)  # 🆕 NOWE (linia 2)

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
async def clear():
    """
    Czyści aktualny stan (awaryjne).
    """
    force_unlock()
    clear_state()
    return {"status": "ok", "message": "Stan wyczyszczony"}


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

async def verify_worker_jwt(request: Request):
    """
    When JWT_SECRET is set, require valid Authorization: Bearer <token>.
    When JWT_SECRET is not set, auth is disabled (backward compatible for dev/CI).
    """
    if not JWT_SECRET:
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
    Create a new task. If session has active task, queues and returns position_in_queue > 0.
    """
    chat_id = request.chat_id
    source = "http"
    task_id = str(uuid.uuid4())
    test_mode = request.test_mode
    try:
        with agent_lock(timeout=10, chat_id=chat_id, source=source):
            state = load_state(chat_id, source)
            active_id = get_active_task_id(chat_id, source) if state else None
            task_done = False
            if active_id and state and state.get("tasks"):
                t = state["tasks"].get(active_id)
                if t and t.get("status") in (OperationStatus.COMPLETED, OperationStatus.FAILED, OperationStatus.ROLLED_BACK):
                    task_done = True
            if active_id and not task_done:
                position = add_task_to_queue(
                    chat_id,
                    task_id,
                    request.instruction,
                    source,
                    dry_run=dry_run,
                    webhook_url=request.webhook_url,
                    test_mode=test_mode,
                )
                print(f"[task_id={task_id}] worker_create_task chat_id={chat_id} position_in_queue={position}")
                return WorkerTaskCreateResponse(
                    task_id=task_id,
                    status="queued",
                    position_in_queue=position,
                    chat_id=chat_id,
                    dry_run=dry_run,
                    test_mode=test_mode,
                )
        response_text, awaiting_input, input_type = await process_message(
            user_input=request.instruction,
            chat_id=chat_id,
            task_id=task_id,
            dry_run=dry_run,
            webhook_url=request.webhook_url,
            test_mode=test_mode,
        )
        with agent_lock(timeout=10, chat_id=chat_id, source=source):
            update_operation_status(
                get_current_status(chat_id, source, task_id=task_id),
                chat_id,
                source,
                task_id=task_id,
                last_response=response_text,
            )
        print(f"[task_id={task_id}] worker_create_task chat_id={chat_id} position_in_queue=0")
        return WorkerTaskCreateResponse(
            task_id=task_id,
            status="processing",
            position_in_queue=0,
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


@app.post("/worker/task/{task_id}/input")
async def worker_task_input(
    task_id: str, body: WorkerTaskInputRequest, _auth=Depends(verify_worker_jwt)
):
    """
    Submit user input for a task. Only the active task can receive input.
    """
    session = find_session_by_task_id(task_id)
    if not session:
        raise HTTPException(status_code=404, detail="Task not found")
    chat_id, source = session
    active_id = get_active_task_id(chat_id, source)
    if active_id != task_id:
        raise HTTPException(
            status_code=400,
            detail="Task is queued; input only accepted for the active task",
        )

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
            raise HTTPException(status_code=500, detail="Task state lost after process_message")
        state = load_state(chat_id, source)
        position_in_queue = 0
        if state and state.get("task_queue") and task_id in state["task_queue"]:
            position_in_queue = 1 + state["task_queue"].index(task_id)
        print(f"[task_id={task_id}] worker_task_input input_type={input_kind} result status={task_payload.get('status')}")
        return _task_response_from_task_payload(task_id, task_payload, position_in_queue)
    except HTTPException:
        raise
    except Exception as e:
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

    status = "healthy" if ssh_status == "ok" else "degraded"
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