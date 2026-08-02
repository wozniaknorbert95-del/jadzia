"""HITL decision persists to calendar and status reflects slot."""

from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from api.app import create_app

JWT_SECRET_VALUE = "test-secret-hitl-persist"


@contextmanager
def jwt_env():
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("JWT_SECRET", JWT_SECRET_VALUE)
        mp.setattr("api.dependencies.JWT_SECRET", JWT_SECRET_VALUE)
        yield


@pytest.fixture
def client():
    return TestClient(create_app())


def _auth(role: str = "dowodca") -> dict[str, str]:
    token = pyjwt.encode({"sub": "t", "role": role}, JWT_SECRET_VALUE, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


def test_hitl_gotowy_persists_calendar(client, tmp_path: Path, monkeypatch):
    cal_path = tmp_path / "CONTENT-CALENDAR.json"
    cal_path.write_text(
        json.dumps(
            {
                "week": "2026-W32",
                "updated": "2026-08-02",
                "slots": [
                    {
                        "date": "2026-08-02",
                        "channel": "tiktok",
                        "asset_id": "tt_persist_01",
                        "status": "planned",
                        "pass_token": None,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    pack = tmp_path
    (pack / "ALLOWLIST.json").write_text(
        '{"targets":[],"max_groups":1,"updated":"2026-08-02"}',
        encoding="utf-8",
    )
    (pack / "LEDGER.csv").write_text(
        "date,channel,icp_role,asset_id,utm_link,publish_Y/N,comments_sent,hot_leads,wizard_starts,paid,notes\n",
        encoding="utf-8",
    )
    (pack / "GROWTH-EVENTS.jsonl").write_text("", encoding="utf-8")

    monkeypatch.setenv("DEMAND_OS_SET_NOW", str(pack))
    monkeypatch.setattr("agent.demand_os.hitl_decision.DEFAULT_CALENDAR_PATH", cal_path)
    monkeypatch.setattr("agent.demand_os.content_calendar.DEFAULT_CALENDAR_PATH", cal_path)

    with jwt_env():
        r = client.post(
            "/api/v1/commander/demand-os/hitl/decision",
            headers=_auth("dowodca"),
            json={"asset_id": "tt_persist_01", "decision": "GOTOWY"},
        )
    assert r.status_code == 200
    saved = json.loads(cal_path.read_text(encoding="utf-8"))
    slot = saved["slots"][0]
    assert slot["status"] == "validated"
