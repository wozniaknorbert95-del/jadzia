"""Queue completeness tests (CE-01, N4/N8)."""

import os
import pytest


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


def test_queue_includes_severity_policy_ref(temp_db):
    from agent.commander.queue import build_queue

    items = build_queue()
    assert isinstance(items, list)
    for item in items:
        assert item.get("severity_policy_ref") == "D0.8"


def test_queue_wp_ticket(temp_db):
    from agent.commander.queue import build_queue
    from agent.db import db_commander_create_ticket

    db_commander_create_ticket("WP fix", "header broken", "telegram")
    items = build_queue()
    types = {i["queue_type"] for i in items}
    assert "wp_ticket" in types
