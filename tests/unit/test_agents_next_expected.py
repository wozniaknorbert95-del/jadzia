"""Agents registry — next_expected_run truth (Wave B)."""

from datetime import datetime, timedelta, timezone
import os

import pytest

from agent.commander.agents_registry import _next_expected_run, list_agents
from agent.db import db_commander_upsert_agent_state


@pytest.fixture
def temp_db(monkeypatch):
    import tempfile

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr("agent.db.DB_PATH", path)
    import agent.db as db_mod

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
    yield path


def test_next_expected_run_from_last_run():
    last = datetime(2026, 7, 22, 10, 0, 0, tzinfo=timezone.utc)
    nxt = _next_expected_run(last.isoformat().replace("+00:00", "Z"), 3600)
    assert nxt == "2026-07-22T11:00:00Z"


def test_next_expected_run_none_without_last():
    assert _next_expected_run(None, 3600) is None
    assert _next_expected_run("2026-07-22T10:00:00Z", 0) is None


def test_list_agents_exposes_next_expected(temp_db):
    last = (datetime.now(timezone.utc) - timedelta(minutes=10)).replace(microsecond=0)
    db_commander_upsert_agent_state(
        "marketing",
        {
            "status": "LIVE",
            "expected_interval_seconds": 3600,
            "last_run_at": last.isoformat().replace("+00:00", "Z"),
            "held_count": 0,
        },
    )
    agents = {a["agent_id"]: a for a in list_agents()}
    m = agents["marketing"]
    assert m["next_expected_run"]
    assert m["next_expected_run"].endswith("Z")
