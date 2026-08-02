"""AT-CHAT-01..06 — orchestrator-backed chat intake."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from agent.inspire import chat_session_store
from agent.inspire.chat_advisor import SESSIONS
from api.app import create_app

_INSPIRE_ROOT = Path(__file__).resolve().parents[3] / "flexgrafik-inspire"
pytestmark = pytest.mark.skipif(
    not (_INSPIRE_ROOT / "engine").is_dir(),
    reason="flexgrafik-inspire engine not available",
)


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


def test_at_chat_02_opening_defers_standard_premium_to_recommendation(client: TestClient) -> None:
    body = client.get("/api/v1/design-agent/chat/opening").json()
    assert not re.search(r"Standard", body["reply_nl"], re.I)
    assert not re.search(r"Premium", body["reply_nl"], re.I)
    assert re.search(r"bedrijfsnaam", body["reply_nl"], re.I)


def test_at_chat_opening_always_fresh_session_id(client: TestClient) -> None:
    a = client.get("/api/v1/design-agent/chat/opening").json()
    b = client.get("/api/v1/design-agent/chat/opening").json()
    assert a["session_id"] != b["session_id"]
    assert not (a.get("brief_partial") or {}).get("bedrijfsnaam")


def test_at_chat_opening_no_cache_headers(client: TestClient) -> None:
    resp = client.get("/api/v1/design-agent/chat/opening")
    assert resp.status_code == 200
    cc = resp.headers.get("cache-control", "")
    assert "no-store" in cc or "no-cache" in cc


def test_at_chat_session_delete(client: TestClient) -> None:
    opening = client.get("/api/v1/design-agent/chat/opening").json()
    sid = opening["session_id"]
    del_resp = client.delete(f"/api/v1/design-agent/chat/{sid}")
    assert del_resp.status_code == 204
    assert client.get(f"/api/v1/design-agent/chat/{sid}").status_code == 404


def test_at_chat_04_no_budget_not_ready(client: TestClient) -> None:
    opening = client.get("/api/v1/design-agent/chat/opening").json()
    sid = opening["session_id"]
    turns = [
        {"message": "Schilder Janssen"},
        {"quick_reply_id": "bus_l", "quick_reply_field": "vehicle.type"},
        {"quick_reply_id": "bouw", "quick_reply_field": "company.branche"},
        {"message": "Noord-Brabant"},
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
        {"quick_reply_id": "bus_l", "quick_reply_field": "vehicle.type"},
        {"quick_reply_id": "bouw", "quick_reply_field": "company.branche"},
        {"message": "Noord-Brabant"},
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


def test_quick_previews_after_bedrijfsnaam_and_vehicle(client: TestClient) -> None:
    """T-002 E2E — orchestrator returns 3 quick preview data URLs after 2Q path."""
    opening = client.get("/api/v1/design-agent/chat/opening").json()
    sid = opening["session_id"]
    client.post(
        "/api/v1/design-agent/chat",
        json={"session_id": sid, "message": "Janssen Elektro"},
    )
    resp = client.post(
        "/api/v1/design-agent/chat",
        json={
            "session_id": sid,
            "message": "",
            "quick_reply_id": "caddy",
            "quick_reply_field": "vehicle.type",
        },
    )
    assert resp.status_code == 200
    previews = resp.json().get("quick_previews") or []
    assert len(previews) == 3
    assert all(str(u).startswith("data:image/") for u in previews)


def test_logo_turn_does_not_pollute_bedrijfsnaam_or_vehicle(client: TestClient) -> None:
    """Wave1 — multipart logo + UI boilerplate must not fill brief text fields."""
    opening = client.get("/api/v1/design-agent/chat/opening").json()
    sid = opening["session_id"]
    client.post(
        "/api/v1/design-agent/chat",
        json={"session_id": sid, "message": "Schilder Janssen"},
    )
    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
    resp = client.post(
        "/api/v1/design-agent/chat/turn",
        data={
            "session_id": sid,
            "message": "Ik heb mijn logo geüpload.",
            "brand_colors": '["#003366","#FFFFFF"]',
        },
        files={"logo": ("logo-janssen.png", png, "image/png")},
    )
    assert resp.status_code == 200
    body = resp.json()
    brief = body["brief_partial"]
    assert brief.get("bedrijfsnaam") == "Schilder Janssen"
    vehicle = str(brief.get("vehicle") or "")
    assert "logo geupload" not in vehicle.lower()
    assert "logo geüpload" not in vehicle.lower()
    assert "ik heb mijn logo" not in vehicle.lower()
    assert brief.get("logo_file") == "logo-janssen.png" or brief.get("logo_status") == "uploaded_png"
    assert "Logo ontvangen" in body["reply_nl"] or "logo" in body["reply_nl"].lower()
