"""MKT-BRAIN-PRO F3 — Brain Bus VCMS health + CEO stub."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from agent.db import (
    db_list_active_quality_flags,
    db_list_brain_events,
    get_connection,
)
from agent.marketing.brain_bus import ingest_brain_bus_event, publish_ceo_priority_stub
from agent.marketing.brain_events import process_brain_events
from agent.marketing.circuit_breakers import evaluate_breakers
from api.app import create_app


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
    try:
        if hasattr(db_mod._local, "conn") and db_mod._local.conn:
            db_mod._local.conn.close()
            db_mod._local.conn = None
        os.unlink(path)
    except OSError:
        pass


def test_degraded_sets_flag_ticket_and_cb(temp_db, monkeypatch):
    monkeypatch.setenv("MB_MODE", "propose")  # isolate CB_ECOSYSTEM from shadow
    enq = ingest_brain_bus_event(
        {
            "event_type": "system.health.degraded",
            "source_brain": "vcms",
            "payload": {"conflicts": 2, "summary": "conflicts.md red"},
            "correlation_id": "test-corr-1",
        }
    )
    assert enq["ok"] is True
    with patch("agent.marketing.brain_bus._send_bus_telegram", return_value=True):
        result = process_brain_events(limit=5, send_telegram=True)
    assert result["done"] >= 1
    flags = db_list_active_quality_flags()
    assert any(
        f.get("source") == "vcms" and f.get("flag_type") == "ecosystem_red" for f in flags
    )
    trips = evaluate_breakers()
    assert any(t.breaker_id == "CB_ECOSYSTEM" for t in trips)
    conn = get_connection()
    ticket = conn.execute(
        "SELECT id, title FROM commander_tickets WHERE source = 'brain_bus' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert ticket is not None
    assert "Ecosystem RED" in ticket["title"]


def test_recovered_clears_ecosystem_flag(temp_db, monkeypatch):
    monkeypatch.setenv("MB_MODE", "propose")
    ingest_brain_bus_event(
        {
            "event_type": "system.health.degraded",
            "source_brain": "vcms",
            "payload": {"conflicts": 1, "summary": "x"},
        }
    )
    with patch("agent.marketing.brain_bus._send_bus_telegram", return_value=False):
        process_brain_events(limit=5, send_telegram=False)
    ingest_brain_bus_event(
        {
            "event_type": "system.health.recovered",
            "source_brain": "vcms",
            "payload": {"conflicts": 0},
        }
    )
    process_brain_events(limit=5, send_telegram=False)
    flags = [
        f
        for f in db_list_active_quality_flags()
        if f.get("flag_type") == "ecosystem_red" and f.get("active")
    ]
    assert flags == []
    trips = evaluate_breakers()
    assert not any(t.breaker_id == "CB_ECOSYSTEM" for t in trips)


def test_ceo_priority_stub(temp_db):
    with patch("agent.marketing.brain_bus._send_bus_telegram", return_value=True):
        out = publish_ceo_priority_stub(
            "Focus: Instant Form €10",
            week="2026-W29",
            process_now=True,
            send_telegram=True,
        )
    assert out.get("ok") is True
    events = db_list_brain_events(limit=5)
    assert any(e.get("event_type") == "ceo.priority" for e in events)
    flags = db_list_active_quality_flags()
    assert any(f.get("flag_type") == "ceo_priority" for f in flags)


def test_brain_bus_api_auth(temp_db, monkeypatch):
    monkeypatch.setenv("BRAIN_BUS_SECRET", "bus-secret-f3")
    monkeypatch.setenv("JWT_SECRET", "test-jwt-f3")
    with patch("api.routes.brain_bus.require_secrets_enabled", return_value=False), patch(
        "agent.marketing.brain_bus._send_bus_telegram",
        return_value=False,
    ):
        client = TestClient(create_app())
        denied = client.post(
            "/api/v1/brain-bus/events",
            json={
                "event_type": "system.health.degraded",
                "source_brain": "vcms",
                "payload": {"conflicts": 1, "summary": "auth test"},
            },
        )
        assert denied.status_code == 401
        ok = client.post(
            "/api/v1/brain-bus/events",
            headers={"X-Brain-Bus-Secret": "bus-secret-f3"},
            json={
                "event_type": "system.health.degraded",
                "source_brain": "vcms",
                "payload": {"conflicts": 3, "summary": "scan red"},
                "correlation_id": "api-test",
            },
        )
    assert ok.status_code == 200
    body = ok.json()
    assert body["ok"] is True
    assert body["processed"]["done"] >= 1
