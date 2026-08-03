"""Demand Desk API — money-check + hitl decision RBAC."""

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

JWT_SECRET_VALUE = "test-secret-desk-api"


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


def test_demand_os_status_shape(client):
    with jwt_env():
        r = client.get(
            "/api/v1/commander/demand-os/status",
            headers=_auth_headers("delegat"),
        )
    assert r.status_code == 200
    data = r.json()
    assert data["desk"] == "Demand Desk v2.1"
    assert "go_ready" not in data
    assert "diagnostics" in data
    assert "week_calendar" in data


def test_money_check_read(client):
    with jwt_env():
        r = client.get(
            "/api/v1/commander/demand-os/money-check",
            headers=_auth_headers("viewer"),
        )
    assert r.status_code == 200
    assert "money_check" in r.json()


def test_money_check_read_reflects_go_env(client, monkeypatch):
    monkeypatch.setenv("DEMAND_OS_MARKETING_HITL", "GO")
    with jwt_env():
        r = client.get(
            "/api/v1/commander/demand-os/money-check",
            headers=_auth_headers("viewer"),
        )
    assert r.status_code == 200
    assert r.json()["marketing"] == "HITL_LIVE"


def test_hitl_decision_viewer_forbidden(client):
    with jwt_env():
        r = client.post(
            "/api/v1/commander/demand-os/hitl/decision",
            headers=_auth_headers("viewer"),
            json={"asset_id": "x", "decision": "GOTOWY"},
        )
    assert r.status_code in (403, 401)


def test_hitl_decision_act(client, tmp_path: Path, monkeypatch):
    cal = tmp_path / "CONTENT-CALENDAR.json"
    cal.write_text(
        json.dumps(
            {
                "week": "2026-W31",
                "slots": [
                    {
                        "date": "2026-07-30",
                        "channel": "tiktok",
                        "asset_id": "tt_api",
                        "status": "planned",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "agent.demand_os.hitl_decision.DEFAULT_CALENDAR_PATH",
        cal,
    )
    with jwt_env():
        r = client.post(
            "/api/v1/commander/demand-os/hitl/decision",
            headers=_auth_headers("dowodca"),
            json={"asset_id": "tt_api", "decision": "GOTOWY"},
        )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["publish"] is False


def test_hunt_dry_viewer_forbidden(client):
    with jwt_env():
        r = client.post(
            "/api/v1/commander/demand-os/hunt/dry",
            headers=_auth_headers("viewer"),
            json={"target_id": "fb_own_page", "text": "dry only"},
        )
    assert r.status_code in (403, 401)


def test_hunt_dry_act(client, tmp_path: Path, monkeypatch):
    pack = tmp_path / "set-now"
    pack.mkdir()
    allow = {
        "targets": [
            {
                "id": "fb_g2",
                "platform": "facebook",
                "kind": "group_nl",
                "name": "Demo group",
                "status": "active",
                "icp_role": "installateur",
            }
        ],
        "max_groups": 1,
        "updated": "2026-08-02",
    }
    (pack / "ALLOWLIST.json").write_text(json.dumps(allow), encoding="utf-8")
    (pack / "ENGAGE-LOG.jsonl").write_text("", encoding="utf-8")
    monkeypatch.setenv("DEMAND_OS_SET_NOW", str(pack))

    with jwt_env():
        r = client.post(
            "/api/v1/commander/demand-os/hunt/dry",
            headers=_auth_headers("dowodca"),
            json={"target_id": "fb_g2", "text": "Tip zonder link — dry test"},
        )
    assert r.status_code == 200
    body = r.json()
    assert body.get("ok") is True
    assert body.get("publish") is False
    assert body.get("live") is False

