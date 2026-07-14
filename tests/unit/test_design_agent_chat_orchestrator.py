"""AT-CHAT-01..06 — orchestrator-backed chat intake."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from agent.inspire import chat_session_store
from agent.inspire.chat_advisor import SESSIONS
from api.app import create_app


@pytest.fixture(autouse=True)
def _orch_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    inspire = Path(__file__).resolve().parents[3] / "flexgrafik-inspire"
    monkeypatch.setenv("INSPIRE_REPO_PATH", str(inspire))
    monkeypatch.setenv("DA_CHAT_ENGINE", "orchestrator")
    monkeypatch.setenv("DA_CHAT_SESSION_DB", str(tmp_path / "chat-orch.sqlite3"))
    matrix = inspire / "brain" / "tier-matrix.json"
    if matrix.is_file():
        monkeypatch.setenv("DA_TIER_MATRIX_PATH", str(matrix))
    from agent import rate_store

    monkeypatch.setenv("DA_RATE_STORE_PATH", str(tmp_path / "rate.json"))
    rate_store.clear_store()
    chat_session_store.clear_all()
    SESSIONS.clear()
    yield
    SESSIONS.clear()
    chat_session_store.clear_all()


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_at_chat_01_opening_no_helpen(client: TestClient) -> None:
    resp = client.get("/api/v1/design-agent/chat/opening")
    assert resp.status_code == 200
    body = resp.json()
    assert not re.search(r"helpen", body["reply_nl"], re.I)
    assert body["opening_source"] == "brain"


def test_at_chat_02_opening_standard_premium(client: TestClient) -> None:
    body = client.get("/api/v1/design-agent/chat/opening").json()
    assert re.search(r"Standard", body["reply_nl"], re.I)
    assert re.search(r"Premium", body["reply_nl"], re.I)


def test_at_chat_04_no_budget_not_ready(client: TestClient) -> None:
    opening = client.get("/api/v1/design-agent/chat/opening").json()
    sid = opening["session_id"]
    turns = [
        {"message": "Schilder Janssen"},
        {"quick_reply_id": "bouw", "quick_reply_field": "company.branche"},
        {"message": "Noord-Brabant"},
        {"quick_reply_id": "bus_l", "quick_reply_field": "vehicle.type"},
        {"quick_reply_id": "zakelijk", "quick_reply_field": "vehicle.usage"},
        {"message": "woningeigenaren en VvE's"},
        {"message": "binnen- en buitenschilderwerk"},
        {"quick_reply_id": "strak", "quick_reply_field": "marketing.desired_impression"},
        {"quick_reply_id": "telefoon", "quick_reply_field": "marketing.primary_cta"},
        {"message": "06-98765432"},
    ]
    last = opening
    for t in turns:
        last = client.post("/api/v1/design-agent/chat", json={"session_id": sid, **t}).json()
    assert last["ready_to_generate"] is False
    assert "budget_range" in last.get("missing_fields", [])


def test_at_chat_05_chip_bouw_sets_branche(client: TestClient) -> None:
    opening = client.get("/api/v1/design-agent/chat/opening").json()
    sid = opening["session_id"]
    client.post(
        "/api/v1/design-agent/chat",
        json={"session_id": sid, "message": "Test BV"},
    )
    resp = client.post(
        "/api/v1/design-agent/chat",
        json={
            "session_id": sid,
            "message": "",
            "quick_reply_id": "bouw",
            "quick_reply_field": "company.branche",
        },
    )
    assert resp.status_code == 200
  # branche may be normalized id in flat brief
    branche = resp.json()["brief_partial"].get("branche", "")
    assert branche in ("bouw", "Bouw/schilder", "bouw/schilder")


def test_at_chat_03_budget_before_summary(client: TestClient) -> None:
    opening = client.get("/api/v1/design-agent/chat/opening").json()
    sid = opening["session_id"]
    flow = [
        {"message": "Schilder Janssen"},
        {"quick_reply_id": "bouw", "quick_reply_field": "company.branche"},
        {"message": "Noord-Brabant"},
        {"quick_reply_id": "bus_l", "quick_reply_field": "vehicle.type"},
        {"quick_reply_id": "zakelijk", "quick_reply_field": "vehicle.usage"},
        {"message": "woningeigenaren"},
        {"message": "schilderwerk"},
        {"quick_reply_id": "strak", "quick_reply_field": "marketing.desired_impression"},
        {"quick_reply_id": "telefoon", "quick_reply_field": "marketing.primary_cta"},
        {"message": "06-98765432"},
        {"quick_reply_id": "uploaded_png", "quick_reply_field": "brand_assets.logo_status"},
        {"message": "#003366, #FFFFFF"},
        {"quick_reply_id": "300_600", "quick_reply_field": "budget.range"},
        {"quick_reply_id": "flexibel_als_het_klopt", "quick_reply_field": "budget.flexibility"},
    ]
    last = opening
    for step in flow:
        last = client.post("/api/v1/design-agent/chat", json={"session_id": sid, **step}).json()
    assert last["stap"] >= 7
    assert last["brief_partial"].get("budget_range") == "300_600"
    assert last["brief_partial"].get("_budget_explicit") is True
