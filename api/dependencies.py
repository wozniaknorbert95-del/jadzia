"""FastAPI dependency injection for external services and auth."""

from __future__ import annotations

import os
from typing import AsyncIterator, Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import require_secrets_enabled
from core.services import (
    ClaudeService,
    GeminiService,
    NotificationService,
    ServiceRegistry,
    WooCommerceService,
    get_registry,
)

_bearer = HTTPBearer(auto_error=False)

JWT_SECRET: Optional[str] = os.getenv("JWT_SECRET")


# ──────────────────────────────────────────────
# Service dependencies
# ──────────────────────────────────────────────

async def get_service_registry() -> AsyncIterator[ServiceRegistry]:
    yield get_registry()


async def get_claude_service(
    registry: ServiceRegistry = Depends(get_service_registry),
) -> ClaudeService:
    return registry.claude


async def get_gemini_service(
    registry: ServiceRegistry = Depends(get_service_registry),
) -> GeminiService:
    return registry.gemini


async def get_woocommerce_service(
    registry: ServiceRegistry = Depends(get_service_registry),
) -> WooCommerceService:
    return registry.woocommerce


async def get_notification_service(
    registry: ServiceRegistry = Depends(get_service_registry),
) -> NotificationService:
    return registry.notifications


# ──────────────────────────────────────────────
# Auth dependency
# ──────────────────────────────────────────────

async def verify_jwt(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> Optional[dict]:
    """
    When JWT_SECRET is set (or REQUIRE_SECRETS/production mode), require Bearer token.
    When JWT_SECRET is not set and not in production mode, auth is disabled (dev/CI).
    """
    if not JWT_SECRET:
        if require_secrets_enabled():
            raise HTTPException(status_code=500, detail="JWT_SECRET not configured")
        return None
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def require_scope(scope: str):
    """FastAPI dependency factory — server-side scope enforcement (N7)."""

    async def _checker(auth: Optional[dict] = Depends(verify_jwt)) -> dict:
        from agent.commander.authz import has_scope

        if auth is None:
            return {}
        if not has_scope(auth, scope):
            raise HTTPException(status_code=403, detail=f"Missing scope: {scope}")
        return auth

    return _checker
