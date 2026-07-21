"""Shared bounds for public HTTP ingress."""

from __future__ import annotations

import hashlib
import os
import uuid

from fastapi import HTTPException, Request

from agent.db import (
    WIDGET_CHAT_SESSION_TTL_SEC,
    db_check_and_record_ingress_rate,
    db_register_widget_chat_session,
    db_widget_chat_session_is_active,
)

WIDGET_BODY_MAX_BYTES = 8_192
TELEGRAM_BODY_MAX_BYTES = 65_536
BRAIN_BUS_BODY_MAX_BYTES = 16_384
WIDGET_RATE_WINDOW_SEC = 3_600


def _positive_env(name: str, default: int, *, minimum: int = 1) -> int:
    try:
        return max(minimum, int(os.getenv(name, str(default))))
    except ValueError:
        return default


def widget_rate_limit() -> int:
    return _positive_env("WIDGET_CHAT_RATE_LIMIT", 30)


async def read_limited_body_async(request: Request, *, max_bytes: int) -> bytes:
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > max_bytes:
                raise HTTPException(status_code=413, detail="Request body too large")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid Content-Length") from exc
    body: bytes = await request.body()
    if len(body) > max_bytes:
        raise HTTPException(status_code=413, detail="Request body too large")
    return body


def _client_key(request: Request, session_id: str) -> str:
    client_ip = request.client.host if request.client else "unknown"
    salt = os.getenv("INGRESS_RATE_SALT", "")
    raw = f"{salt}|{client_ip}|{session_id}".encode()
    return hashlib.sha256(raw).hexdigest()


def check_widget_rate_limit(request: Request, session_id: str) -> None:
    if not db_check_and_record_ingress_rate(
        _client_key(request, session_id),
        window_sec=WIDGET_RATE_WINDOW_SEC,
        limit=widget_rate_limit(),
    ):
        raise HTTPException(
            status_code=429,
            detail="Te veel berichten. Probeer het later opnieuw.",
            headers={"Retry-After": str(WIDGET_RATE_WINDOW_SEC)},
        )


def _is_issued_widget_session(session_id: str | None) -> bool:
    try:
        parsed = uuid.UUID((session_id or "").strip())
    except (ValueError, AttributeError):
        return False
    return parsed.version == 4 and db_widget_chat_session_is_active(
        str(parsed), ttl_sec=WIDGET_CHAT_SESSION_TTL_SEC
    )


def resolve_widget_session(session_id: str | None) -> str:
    """Use only known UUIDv4 sessions; mint an opaque replacement otherwise."""
    if session_id and _is_issued_widget_session(session_id):
        return str(uuid.UUID(session_id.strip()))
    issued = str(uuid.uuid4())
    db_register_widget_chat_session(issued)
    return issued
