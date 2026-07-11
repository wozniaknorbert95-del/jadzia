"""SQLite-backed chat session persistence (F-006) — survives jadzia restart."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SESSION_TTL_SEC = 2 * 3600


def _db_path() -> Path:
    raw = os.getenv("DA_CHAT_SESSION_DB", "/tmp/da-chat-sessions.sqlite3")
    return Path(raw)


def _connect() -> sqlite3.Connection:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id TEXT PRIMARY KEY,
            payload TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    return conn


def _is_expired(updated_at: str) -> bool:
    try:
        ts = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - ts).total_seconds()
        return age > SESSION_TTL_SEC
    except (TypeError, ValueError):
        return True


def save_session(session_id: str, payload: dict[str, Any]) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO chat_sessions (session_id, payload, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                payload = excluded.payload,
                updated_at = excluded.updated_at
            """,
            (session_id, json.dumps(payload, ensure_ascii=False), now),
        )
        conn.commit()


def load_session(session_id: str) -> dict[str, Any] | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT payload, updated_at FROM chat_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
    if not row:
        return None
    payload_raw, updated_at = row
    if _is_expired(updated_at):
        delete_session(session_id)
        return None
    try:
        data = json.loads(payload_raw)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def delete_session(session_id: str) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
        conn.commit()


def clear_all() -> None:
    """Test helper."""
    with _connect() as conn:
        conn.execute("DELETE FROM chat_sessions")
        conn.commit()
