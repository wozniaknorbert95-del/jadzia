"""Authz scope matrix tests (N7)."""

import os
from contextlib import contextmanager
from unittest.mock import patch

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from api.app import create_app

JWT_SECRET_VALUE = "test-secret-authz"


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


@pytest.fixture
def client():
    return TestClient(create_app())


def _headers(role: str) -> dict:
    token = pyjwt.encode(
        {"sub": role, "role": role},
        JWT_SECRET_VALUE,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


def test_delegat_can_publish_route(client, temp_db, monkeypatch):
    from agent.db import db_create_calendar_entry

    with jwt_env():
        monkeypatch.setattr(
            "agent.commander.publish.is_facebook_configured",
            lambda: True,
        )
        monkeypatch.setattr(
            "agent.commander.publish.publish_calendar_content",
            lambda row: {"status": "success", "post_id": "x"},
        )
        eid_str, _ = db_create_calendar_entry(
            {
                "platform": "facebook",
                "title": "T",
                "body_nl": "B",
                "scheduled_at": "2026-12-01T10:00:00Z",
                "status": "approved",
            }
        )
        r = client.post(
            f"/api/v1/content-calendar/{eid_str}/publish",
            headers=_headers("delegat"),
        )
        assert r.status_code == 200


def test_delegat_cannot_pause(client, temp_db):
    with jwt_env():
        r = client.post(
            "/api/v1/agents/marketing/pause",
            headers=_headers("delegat"),
        )
    assert r.status_code == 403


def test_viewer_cannot_patch_calendar(client, temp_db):
    from agent.db import db_create_calendar_entry

    with jwt_env():
        eid_str, _ = db_create_calendar_entry(
            {
                "platform": "facebook",
                "title": "T",
                "body_nl": "B",
                "scheduled_at": "2026-12-01T10:00:00Z",
                "status": "draft",
            }
        )
        r = client.patch(
            f"/api/v1/content-calendar/{eid_str}",
            json={"status": "approved"},
            headers=_headers("viewer"),
        )
    assert r.status_code == 403


def test_viewer_cannot_read_audit(client, temp_db):
    with jwt_env():
        r = client.get("/api/v1/commander/audit-log", headers=_headers("viewer"))
    assert r.status_code == 403


def test_delegat_cannot_patch_settings(client, temp_db):
    with jwt_env():
        r = client.patch(
            "/api/v1/commander/settings",
            json={"delegat_email": "x@test.nl"},
            headers=_headers("delegat"),
        )
    assert r.status_code == 403
