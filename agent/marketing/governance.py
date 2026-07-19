"""Governance execute API — approval_token bound to action_id (F2)."""

from __future__ import annotations

import hashlib
import logging
import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from agent.db import (
    db_get_marketing_shadow,
    db_update_marketing_shadow_hitl,
    get_connection,
)
from agent.marketing.circuit_breakers import is_execute_allowed
from agent.marketing.decision_engine import get_mb_mode

logger = logging.getLogger(__name__)

TOKEN_TTL_MINUTES = 15


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _utc_iso(dt: Optional[datetime] = None) -> str:
    return (dt or _utc_now()).isoformat()


def ensure_governance_schema() -> None:
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS marketing_approval_tokens (
            token_hash TEXT PRIMARY KEY,
            action_id TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used_at TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS circuit_breaker_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            breaker_id TEXT NOT NULL,
            message TEXT NOT NULL,
            action_id TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()


def mint_approval_token(action_id: str) -> Dict[str, Any]:
    """Mint one-time token bound to action_id (TTL 15m). Returns raw token once."""
    ensure_governance_schema()
    raw = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    now = _utc_now()
    expires = now + timedelta(minutes=TOKEN_TTL_MINUTES)
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO marketing_approval_tokens
        (token_hash, action_id, expires_at, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (token_hash, action_id, _utc_iso(expires), _utc_iso(now)),
    )
    conn.commit()
    return {
        "action_id": action_id,
        "approval_token": raw,
        "expires_at": _utc_iso(expires),
        "ttl_minutes": TOKEN_TTL_MINUTES,
    }


def _consume_token(action_id: str, raw_token: str) -> Dict[str, Any]:
    ensure_governance_schema()
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM marketing_approval_tokens WHERE token_hash = ?",
        (token_hash,),
    ).fetchone()
    if not row:
        return {"ok": False, "error": "invalid_token"}
    if row["action_id"] != action_id:
        return {"ok": False, "error": "token_action_mismatch"}
    if row["used_at"]:
        return {"ok": False, "error": "token_already_used"}
    exp = datetime.fromisoformat(str(row["expires_at"]).replace("Z", "+00:00"))
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > exp:
        return {"ok": False, "error": "token_expired"}
    conn.execute(
        "UPDATE marketing_approval_tokens SET used_at = ? WHERE token_hash = ?",
        (_utc_iso(), token_hash),
    )
    conn.commit()
    return {"ok": True}


def _log_breaker_trips(trips: list, action_id: str) -> None:
    ensure_governance_schema()
    conn = get_connection()
    now = _utc_iso()
    for t in trips:
        conn.execute(
            """
            INSERT INTO circuit_breaker_events (breaker_id, message, action_id, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (t["breaker_id"], t["message"], action_id, now),
        )
    conn.commit()


def execute_action(
    action_id: str,
    approval_token: str,
    *,
    actor: str = "dowodca",
) -> Dict[str, Any]:
    """
    Governed execute. Shadow mode always denies side-effects.
    Meta/TikTok Ads create remains PARK even when allowed.
    """
    shadow = db_get_marketing_shadow(action_id)
    if not shadow:
        return {"ok": False, "error": "action_not_found", "status_code": 404}

    token_check = _consume_token(action_id, approval_token)
    if not token_check.get("ok"):
        return {"ok": False, "error": token_check.get("error"), "status_code": 403}

    breakers = is_execute_allowed()
    if not breakers["allowed"]:
        _log_breaker_trips(breakers["trips"], action_id)
        db_update_marketing_shadow_hitl(
            action_id, "blocked_breaker", governance_result="deny"
        )
        return {
            "ok": False,
            "error": "circuit_breaker",
            "breakers": breakers["trips"],
            "status_code": 423,
            "mb_mode": get_mb_mode(),
        }

    mode = get_mb_mode()
    if mode == "shadow":
        return {
            "ok": False,
            "error": "shadow_mode",
            "message": "MB_MODE=shadow — execute denied (log only)",
            "status_code": 423,
            "mb_mode": mode,
        }

    # F2 Act path: ticket / paste-ready only — Ads API create PARK
    proposed = shadow.get("proposed_action")
    result_payload = {
        "executed": False,
        "execution_type": "ticket_only",
        "proposed_action": proposed,
        "note": (
            "Ads API create PARK. Approve = ticket / paste-ready for Ads Manager."
        ),
        "ticket_id": f"mkt-{uuid.uuid4().hex[:10]}",
        "actor": actor,
    }
    db_update_marketing_shadow_hitl(
        action_id, "executed_ticket", governance_result="allow"
    )
    logger.info(
        "[mb.governance] ticket execute action_id=%s type=%s actor=%s",
        action_id,
        proposed,
        actor,
    )
    return {
        "ok": True,
        "action_id": action_id,
        "mb_mode": mode,
        "result": result_payload,
        "status_code": 200,
    }


def approve_and_mint(action_id: str) -> Dict[str, Any]:
    """Telegram APPROVE path: record HITL + mint token for optional execute."""
    shadow = db_get_marketing_shadow(action_id)
    if not shadow:
        return {"ok": False, "error": "action_not_found"}
    db_update_marketing_shadow_hitl(action_id, "approved", governance_result="allow")
    token = mint_approval_token(action_id)
    mode = get_mb_mode()
    auto = (os.getenv("MB_AUTO_EXECUTE_ON_APPROVE") or "").strip() == "1"
    out: Dict[str, Any] = {
        "ok": True,
        "action_id": action_id,
        "mb_mode": mode,
        "approval_token": token["approval_token"],
        "expires_at": token["expires_at"],
    }
    if auto and mode != "shadow":
        out["execute"] = execute_action(
            action_id, token["approval_token"], actor="telegram_auto"
        )
    return out
