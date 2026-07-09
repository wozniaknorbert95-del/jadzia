"""Tests for COI Commander API (control plane)."""

import os
from contextlib import contextmanager
from unittest.mock import patch

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from api.app import create_app

JWT_SECRET_VALUE = "test-secret-commander"


@contextmanager
def jwt_env():
    with patch.dict(os.environ, {"JWT_SECRET": JWT_SECRET_VALUE}, clear=False), patch(
        "api.dependencies.JWT_SECRET",
        JWT_SECRET_VALUE,
    ):
        yield


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
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def client():
    return TestClient(create_app())


def _auth_headers(role: str = "dowodca") -> dict[str, str]:
    token = pyjwt.encode(
        {"sub": "norbert", "role": role},
        JWT_SECRET_VALUE,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


def test_commander_queue_requires_jwt(client, temp_db):
    with jwt_env():
        r = client.get("/api/v1/commander/queue")
    assert r.status_code == 401


def test_commander_queue_empty(client, temp_db):
    with jwt_env():
        r = client.get("/api/v1/commander/queue", headers=_auth_headers())
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert data.get("severity_policy_ref") == "D0.8"


def test_commander_priorities_today(client, temp_db):
    with jwt_env():
        r = client.get("/api/v1/commander/priorities/today", headers=_auth_headers())
    assert r.status_code == 200
    assert "priorities" in r.json()


def test_commander_audit_append_and_list(client, temp_db):
    from agent.commander.audit import append_audit

    with jwt_env():
        row_id = append_audit(
            actor_id="norbert",
            actor_role="dowodca",
            action="test_action",
            source="pytest",
        )
        assert row_id is not None
        r = client.get("/api/v1/commander/audit-log", headers=_auth_headers())
        assert r.status_code == 200
        assert r.json()["total"] >= 1


def test_commander_feedback_graduation(client, temp_db):
    with jwt_env():
        r = client.post(
            "/api/v1/commander/feedback",
            json={
                "action_type": "fb_post_approve",
                "feedback_type": "approval",
                "payload": {},
            },
            headers=_auth_headers(),
        )
        assert r.status_code == 200
        assert r.json()["mode"] == "HITL"


def test_viewer_cannot_pause_agent(client, temp_db):
    with jwt_env():
        r = client.post(
            "/api/v1/agents/marketing/pause",
            headers=_auth_headers(role="viewer"),
        )
    assert r.status_code == 403


def test_deeplink_mint_and_verify(client, temp_db):
    from agent.db import db_commander_create_ticket

    ticket_id = db_commander_create_ticket("Test", "desc", "pytest")
    assert ticket_id

    with jwt_env():
        r = client.post(
            "/api/v1/commander/deeplink",
            json={"ticket_id": ticket_id, "base_url": "http://localhost:8000"},
            headers=_auth_headers(),
        )
        assert r.status_code == 200
        assert "url" in r.json()


def test_agents_list(client, temp_db):
    with jwt_env():
        r = client.get("/api/v1/agents", headers=_auth_headers())
    assert r.status_code == 200
    assert r.json()["total"] >= 1


def test_orders_and_leads(client, temp_db):
    with jwt_env():
        orders = client.get("/api/v1/orders", headers=_auth_headers())
        leads = client.get("/api/v1/leads", headers=_auth_headers())
    assert orders.status_code == 200
    assert leads.status_code == 200


def test_authz_has_scope():
    from agent.commander.authz import has_scope

    assert has_scope({"role": "dowodca"}, "agents:pause")
    assert not has_scope({"role": "viewer"}, "agents:pause")
    assert has_scope({"role": "viewer"}, "commander:read")
