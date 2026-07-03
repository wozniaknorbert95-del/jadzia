"""Tests for weekly COI brief node (S3-02)."""

import os
from unittest.mock import patch

import pytest

from agent.db import db_save_analytics_snapshot, db_upsert_order
from agent.nodes.brief_node import build_weekly_brief, send_weekly_brief


@pytest.fixture
def temp_db(monkeypatch):
    import tempfile
    from datetime import datetime, timezone

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr("agent.db.DB_PATH", path)
    import agent.db as db_mod

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    db_upsert_order(
        {
            "order_id": "9001",
            "status": "completed",
            "items": [{"sku": "NS-001", "qty": 1, "price": 199.0}],
            "customer": {"email": "a@test.nl", "name": "Test"},
            "total_gross": 199.0,
            "payment_id": "mollie-1",
            "created_at": now,
            "updated_at": now,
        }
    )
    db_save_analytics_snapshot(
        {
            "period": "last_7_days",
            "generated_at": now,
            "sync_status": "success",
            "sources": {"zzpackage": {"sessions": 5, "conversions": 1}},
            "errors": [],
        }
    )
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


def test_build_weekly_brief_includes_orders_and_ga4(temp_db):
    text = build_weekly_brief()
    assert "Orders (7d):" in text
    assert "GA4" in text
    assert "wizard sessions=5" in text


def test_send_weekly_brief_calls_telegram(temp_db):
    with patch("agent.customer_agent._send_telegram_alert_sync") as mock_send:
        ok = send_weekly_brief()
    assert ok is True
    mock_send.assert_called_once()
    assert "weekly brief" in mock_send.call_args[0][0].lower()
