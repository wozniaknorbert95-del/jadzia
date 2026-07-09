"""Append-only audit log with hash-chain."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from agent.db import db_commander_insert_audit, db_commander_last_audit_hash, db_commander_list_audit

logger = logging.getLogger(__name__)

RETENTION_MONTHS = 24


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


def verify_audit_chain() -> Dict[str, Any]:
    """Tamper-evidence verification (N2)."""
    rows = db_commander_list_audit(limit=10000, offset=0)
    prev = ""
    for row in reversed(rows):
        core = {
            "ts": row["ts"],
            "actor_id": row["actor_id"],
            "actor_role": row["actor_role"],
            "action": row["action"],
            "source": row["source"],
            "target_type": row.get("target_type"),
            "target_id": row.get("target_id"),
            "before_json": row.get("before_json"),
            "after_json": row.get("after_json"),
            "reason": row.get("reason"),
            "risk_tier": row.get("risk_tier"),
            "session_id": row.get("session_id"),
            "prev_hash": prev,
        }
        expected = hashlib.sha256((prev + _canonical(core)).encode()).hexdigest()
        if expected != row.get("row_hash"):
            return {
                "valid": False,
                "broken_at_id": row.get("id"),
                "expected": expected,
                "actual": row.get("row_hash"),
            }
        prev = row.get("row_hash") or ""
    return {"valid": True, "rows_checked": len(rows)}


def purge_audit_retention(export_path: Optional[str] = None) -> Dict[str, int]:
    """Export and purge rows older than 24 months (N2)."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=RETENTION_MONTHS * 30)).isoformat()
    rows = db_commander_list_audit(limit=50000, offset=0)
    old = [r for r in rows if r.get("ts", "") < cutoff]
    if export_path and old:
        with open(export_path, "w", encoding="utf-8") as fh:
            json.dump(old, fh, indent=2)
    from agent.db import get_connection

    conn = get_connection()
    deleted = 0
    for row in old:
        conn.execute("DELETE FROM commander_audit_log WHERE id = ?", (row["id"],))
        deleted += 1
    if deleted:
        conn.commit()
    return {"exported": len(old) if export_path else 0, "purged": deleted, "cutoff": cutoff}
