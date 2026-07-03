"""Session management endpoints."""

from fastapi import APIRouter, Depends

from api.dependencies import verify_jwt
from agent.state import list_active_sessions, cleanup_old_sessions

router = APIRouter(tags=["sessions"])


@router.get("/sessions")
async def get_sessions(_auth=Depends(verify_jwt)):
    """List all active sessions."""
    return {"sessions": list_active_sessions()}


@router.post("/sessions/cleanup")
async def cleanup_sessions(days: int = 7, _auth=Depends(verify_jwt)):
    """Clean up old sessions."""
    removed = cleanup_old_sessions(days=days)
    return {"removed": removed}
