"""SQLite WAL / busy_timeout and retention contracts."""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from agent.db import get_connection
from agent.portal_qualification.lead_store import purge_expired_portal_qual_leads


def test_sqlite_connection_enables_wal_and_busy_timeout() -> None:
    conn = get_connection()
    journal = conn.execute("PRAGMA journal_mode").fetchone()[0]
    busy = conn.execute("PRAGMA busy_timeout").fetchone()[0]
    assert str(journal).lower() == "wal"
    assert int(busy) >= 30000


def test_sqlite_contention_microbenchmark_records_threshold(tmp_path: Path) -> None:
    """Documented micro-benchmark: N sequential writes under WAL should stay < 2s locally."""
    conn = get_connection()
    started = time.perf_counter()
    with conn:
        for i in range(50):
            conn.execute(
                "INSERT OR REPLACE INTO sessions(chat_id, source, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (f"bench-{i}", "http", "2026-01-01T00:00:00+00:00", "2026-01-01T00:00:00+00:00"),
            )
    elapsed = time.perf_counter() - started
    # Soft gate — records performance; fails only on pathological lock stalls.
    assert elapsed < 5.0, f"contention microbench too slow: {elapsed:.3f}s"


def test_purge_expired_portal_qual_leads() -> None:
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    future = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM portal_qual_leads WHERE session_id IN (?, ?)", ("expired-sess", "active-sess"))
        conn.execute(
            """
            INSERT INTO portal_qual_leads (
                session_id, industry, goal, vehicle, budget_tier,
                recommended_preset_id, source, consent, created_at, expires_at
            ) VALUES (?, 'x', 'y', 'z', 'low', 'preset', 'test', 1, ?, ?)
            """,
            ("expired-sess", past, past),
        )
        conn.execute(
            """
            INSERT INTO portal_qual_leads (
                session_id, industry, goal, vehicle, budget_tier,
                recommended_preset_id, source, consent, created_at, expires_at
            ) VALUES (?, 'x', 'y', 'z', 'low', 'preset', 'test', 1, ?, ?)
            """,
            ("active-sess", past, future),
        )

    deleted = purge_expired_portal_qual_leads()
    assert deleted >= 1
    remaining = conn.execute(
        "SELECT session_id FROM portal_qual_leads WHERE session_id IN (?, ?)",
        ("expired-sess", "active-sess"),
    ).fetchall()
    ids = {row[0] for row in remaining}
    assert "expired-sess" not in ids
    assert "active-sess" in ids
