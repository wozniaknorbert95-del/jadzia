"""MKT-BRAIN-PRO F2 — governance + circuit breakers."""

from __future__ import annotations

import os
from unittest.mock import patch

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from agent.marketing.circuit_breakers import evaluate_breakers, is_execute_allowed
from agent.marketing.decision_engine import run_decision_cycle
from agent.marketing.governance import execute_action, mint_approval_token
from api.app import create_app

JWT_SECRET_VALUE = "test-secret-mb-f2-governance-ok"


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


def test_cb_shadow_trips(temp_db, monkeypatch):
    monkeypatch.setenv("MB_MODE", "shadow")
    trips = evaluate_breakers()
    assert any(t.breaker_id == "CB_SHADOW" for t in trips)
    status = is_execute_allowed()
    assert status["allowed"] is False


def test_execute_denied_in_shadow(temp_db, monkeypatch):
    monkeypatch.setenv("MB_MODE", "shadow")
    with patch("agent.marketing.decision_engine.get_mb_mode", return_value="shadow"):
        cycle = run_decision_cycle()
    action_id = cycle["records"][0]["action_id"]
    tok = mint_approval_token(action_id)
    # Even with valid token, CB_SHADOW blocks
    with patch("agent.marketing.governance.get_mb_mode", return_value="shadow"):
        with patch(
            "agent.marketing.circuit_breakers.get_mb_mode",
            return_value="shadow",
        ):
            result = execute_action(action_id, tok["approval_token"])
    assert result["ok"] is False
    assert result.get("error") in ("circuit_breaker", "shadow_mode")


def test_execute_api_requires_auth(temp_db):
    with patch.dict(os.environ, {"JWT_SECRET": JWT_SECRET_VALUE}, clear=False), patch(
        "api.dependencies.JWT_SECRET",
        JWT_SECRET_VALUE,
    ):
        client = TestClient(create_app())
        r = client.post(
            "/api/v1/marketing/actions/execute",
            json={"action_id": "x", "approval_token": "y"},
        )
    assert r.status_code == 401


def test_breakers_api(temp_db):
    client = TestClient(create_app())
    token = pyjwt.encode(
        {"sub": "norbert", "role": "dowodca"},
        JWT_SECRET_VALUE,
        algorithm="HS256",
    )
    headers = {"Authorization": f"Bearer {token}"}
    with patch.dict(os.environ, {"JWT_SECRET": JWT_SECRET_VALUE, "MB_MODE": "shadow"}, clear=False), patch(
        "api.dependencies.JWT_SECRET",
        JWT_SECRET_VALUE,
    ):
        r = client.get("/api/v1/commander/marketing/breakers", headers=headers)
    assert r.status_code == 200
    assert r.json()["allowed"] is False
