"""Hunt dry POST → status queue shows SENT."""

from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from api.app import create_app

JWT_SECRET_VALUE = "test-secret-hunt-queue"


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


def test_hunt_dry_then_status_sent(client, tmp_path: Path, monkeypatch):
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
    (pack / "LEDGER.csv").write_text(
        "date,channel,icp_role,asset_id,utm_link,publish_Y/N,comments_sent,hot_leads,wizard_starts,paid,notes\n",
        encoding="utf-8",
    )
    (pack / "CONTENT-CALENDAR.json").write_text(
        '{"week":"2026-W32","updated":"2026-08-02","slots":[]}',
        encoding="utf-8",
    )
    (pack / "GROWTH-EVENTS.jsonl").write_text("", encoding="utf-8")
    (pack / "ENGAGE-LOG.jsonl").write_text("", encoding="utf-8")

    monkeypatch.setenv("DEMAND_OS_SET_NOW", str(pack))

    with jwt_env():
        dry = client.post(
            "/api/v1/commander/demand-os/hunt/dry",
            headers=_auth("dowodca"),
            json={"target_id": "fb_g2", "text": "ICP tip + Wizard UTM dry only"},
        )
        assert dry.status_code == 200
        assert dry.json().get("ok") is True

        st = client.get(
            "/api/v1/commander/demand-os/status",
            headers=_auth("dowodca"),
        )
    assert st.status_code == 200
    hunt = st.json().get("screen", {}).get("hunt_queue") or []
    sent = [h for h in hunt if h.get("target_id") == "fb_g2" and h.get("desk_status") == "SENT"]
    assert sent, f"expected SENT for fb_g2, got {hunt}"
