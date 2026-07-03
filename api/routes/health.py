"""Health check, status, and maintenance endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import verify_jwt
from core.models import RollbackResponse, StatusResponse

router = APIRouter(tags=["health"])


@router.get("/")
async def root():
    """Root health check."""
    return {
        "status": "ok",
        "agent": "JADZIA",
        "version": "1.0.0",
        "message": "Agent ready",
    }


@router.get("/health")
async def health():
    """Shop health check."""
    from agent.tools.rest import health_check

    return health_check()


@router.get("/status", response_model=StatusResponse)
async def status():
    """Current agent and operation status."""
    from agent.state import load_state

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


@router.post("/rollback", response_model=RollbackResponse)
async def do_rollback(_auth=Depends(verify_jwt)):
    """Roll back latest changes."""
    try:
        from agent.tools.rest import rollback
        from agent.alerts import send_alert
        from agent.state import clear_state

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
            message=result.get("msg", "Rollback executed"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-ssh")
async def test_ssh(_auth=Depends(verify_jwt)):
    """Test SSH connection to the server."""
    from agent.tools.rest import test_ssh_connection

    success, message = test_ssh_connection()
    return {"status": "ok" if success else "error", "message": message}


@router.post("/clear")
async def clear(
    chat_id: Optional[str] = Query(None, description="Session chat_id"),
    source: Optional[str] = Query(None, description="Session source"),
    _auth=Depends(verify_jwt),
):
    """Clear session state and queue (emergency reset)."""
    from agent.state import force_unlock, clear_state, LockError

    cid = chat_id if chat_id is not None else "default"
    src = source if source is not None else "http"
    try:
        force_unlock(chat_id=cid, source=src)
        clear_state(chat_id=cid, source=src)
        return {"status": "ok", "message": f"State cleared for {src}_{cid}"}
    except LockError:
        raise HTTPException(status_code=503, detail="Session locked, try again shortly")


@router.get("/logs")
async def logs(limit: int = 20, _auth=Depends(verify_jwt)):
    """Recent log entries."""
    from agent.log import get_recent_logs

    return {"logs": get_recent_logs(limit=limit)}
