"""Tests for publish failure handling (Phase B)."""

import json
import os
from unittest.mock import patch

import pytest

from agent.publishers.facebook import parse_publish_error


def test_parse_publish_error_expired_token():
    result = {
        "status": "error",
        "details": json.dumps({
            "error": {
                "message": "Session has expired",
                "code": 190,
                "error_subcode": 463,
            }
        }),
    }
    msg = parse_publish_error(result)
    assert "wygasł" in msg.lower() or "Token" in msg


def test_parse_publish_error_user_token():
    result = {
        "status": "error",
        "details": json.dumps({
            "error": {
                "message": "publish_actions are not available",
                "code": 200,
            }
        }),
    }
    msg = parse_publish_error(result)
    assert "Page Token" in msg


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


def test_publish_failure_sends_telegram(temp_db, monkeypatch):
    from agent.commander.publish import publish_calendar_entry
    from agent.db import db_create_calendar_entry, db_update_calendar_entry

    monkeypatch.setattr("agent.commander.publish.is_facebook_configured", lambda: True)
    monkeypatch.setattr(
        "agent.commander.publish.publish_calendar_content",
        lambda row: {
            "status": "error",
            "error": "400",
            "details": json.dumps({"error": {"code": 190, "message": "expired"}}),
        },
    )
    alerts = []
    monkeypatch.setattr(
        "agent.customer_agent._send_telegram_alert_sync",
        lambda msg: alerts.append(msg),
    )

    eid_str, _ = db_create_calendar_entry({
        "platform": "facebook",
        "title": "Fail post",
        "body_nl": "NL",
        "scheduled_at": "2026-12-01T10:00:00Z",
        "status": "approved",
    })
    eid = int(eid_str)

    result = publish_calendar_entry(str(eid), {"sub": "test", "role": "dowodca"})
    assert result["status"] == "error"
    assert "message_pl" in result
    assert len(alerts) == 1
    assert "Fail post" in alerts[0]


def test_publish_retry_from_failed_status(temp_db, monkeypatch):
    from agent.commander.publish import publish_calendar_entry
    from agent.db import db_create_calendar_entry, db_update_calendar_entry, db_get_calendar_entry

    monkeypatch.setattr("agent.commander.publish.is_facebook_configured", lambda: True)
    monkeypatch.setattr(
        "agent.commander.publish.publish_calendar_content",
        lambda row: {"status": "success", "post_id": "page_123"},
    )
    monkeypatch.setattr("agent.commander.publish_errors.notify_publish_failure", lambda *a, **k: None)

    eid_str, _ = db_create_calendar_entry({
        "platform": "facebook",
        "title": "Retry",
        "body_nl": "NL",
        "scheduled_at": "2026-12-01T10:00:00Z",
        "status": "failed",
    })
    eid = int(eid_str)
    db_update_calendar_entry(eid, {
        "publish_result": json.dumps({"status": "error", "error": "old"}),
    })

    result = publish_calendar_entry(str(eid), {"sub": "test", "role": "dowodca"})
    assert result["status"] == "success"
    row = db_get_calendar_entry(eid)
    assert row["status"] == "published"
