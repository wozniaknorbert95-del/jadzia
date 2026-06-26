"""Tests for content_calendar_node (INT-010)."""

import os
import tempfile

import pytest

from agent.nodes.content_calendar_node import (
    create_calendar_entry,
    list_calendar_entries,
    update_calendar_entry,
)
from core.models import ContentCalendarCreateRequest, ContentCalendarUpdateRequest


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


def _payload() -> ContentCalendarCreateRequest:
    return ContentCalendarCreateRequest(
        platform="tiktok",
        title="ZZP tip van de week",
        body_nl="Start vandaag met je online zichtbaarheid.",
        scheduled_at="2026-07-15T14:00:00+00:00",
    )


def test_create_calendar_entry_success(temp_db):
    result = create_calendar_entry(_payload())
    assert result.sync_status == "success"
    assert result.entry_id == "1"


def test_list_calendar_entries(temp_db):
    create_calendar_entry(_payload())
    listed = list_calendar_entries()
    assert listed.total == 1
    assert listed.entries[0].platform == "tiktok"


def test_update_calendar_entry(temp_db):
    created = create_calendar_entry(_payload())
    updated = update_calendar_entry(
        created.entry_id,
        ContentCalendarUpdateRequest(status="pending_approval"),
    )
    assert updated is not None
    assert updated.status == "pending_approval"


def test_pending_approval_sends_alert(temp_db, monkeypatch):
    alerts: list[str] = []

    def _capture(msg: str) -> None:
        alerts.append(msg)

    monkeypatch.setattr(
        "agent.customer_agent._send_telegram_alert_sync",
        _capture,
    )
    created = create_calendar_entry(_payload())
    update_calendar_entry(
        created.entry_id,
        ContentCalendarUpdateRequest(status="pending_approval"),
    )
    import time

    time.sleep(0.2)
    assert any("CONTENT CALENDAR" in a for a in alerts)
