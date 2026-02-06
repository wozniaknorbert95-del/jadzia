"""
Telegram Bot — HTTP client for Worker API.

Calls local Worker API (POST/GET /worker/task, POST /worker/task/{id}/input)
and POST /rollback with JWT from TELEGRAM_BOT_JWT_TOKEN or generated from JWT_SECRET.
Uses TELEGRAM_BOT_API_BASE_URL (default http://127.0.0.1:8000).
"""

import os
from typing import Any, Dict, Optional

import httpx

# Load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 120.0  # Worker task can run long


def get_bot_jwt_token() -> Optional[str]:
    """
    Return JWT for Worker API: from TELEGRAM_BOT_JWT_TOKEN or generate from JWT_SECRET.
    Returns None if neither is set.
    """
    token = os.getenv("TELEGRAM_BOT_JWT_TOKEN", "").strip()
    if token:
        return token
    secret = os.getenv("JWT_SECRET", "").strip()
    if not secret:
        return None
    try:
        import jwt
        from datetime import datetime, timedelta, timezone
        payload = {
            "sub": "worker",
            "exp": datetime.now(timezone.utc) + timedelta(days=365),
        }
        t = jwt.encode(payload, secret, algorithm="HS256")
        return t if isinstance(t, str) else t.decode("utf-8")
    except Exception:
        return None


def get_base_url() -> str:
    """Return Worker API base URL from env or default."""
    return os.getenv("TELEGRAM_BOT_API_BASE_URL", "").strip() or DEFAULT_BASE_URL


async def create_task(
    instruction: str,
    chat_id: str,
    jwt_token: str,
    base_url: Optional[str] = None,
    test_mode: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    POST /worker/task. Returns dict with task_id, status, position_in_queue, etc.
    Raises httpx.HTTPStatusError on 4xx/5xx.
    """
    url = (base_url or get_base_url()).rstrip("/") + "/worker/task"
    headers = {"Authorization": f"Bearer {jwt_token}", "Content-Type": "application/json"}
    payload = {
        "instruction": instruction,
        "chat_id": chat_id,
        "test_mode": test_mode,
    }
    params = {"dry_run": str(dry_run).lower()}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.post(url, json=payload, headers=headers, params=params)
        r.raise_for_status()
        return r.json()


async def get_task(
    task_id: str,
    jwt_token: str,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    GET /worker/task/{task_id}. Returns task status, response, operation, etc.
    Raises httpx.HTTPStatusError on 4xx/5xx.
    """
    url = (base_url or get_base_url()).rstrip("/") + f"/worker/task/{task_id}"
    headers = {"Authorization": f"Bearer {jwt_token}"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(url, headers=headers)
        r.raise_for_status()
        return r.json()


async def submit_input(
    task_id: str,
    jwt_token: str,
    base_url: Optional[str] = None,
    approval: Optional[bool] = None,
    answer: Optional[str] = None,
) -> Dict[str, Any]:
    """
    POST /worker/task/{task_id}/input with approval and/or answer.
    Raises httpx.HTTPStatusError on 4xx/5xx.
    """
    url = (base_url or get_base_url()).rstrip("/") + f"/worker/task/{task_id}/input"
    headers = {"Authorization": f"Bearer {jwt_token}", "Content-Type": "application/json"}
    body: Dict[str, Any] = {}
    if approval is not None:
        body["approval"] = approval
    if answer is not None:
        body["answer"] = answer
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.post(url, json=body, headers=headers)
        r.raise_for_status()
        return r.json()


async def do_rollback(base_url: Optional[str] = None) -> Dict[str, Any]:
    """
    POST /rollback (no JWT). Returns status, restored, errors, message.
    Raises httpx.HTTPStatusError on 4xx/5xx.
    """
    url = (base_url or get_base_url()).rstrip("/") + "/rollback"
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(url)
        r.raise_for_status()
        return r.json()
