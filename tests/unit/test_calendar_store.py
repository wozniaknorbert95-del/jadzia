"""Tests for content_calendar table (INT-010)."""

import os
import tempfile

import pytest

from agent.db import (
    db_create_calendar_entry,
    db_get_calendar_entry,
    db_list_calendar_entries,
    db_update_calendar_entry,
)


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


def _sample_entry() -> dict:
    return {
        "platform": "facebook",
        "title": "Nieuwe case study",
        "body_nl": "Bekijk ons laatste project voor een ZZP'er.",
        "scheduled_at": "2026-07-01T10:00:00+00:00",
        "status": "draft",
    }


def test_db_create_calendar_entry(temp_db):
    entry_id, status = db_create_calendar_entry(_sample_entry())
    assert status == "success"
    assert entry_id == "1"

    row = db_get_calendar_entry(1)
    assert row is not None
    assert row["platform"] == "facebook"
    assert row["status"] == "draft"


def test_db_list_calendar_entries_filter(temp_db):
    db_create_calendar_entry(_sample_entry())
    tiktok = _sample_entry()
    tiktok["platform"] = "tiktok"
    db_create_calendar_entry(tiktok)

    fb_only = db_list_calendar_entries(platform="facebook")
    assert len(fb_only) == 1
    assert fb_only[0]["platform"] == "facebook"


def test_db_update_calendar_entry_status(temp_db):
    db_create_calendar_entry(_sample_entry())
    ok = db_update_calendar_entry(1, {"status": "pending_approval"})
    assert ok is True
    row = db_get_calendar_entry(1)
    assert row["status"] == "pending_approval"
