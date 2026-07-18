"""COI-CS-01/02 queue mapping + API tests."""

import os
from contextlib import contextmanager
from unittest.mock import patch

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from agent.commander.cs_followup import spawn_cs_followup_ticket
from agent.commander.queue import build_queue
from api.app import create_app

JWT_SECRET_VALUE = "test-secret-cs02"


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

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
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


def test_spawn_cs_followup_maps_to_queue(temp_db):
    tid = spawn_cs_followup_ticket(order_id="ORD-CS-1", customer_hint="test@flexgrafik.nl")
    assert tid is not None
    items = build_queue()
    cs = [i for i in items if i["queue_type"] == "cs_followup"]
    assert len(cs) >= 1
    assert cs[0]["severity"] == "ACTION"
    assert cs[0]["payload"]["ticket_id"] == tid
    assert "acked" in cs[0]["available_actions"]


def test_cs_followup_api_spawn_and_disposition(client, temp_db):
    with jwt_env():
        r = client.post(
            "/api/v1/commander/cs/followup",
            json={"order_id": "ORD-CS-API", "customer_hint": "cs@test.nl", "note": "dogfood"},
            headers=_auth_headers(),
        )
        assert r.status_code == 200
        tid = r.json()["ticket_id"]
        assert r.json()["queue_type"] == "cs_followup"

        q = client.get("/api/v1/commander/queue", headers=_auth_headers())
        assert q.status_code == 200
        cs = [i for i in q.json()["items"] if i["queue_type"] == "cs_followup"]
        assert any(i["payload"]["ticket_id"] == tid for i in cs)

        d = client.post(
            f"/api/v1/commander/tickets/{tid}/disposition",
            json={"disposition": "acked"},
            headers=_auth_headers(),
        )
        assert d.status_code == 200
        assert d.json()["disposition"] == "acked"

        q2 = client.get("/api/v1/commander/queue", headers=_auth_headers())
        cs2 = [i for i in q2.json()["items"] if i.get("payload", {}).get("ticket_id") == tid]
        assert cs2 == []


def test_cs_followup_api_requires_auth(client, temp_db):
    with jwt_env():
        r = client.post(
            "/api/v1/commander/cs/followup",
            json={"order_id": "ORD-X"},
        )
    assert r.status_code == 401
