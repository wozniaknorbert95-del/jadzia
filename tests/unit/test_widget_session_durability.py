"""REV-DEMAND-02: widget chat SQLite/TTL hybrid session durability."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _isolate_db(monkeypatch):
    import tempfile

    import agent.db as db_mod

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr(db_mod, "DB_PATH", path)
    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
    return path


def _cleanup_db(path: str) -> None:
    import agent.db as db_mod

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
    try:
        os.unlink(path)
    except OSError:
        pass


def test_long_session_id_normalized_same_key(monkeypatch):
    path = _isolate_db(monkeypatch)
    from agent.customer_agent import (
        _customer_sessions_cache,
        _normalize_widget_session_id,
        _persist_widget_history,
        _load_widget_history,
    )
    from agent.db import db_get_widget_chat_history

    _customer_sessions_cache.clear()
    long_id = "w" * 200
    norm = _normalize_widget_session_id(long_id)
    assert len(norm) == 128
    _persist_widget_history(long_id, [{"role": "user", "content": "x"}])
    _customer_sessions_cache.clear()
    loaded = _load_widget_history(long_id)
    assert loaded == [{"role": "user", "content": "x"}]
    assert db_get_widget_chat_history(norm) == loaded
    _cleanup_db(path)


def test_widget_history_roundtrip(monkeypatch):
    path = _isolate_db(monkeypatch)
    from agent.db import (
        db_delete_widget_chat_history,
        db_get_widget_chat_history,
        db_save_widget_chat_history,
    )

    history = [
        {"role": "user", "content": "hoi"},
        {"role": "assistant", "content": '{"reply":"Hallo"}'},
    ]
    db_save_widget_chat_history("sess-rt", history)
    loaded = db_get_widget_chat_history("sess-rt")
    assert loaded == history
    db_delete_widget_chat_history("sess-rt")
    assert db_get_widget_chat_history("sess-rt") is None
    _cleanup_db(path)


def test_widget_created_at_set_once_on_insert(monkeypatch):
    """OPS-AI-01: created_at is durable AI-ops clock; updates must not rewrite it."""
    path = _isolate_db(monkeypatch)
    from agent.db import db_save_widget_chat_history, get_connection

    db_save_widget_chat_history("sess-ca", [{"role": "user", "content": "a"}])
    conn = get_connection()
    row1 = conn.execute(
        "SELECT created_at, updated_at FROM widget_chat_sessions WHERE session_id = ?",
        ("sess-ca",),
    ).fetchone()
    assert row1["created_at"]
    assert row1["updated_at"]
    created = row1["created_at"]

    older = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    conn.execute(
        "UPDATE widget_chat_sessions SET created_at = ?, updated_at = ? WHERE session_id = ?",
        (older, older, "sess-ca"),
    )
    conn.commit()

    db_save_widget_chat_history(
        "sess-ca",
        [
            {"role": "user", "content": "a"},
            {"role": "assistant", "content": "b"},
        ],
    )
    row2 = conn.execute(
        "SELECT created_at, updated_at FROM widget_chat_sessions WHERE session_id = ?",
        ("sess-ca",),
    ).fetchone()
    assert row2["created_at"] == older
    assert row2["updated_at"] > older
    _cleanup_db(path)


def test_widget_created_at_backfill_on_legacy_schema(monkeypatch):
    """Legacy rows without created_at get backfilled from updated_at at migrate."""
    path = _isolate_db(monkeypatch)
    from agent.db import get_connection, _migrate_widget_chat_created_at

    conn = get_connection()
    # Simulate pre-migration row shape if column somehow empty
    conn.execute(
        "INSERT INTO widget_chat_sessions (session_id, history_json, created_at, updated_at) "
        "VALUES (?, ?, ?, ?)",
        ("sess-bf", "[]", "", "2026-07-10T12:00:00+00:00"),
    )
    conn.commit()
    _migrate_widget_chat_created_at(conn)
    conn.commit()
    row = conn.execute(
        "SELECT created_at FROM widget_chat_sessions WHERE session_id = ?",
        ("sess-bf",),
    ).fetchone()
    assert row["created_at"] == "2026-07-10T12:00:00+00:00"
    _cleanup_db(path)


def test_widget_history_expires(monkeypatch):
    path = _isolate_db(monkeypatch)
    from agent.db import db_get_widget_chat_history, db_save_widget_chat_history, get_connection

    db_save_widget_chat_history(
        "sess-exp",
        [{"role": "user", "content": "old"}],
    )
    old = (datetime.now(timezone.utc) - timedelta(hours=25)).isoformat()
    conn = get_connection()
    conn.execute(
        "UPDATE widget_chat_sessions SET updated_at = ? WHERE session_id = ?",
        (old, "sess-exp"),
    )
    conn.commit()
    assert db_get_widget_chat_history("sess-exp", ttl_sec=24 * 3600) is None
    row = conn.execute(
        "SELECT 1 FROM widget_chat_sessions WHERE session_id = ?",
        ("sess-exp",),
    ).fetchone()
    assert row is None
    _cleanup_db(path)


@pytest.mark.asyncio
async def test_history_survives_cache_clear(monkeypatch):
    """Simulates process restart: L1 cleared, L2 SQLite still has turns."""
    path = _isolate_db(monkeypatch)
    from agent.customer_agent import (
        _customer_sessions_cache,
        _load_widget_history,
        process_customer_message,
    )

    _customer_sessions_cache.clear()

    mock_client = MagicMock()
    mock_msg = MagicMock()
    mock_msg.content = [
        MagicMock(
            text=(
                '{"reply":"Eerste","lead":{"score":20,"intent":"low",'
                '"category":"informacja","reason":"hi"}}'
            )
        )
    ]
    mock_client.messages.create = AsyncMock(return_value=mock_msg)

    with patch("agent.customer_agent.client", mock_client):
        with patch("agent.customer_agent.Thread"):
            with patch("agent.customer_agent.LeadScorer") as mock_scorer_cls:
                mock_scorer_cls.return_value.compute.return_value = {
                    "lead_score": 15,
                    "intent": "low",
                    "category": "informacja",
                    "reason": "low",
                }
                await process_customer_message("sess-dur-1", "Eerste bericht")

    assert "sess-dur-1" in _customer_sessions_cache
    _customer_sessions_cache.clear()
    assert "sess-dur-1" not in _customer_sessions_cache

    restored = _load_widget_history("sess-dur-1")
    assert len(restored) == 2
    assert restored[0]["role"] == "user"
    assert restored[0]["content"] == "Eerste bericht"
    assert "sess-dur-1" in _customer_sessions_cache

    captured = []

    async def capture_create(*args, **kwargs):
        captured.append(list(kwargs.get("messages", [])))
        mock_msg.content = [
            MagicMock(
                text=(
                    '{"reply":"Tweede","lead":{"score":25,"intent":"low",'
                    '"category":"informacja","reason":"follow"}}'
                )
            )
        ]
        return mock_msg

    mock_client.messages.create = AsyncMock(side_effect=capture_create)
    _customer_sessions_cache.clear()

    with patch("agent.customer_agent.client", mock_client):
        with patch("agent.customer_agent.Thread"):
            with patch("agent.customer_agent.LeadScorer") as mock_scorer_cls:
                mock_scorer_cls.return_value.compute.return_value = {
                    "lead_score": 15,
                    "intent": "low",
                    "category": "informacja",
                    "reason": "low",
                }
                await process_customer_message("sess-dur-1", "Tweede bericht")

    assert len(captured) == 1
    assert len(captured[0]) == 3
    assert captured[0][0]["content"] == "Eerste bericht"
    assert captured[0][2]["content"] == "Tweede bericht"
    _cleanup_db(path)


@pytest.mark.asyncio
async def test_persist_failure_does_not_break_reply(monkeypatch):
    path = _isolate_db(monkeypatch)
    from agent.customer_agent import _customer_sessions_cache, process_customer_message

    _customer_sessions_cache.clear()
    mock_client = MagicMock()
    mock_msg = MagicMock()
    mock_msg.content = [
        MagicMock(
            text=(
                '{"reply":"Ok","lead":{"score":10,"intent":"low",'
                '"category":"informacja","reason":"x"}}'
            )
        )
    ]
    mock_client.messages.create = AsyncMock(return_value=mock_msg)

    with patch("agent.customer_agent.client", mock_client):
        with patch("agent.customer_agent.Thread"):
            with patch(
                "agent.db.db_save_widget_chat_history",
                side_effect=RuntimeError("disk full"),
            ):
                with patch("agent.customer_agent.LeadScorer") as mock_scorer_cls:
                    mock_scorer_cls.return_value.compute.return_value = {
                        "lead_score": 10,
                        "intent": "low",
                        "category": "informacja",
                        "reason": "low",
                    }
                    result = await process_customer_message(
                        "sess-fail-save", "hallo"
                    )

    assert result.get("reply") == "Ok"
    assert "sess-fail-save" in _customer_sessions_cache
    _cleanup_db(path)
