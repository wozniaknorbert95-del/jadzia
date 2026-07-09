"""Tests for publish version lock and worker path (N13)."""

import os
from contextlib import contextmanager
from unittest.mock import patch

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from api.app import create_app

JWT_SECRET_VALUE = "test-secret-publish"


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


def _headers(role: str = "dowodca") -> dict:
    token = pyjwt.encode(
        {"sub": "test", "role": role},
        JWT_SECRET_VALUE,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


def _create_approved(monkeypatch):
    from agent.db import db_create_calendar_entry, db_update_calendar_entry

    eid_str, _ = db_create_calendar_entry(
        {
            "platform": "facebook",
            "title": "Test",
            "body_nl": "Body",
            "scheduled_at": "2026-12-01T10:00:00Z",
            "status": "approved",
        }
    )
    eid = int(eid_str)
    db_update_calendar_entry(eid, {"scheduled_publish_at": "2020-01-01T10:00:00Z"})
    return eid


def test_publish_version_conflict(client, temp_db, monkeypatch):
    with jwt_env():
        monkeypatch.setattr(
            "agent.commander.publish.is_facebook_configured",
            lambda: True,
        )
        monkeypatch.setattr(
            "agent.commander.publish.publish_calendar_content",
            lambda row: {"status": "success", "post_id": "fb123"},
        )
        eid = _create_approved(monkeypatch)
        r = client.post(
            f"/api/v1/content-calendar/{eid}/publish",
            json={"version": 999},
            headers=_headers(),
        )
        assert r.status_code == 409


def test_worker_publish_uses_system_path(temp_db, monkeypatch):
    from agent.db import db_commander_list_audit
    from agent.nodes.content_calendar_node import publish_due_scheduled_entries

    monkeypatch.setattr(
        "agent.nodes.content_calendar_node.is_facebook_configured",
        lambda: True,
    )
    monkeypatch.setattr(
        "agent.commander.publish.is_facebook_configured",
        lambda: True,
    )
    monkeypatch.setattr(
        "agent.commander.publish.publish_calendar_content",
        lambda row: {"status": "success", "post_id": "fb456"},
    )
    _create_approved(monkeypatch)
    count = publish_due_scheduled_entries()
    assert count >= 1
    audit = db_commander_list_audit(limit=5)
    assert any(a["action"] == "publish" for a in audit)
