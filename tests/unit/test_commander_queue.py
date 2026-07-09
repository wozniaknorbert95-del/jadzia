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


def test_queue_publish_failed(temp_db):
    import json

    from agent.commander.queue import build_queue
    from agent.db import db_create_calendar_entry, db_update_calendar_entry

    eid_str, _ = db_create_calendar_entry({
        "platform": "facebook",
        "title": "Broken post",
        "body_nl": "NL",
        "scheduled_at": "2026-12-01T10:00:00Z",
        "status": "failed",
    })
    db_update_calendar_entry(int(eid_str), {
        "publish_result": json.dumps({
            "status": "error",
            "details": json.dumps({"error": {"code": 190, "message": "expired"}}),
        }),
    })
    items = build_queue()
    failed = [i for i in items if i["queue_type"] == "publish_failed"]
    assert len(failed) == 1
    assert failed[0]["severity"] == "CRITICAL"
    assert "entry_id" in failed[0]["payload"]
