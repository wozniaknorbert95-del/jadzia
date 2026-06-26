"""Tests for POST /api/v1/leads (INT-004)."""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from api.app import create_app


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
def client():
    return TestClient(create_app())


def _valid_payload() -> dict:
    return {
        "email": "lead@example.nl",
        "name": "Lead Test",
        "source": "game",
        "consent_status": True,
        "game_score": 99,
        "reward_tier": "bronze",
    }


def test_leads_api_success(client, temp_db):
    r = client.post("/api/v1/leads", json=_valid_payload())
    assert r.status_code == 200
    data = r.json()
    assert data["sync_status"] == "success"
    assert data["lead_id"] == "1"


def test_leads_api_rejects_no_consent(client, temp_db):
    bad = _valid_payload()
    bad["consent_status"] = False
    r = client.post("/api/v1/leads", json=bad)
    assert r.status_code == 200
    assert r.json()["sync_status"] == "fail"


def test_leads_api_invalid_email(client, temp_db):
    bad = _valid_payload()
    bad["email"] = "not-an-email"
    r = client.post("/api/v1/leads", json=bad)
    assert r.status_code == 422


def test_leads_api_key_required(monkeypatch, client, temp_db):
    monkeypatch.setenv("LEADS_API_KEY", "test-leads-key")
    import api.routes.leads as leads_mod

    monkeypatch.setattr(leads_mod, "LEADS_API_KEY", "test-leads-key")

    r = client.post("/api/v1/leads", json=_valid_payload())
    assert r.status_code == 401

    r = client.post(
        "/api/v1/leads",
        json=_valid_payload(),
        headers={"X-API-Key": "test-leads-key"},
    )
    assert r.status_code == 200
    assert r.json()["sync_status"] == "success"
