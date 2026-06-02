"""Dashboard and worker health endpoints."""

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends

from api.dependencies import verify_jwt
from agent.state import USE_SQLITE_STATE

_log = logging.getLogger("api.routes.dashboard")
router = APIRouter(prefix="/worker", tags=["dashboard"])


def _dashboard_empty_response(sqlite_required: bool = False, error: str = None) -> dict:
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


@router.get("/dashboard")
async def get_worker_dashboard(_auth=Depends(verify_jwt)):
    """Dashboard metrics for tasks."""
    from agent.db import db_get_dashboard_metrics

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


def _task_api_status(internal_status: str) -> str:
    """Map internal status to worker API status."""
    from agent.state import OperationStatus

    if internal_status == OperationStatus.DIFF_READY:
        return "diff_ready"
    if internal_status == OperationStatus.COMPLETED:
        return "completed"
    if internal_status in (OperationStatus.FAILED, OperationStatus.ROLLED_BACK):
        return "error"
    return "in_progress"


@router.get("/health")
async def get_worker_health():
    """Health check endpoint for monitoring (Director V4)."""
    from agent.db import (
        db_get_worker_health_session_counts,
        db_health_check,
    )
    from agent.state import USE_SQLITE_STATE
    from agent.tools.rest import test_ssh_connection
    from api._state import _worker_loop_ref, health_metrics

    active_sessions = 0
    total_tasks = 0
    active_tasks = 0
    queued_tasks = 0

    if USE_SQLITE_STATE:
        try:
            active_sessions, total_tasks, active_tasks, queued_tasks = db_get_worker_health_session_counts()
        except Exception:
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

    worker_alive = _worker_loop_ref is not None and not _worker_loop_ref.done()
    status = "healthy" if ssh_status == "ok" and worker_alive else "degraded"
    last_ver = health_metrics.get("last_deployment_verification") or {}
    return {
        "status": status,
        "uptime_seconds": uptime_seconds,
        "worker_loop_alive": worker_alive,
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
