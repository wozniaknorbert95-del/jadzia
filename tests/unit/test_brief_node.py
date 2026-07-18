"""Tests for weekly COI brief node (S3-02 + COI-STRATEGY-HITL-01)."""

import os
from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from agent.db import (
    db_commander_list_tickets,
    db_record_revenue_classification,
    db_save_analytics_snapshot,
    db_upsert_order,
)
from agent.nodes.brief_node import (
    build_weekly_brief,
    collect_weekly_metrics,
    propose_brief_recommendations,
    send_weekly_brief,
    spawn_brief_hitl_tickets,
)


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

    now = datetime.now(UTC).replace(microsecond=0).isoformat()
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
    db_record_revenue_classification(
        "order",
        "9001",
        "real",
        "production_order_evidence",
    )
    db_upsert_order(
        {
            "order_id": "SMOKE-1",
            "status": "completed",
            "items": [{"sku": "TEST", "qty": 1, "price": 999.0}],
            "customer": {"email": "smoke@test.nl", "name": "Smoke"},
            "total_gross": 999.0,
            "payment_id": "tr_test_smoke",
        }
    )
    db_record_revenue_classification(
        "order",
        "SMOKE-1",
        "test",
        "known_test_order_pattern",
    )
    db_upsert_order(
        {
            "order_id": "UNK-1",
            "status": "processing",
            "items": [{"sku": "X", "qty": 1, "price": 50.0}],
            "customer": {"email": "u@test.nl", "name": "Unk"},
            "total_gross": 50.0,
            "payment_id": "tr_unk",
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
    assert "Orders KPI-eligible (7d): 1 | EUR 199.00" in text
    assert "Orders excluded: test=1 unknown=1" in text
    assert "GA4" in text
    assert "wizard sessions=5" in text


def test_propose_brief_recommendations_includes_unknown_and_hygiene(temp_db):
    metrics = collect_weekly_metrics()
    recs = propose_brief_recommendations(metrics)
    codes = {r["code"] for r in recs}
    assert "triage_unknown_orders" in codes
    assert "ops_fb_hygiene_nudge" in codes
    assert len(recs) <= 3


def test_spawn_brief_hitl_tickets_creates_open_commander_tickets(temp_db):
    ids = spawn_brief_hitl_tickets()
    assert ids
    open_tickets = db_commander_list_tickets(status="open", limit=50)
    brief = [t for t in open_tickets if t.get("source") == "brief_hitl"]
    assert len(brief) == len(ids)
    # Idempotent: second spawn creates no duplicates
    ids2 = spawn_brief_hitl_tickets()
    assert ids2 == []
    brief2 = [
        t
        for t in db_commander_list_tickets(status="open", limit=50)
        if t.get("source") == "brief_hitl"
    ]
    assert len(brief2) == len(brief)


def test_send_weekly_brief_calls_telegram_and_spawns_hitl(temp_db):
    with patch("agent.customer_agent._send_telegram_alert_sync") as mock_send:
        ok = send_weekly_brief()
    assert ok is True
    mock_send.assert_called_once()
    assert "weekly brief" in mock_send.call_args[0][0].lower()
    brief = [
        t
        for t in db_commander_list_tickets(status="open", limit=50)
        if t.get("source") == "brief_hitl"
    ]
    assert brief
