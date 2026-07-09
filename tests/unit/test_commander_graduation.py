"""Graduation / HOTL tests (N3, CE-08)."""

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


def test_graduation_hitl_by_default(temp_db):
    from agent.commander.graduation import graduation_status

    status = graduation_status("fb_post_approve")
    assert status["mode"] == "HITL"


def test_is_hotl_mode_false_without_threshold(temp_db):
    from agent.commander.graduation import is_hotl_mode

    assert is_hotl_mode("fb_post_approve") is False


def test_feedback_records_confidence(temp_db):
    from agent.commander.graduation import record_feedback, graduation_status

    record_feedback(
        "fb_post_approve",
        "approval",
        {"confidence": 0.95},
        "norbert",
    )
    stats = graduation_status("fb_post_approve")["stats"]
    assert stats.get("confidence_avg", 0) >= 0.9
