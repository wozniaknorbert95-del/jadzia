"""Append-only audit log with hash-chain."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agent.db import db_commander_insert_audit, db_commander_last_audit_hash, db_commander_list_audit

logger = logging.getLogger(__name__)


def _canonical(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def append_audit(
    *,
    actor_id: str,
    actor_role: str,
    action: str,
    source: str,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    before: Optional[Dict] = None,
    after: Optional[Dict] = None,
    reason: Optional[str] = None,
    risk_tier: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Optional[int]:
    ts = datetime.now(timezone.utc).isoformat()
    prev_hash = db_commander_last_audit_hash() or ""
    core = {
        "ts": ts,
        "actor_id": actor_id,
        "actor_role": actor_role,
        "action": action,
        "source": source,
        "target_type": target_type,
        "target_id": target_id,
        "before_json": json.dumps(before) if before is not None else None,
        "after_json": json.dumps(after) if after is not None else None,
        "reason": reason,
        "risk_tier": risk_tier,
        "session_id": session_id,
        "prev_hash": prev_hash,
    }
    row_hash = hashlib.sha256((prev_hash + _canonical(core)).encode()).hexdigest()
    core["row_hash"] = row_hash
    row_id = db_commander_insert_audit(core)
    if row_id:
        logger.info(
            "[CommanderAudit] action=%s actor=%s target=%s:%s",
            action,
            actor_id,
            target_type,
            target_id,
        )
    return row_id


def list_audit(limit: int = 100, offset: int = 0) -> List[Dict]:
    return db_commander_list_audit(limit=limit, offset=offset)
