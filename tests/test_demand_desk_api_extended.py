"""Demand Desk API — ICP memory + ledger ensure (act scope)."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from api.app import create_app

JWT_SECRET_VALUE = "test-secret-desk-api-ext"


@contextmanager
def jwt_env():
    with patch.dict(os.environ, {"JWT_SECRET": JWT_SECRET_VALUE}, clear=False), patch(
        "api.dependencies.JWT_SECRET",
        JWT_SECRET_VALUE,
    ):
        yield


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


def test_memory_icp_viewer_forbidden(client):
    with jwt_env():
        r = client.post(
            "/api/v1/commander/demand-os/memory/icp",
            headers=_auth_headers("viewer"),
            json={"icp_role": "installateur", "hook": "bus 50m²"},
        )
    assert r.status_code in (403, 401)


def test_memory_icp_missing_fields(client):
    with jwt_env():
        r = client.post(
            "/api/v1/commander/demand-os/memory/icp",
            headers=_auth_headers("dowodca"),
            json={"icp_role": "installateur"},
        )
    assert r.status_code == 400


def test_memory_icp_act(client, tmp_path: Path, monkeypatch):
    mem = tmp_path / "MEMORY.json"
    monkeypatch.setenv("DEMAND_OS_MEMORY", str(mem))
    with jwt_env():
        r = client.post(
            "/api/v1/commander/demand-os/memory/icp",
            headers=_auth_headers("dowodca"),
            json={"icp_role": "loodgieter", "hook": "bus 50m²"},
        )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["memory"]["semantic"]["icp_role_week"] == "loodgieter"
    assert body["memory"]["semantic"]["hook_nl"] == "bus 50m²"
    assert body["scope"] == "demand_os:act"
    saved = json.loads(mem.read_text(encoding="utf-8"))
    assert saved["semantic"]["icp_role_week"] == "loodgieter"


def test_ledger_ensure_viewer_forbidden(client):
    with jwt_env():
        r = client.post(
            "/api/v1/commander/demand-os/ledger/ensure-today",
            headers=_auth_headers("viewer"),
            json={},
        )
    assert r.status_code in (403, 401)


def test_ledger_ensure_act(client, tmp_path: Path, monkeypatch):
    ledger = tmp_path / "LEDGER.csv"
    ledger.write_text(
        "date,channel,icp_role,asset_id,utm_link,publish_Y/N,comments_sent,"
        "hot_leads,wizard_starts,paid,notes\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("agent.demand_os.ledger.DEFAULT_LEDGER", ledger)
    with jwt_env():
        r = client.post(
            "/api/v1/commander/demand-os/ledger/ensure-today",
            headers=_auth_headers("dowodca"),
            json={},
        )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["action"] in ("appended", "exists")
    if body["action"] == "appended":
        text = ledger.read_text(encoding="utf-8")
        assert "tt_hygiene" in text or "hygiene" in text
