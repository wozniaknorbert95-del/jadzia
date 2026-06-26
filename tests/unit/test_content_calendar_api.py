"""Tests for content calendar API (INT-010)."""

import os
from unittest.mock import patch

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from api.app import create_app

JWT_SECRET_VALUE = "test-secret-calendar"


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


def _auth_headers() -> dict[str, str]:
    token = pyjwt.encode({"sub": "test"}, JWT_SECRET_VALUE, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


def _valid_payload() -> dict:
    return {
        "platform": "facebook",
        "title": "Wizard launch",
        "body_nl": "Nieuwe wizard features voor ZZP.",
        "scheduled_at": "2026-08-01T09:00:00+00:00",
    }


def test_content_calendar_create_and_list(client, temp_db):
    with patch.dict(os.environ, {"JWT_SECRET": JWT_SECRET_VALUE}, clear=False), patch(
        "api.dependencies.JWT_SECRET",
        JWT_SECRET_VALUE,
    ):
        create = client.post(
            "/api/v1/content-calendar",
            json=_valid_payload(),
            headers=_auth_headers(),
        )
        assert create.status_code == 200
        assert create.json()["sync_status"] == "success"

        listed = client.get("/api/v1/content-calendar", headers=_auth_headers())
        assert listed.status_code == 200
        assert listed.json()["total"] == 1


def test_content_calendar_requires_jwt(client, temp_db):
    with patch.dict(os.environ, {"JWT_SECRET": JWT_SECRET_VALUE}, clear=False), patch(
        "api.dependencies.JWT_SECRET",
        JWT_SECRET_VALUE,
    ):
        r = client.get("/api/v1/content-calendar")
    assert r.status_code == 401


def test_content_calendar_patch_status(client, temp_db):
    with patch.dict(os.environ, {"JWT_SECRET": JWT_SECRET_VALUE}, clear=False), patch(
        "api.dependencies.JWT_SECRET",
        JWT_SECRET_VALUE,
    ):
        created = client.post(
            "/api/v1/content-calendar",
            json=_valid_payload(),
            headers=_auth_headers(),
        )
        entry_id = created.json()["entry_id"]
        patched = client.patch(
            f"/api/v1/content-calendar/{entry_id}",
            json={"status": "approved"},
            headers=_auth_headers(),
        )
        assert patched.status_code == 200
        assert patched.json()["status"] == "approved"
