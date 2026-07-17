"""Unit tests for publish_entry flow (INT-011)."""

import json
import os
import tempfile

import pytest

from agent.db import db_create_calendar_entry, db_get_calendar_entry, db_update_calendar_entry
from agent.nodes.content_calendar_node import publish_due_scheduled_entries, publish_entry


@pytest.fixture
def temp_db(monkeypatch):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr("agent.db.DB_PATH", path)
    import agent.db as db_mod

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def fb_env(monkeypatch):
    monkeypatch.setenv("FB_PAGE_ID", "491325420727745")
    monkeypatch.setenv("FB_ACCESS_TOKEN", "test-token")


def _create_approved_facebook_entry() -> str:
    entry_id, status = db_create_calendar_entry(
        {
            "platform": "facebook",
            "title": "Test",
            "body_nl": "Jadzia COI test body",
            "scheduled_at": "2026-07-01T10:00:00+00:00",
            "status": "draft",
        }
    )
    assert status == "success"
    db_update_calendar_entry(int(entry_id), {"status": "approved"})
    return entry_id


def test_publish_entry_not_found(temp_db, fb_env):
    result = publish_entry("999")
    assert result["status"] == "error"
    assert result["message"] == "Entry not found"


def test_publish_entry_wrong_platform(temp_db, fb_env):
    entry_id, _ = db_create_calendar_entry(
        {
            "platform": "tiktok",
            "title": "T",
            "body_nl": "body",
            "scheduled_at": "2026-07-01T10:00:00+00:00",
        }
    )
    db_update_calendar_entry(int(entry_id), {"status": "approved"})
    result = publish_entry(entry_id)
    assert result["status"] == "error"
    assert "facebook only" in result["message"]


def test_publish_entry_not_approved(temp_db, fb_env):
    entry_id, _ = db_create_calendar_entry(
        {
            "platform": "facebook",
            "title": "T",
            "body_nl": "body",
            "scheduled_at": "2026-07-01T10:00:00+00:00",
        }
    )
    result = publish_entry(entry_id)
    assert result["status"] == "error"
    assert "approved" in result["message"]


def test_publish_entry_no_fb_config(temp_db, monkeypatch):
    monkeypatch.delenv("FB_ACCESS_TOKEN", raising=False)
    entry_id = _create_approved_facebook_entry()
    result = publish_entry(entry_id)
    assert result["status"] == "error"
    assert "not configured" in result["message"]


def test_publish_entry_success(temp_db, fb_env, monkeypatch):
    entry_id = _create_approved_facebook_entry()

    def _mock_publish(row):
        return {"status": "success", "post_id": "491325420727745_42"}

    monkeypatch.setattr(
        "agent.nodes.content_calendar_node.publish_calendar_content",
        _mock_publish,
    )
    result = publish_entry(entry_id)
    assert result["status"] == "success"
    row = db_get_calendar_entry(int(entry_id))
    assert row["status"] == "published"
    assert row["fb_post_id"] == "491325420727745_42"
    parsed = json.loads(row["publish_result"])
    assert parsed["post_id"] == "491325420727745_42"


def test_publish_entry_failure_sets_failed(temp_db, fb_env, monkeypatch):
    entry_id = _create_approved_facebook_entry()
    monkeypatch.setattr(
        "agent.nodes.content_calendar_node.publish_calendar_content",
        lambda row: {"status": "error", "error": "Graph API down"},
    )
    result = publish_entry(entry_id)
    assert result["status"] == "error"
    row = db_get_calendar_entry(int(entry_id))
    assert row["status"] == "failed"


def test_publish_due_scheduled_entries_skips_future(temp_db, fb_env, monkeypatch):
    entry_id = _create_approved_facebook_entry()
    db_update_calendar_entry(
        int(entry_id),
        {"scheduled_publish_at": "2099-01-01T10:00:00+00:00"},
    )
    calls: list[str] = []

    def _mock_publish_entry(eid: str) -> dict:
        calls.append(eid)
        return {"status": "success", "post_id": "x"}

    monkeypatch.setattr(
        "agent.nodes.content_calendar_node.publish_entry",
        _mock_publish_entry,
    )
    count = publish_due_scheduled_entries()
    assert count == 0
    assert calls == []


def test_publish_due_scheduled_entries_publishes_past(temp_db, fb_env, monkeypatch):
    entry_id = _create_approved_facebook_entry()
    db_update_calendar_entry(
        int(entry_id),
        {"scheduled_publish_at": "2020-01-01T10:00:00+00:00"},
    )

    monkeypatch.setattr(
        "agent.commander.publish.publish_calendar_entry_system",
        lambda entry_id, expected_version=None: {"status": "success", "post_id": "491325420727745_1"},
    )
    count = publish_due_scheduled_entries()
    assert count == 1
