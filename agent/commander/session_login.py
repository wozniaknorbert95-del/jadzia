"""Enterprise Commander mobile login — one-time code exchange (no JWT in URL)."""

from __future__ import annotations

import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import jwt

from agent.db import (
    db_commander_get_login_code,
    db_commander_mark_login_code_used,
    db_commander_save_login_code,
)

logger = logging.getLogger(__name__)

LOGIN_CODE_TTL_MINUTES = 15
SESSION_JWT_HOURS = 24


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def _jwt_secret() -> str:
    secret = (os.getenv("JWT_SECRET") or "").strip()
    if not secret:
        raise RuntimeError("JWT_SECRET not configured")
    return secret


def mint_session_jwt(
    *,
    sub: str,
    role: str = "dowodca",
    hours: int = SESSION_JWT_HOURS,
) -> str:
    """Mint Commander session JWT (Bearer). Never put this in a shareable URL."""
    hours = max(1, min(int(hours), 24 * 7))
    payload = {
        "sub": str(sub),
        "role": role,
        "exp": _utc_now() + timedelta(hours=hours),
    }
    token = jwt.encode(payload, _jwt_secret(), algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def mint_login_link(
    *,
    base_url: str,
    sub: str,
    role: str = "dowodca",
) -> Dict[str, Any]:
    """
    Create one-time login code + Commander URL with ?code= (not JWT).

    Code is single-use, TTL LOGIN_CODE_TTL_MINUTES.
    """
    code = secrets.token_urlsafe(32)
    exp = _utc_now() + timedelta(minutes=LOGIN_CODE_TTL_MINUTES)
    code_hash = _hash_code(code)
    ok = db_commander_save_login_code(
        code_hash=code_hash,
        sub=str(sub),
        role=role,
        expires_at=exp.isoformat(),
    )
    if not ok:
        raise RuntimeError("failed to persist login code")
    qs = urlencode({"code": code})
    url = f"{base_url.rstrip('/')}/commander/?{qs}"
    logger.info(
        "[CommanderLogin] mint login code sub=%s role=%s expires_at=%s",
        sub,
        role,
        exp.isoformat(),
    )
    return {
        "url": url,
        "expires_at": exp.isoformat(),
        "ttl_minutes": LOGIN_CODE_TTL_MINUTES,
        "sub": str(sub),
        "role": role,
    }


def exchange_login_code(code: str) -> Optional[Dict[str, Any]]:
    """
    Exchange one-time code for session JWT. Returns None if invalid/used/expired.
    """
    raw = (code or "").strip()
    if not raw or len(raw) > 256:
        return None
    code_hash = _hash_code(raw)
    row = db_commander_get_login_code(code_hash)
    if not row:
        logger.info("[CommanderLogin] exchange miss (unknown code)")
        return None
    if row.get("used_at"):
        logger.info("[CommanderLogin] exchange reject used code")
        return None
    try:
        exp = datetime.fromisoformat(str(row["expires_at"]).replace("Z", "+00:00"))
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None
    if _utc_now() > exp:
        logger.info("[CommanderLogin] exchange reject expired code")
        return None
    db_commander_mark_login_code_used(code_hash)
    sub = str(row.get("sub") or "dowodca")
    role = str(row.get("role") or "dowodca")
    token = mint_session_jwt(sub=sub, role=role, hours=SESSION_JWT_HOURS)
    exp_jwt = _utc_now() + timedelta(hours=SESSION_JWT_HOURS)
    logger.info("[CommanderLogin] exchange ok sub=%s role=%s", sub, role)
    return {
        "token": token,
        "role": role,
        "sub": sub,
        "expires_at": exp_jwt.isoformat(),
    }
