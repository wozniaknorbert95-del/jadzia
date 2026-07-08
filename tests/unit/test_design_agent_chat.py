"""Unit tests for Design Agent GPT chat advisor (mocked LLM)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from agent.inspire import chat_advisor
from agent.inspire.chat_advisor import SESSIONS, set_llm_callable
from api.app import create_app


@pytest.fixture(autouse=True)
def clear_sessions():
    SESSIONS.clear()
    set_llm_callable(None)
    yield
    SESSIONS.clear()
    set_llm_callable(None)


@pytest.fixture
def client():
    return TestClient(create_app())


def _mock_llm(responses: list[dict]):
    calls = {"i": 0}

    def fn(_messages):
        idx = calls["i"]
        calls["i"] += 1
        return responses[min(idx, len(responses) - 1)]

    set_llm_callable(fn)


def test_chat_route_registered(client: TestClient) -> None:
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    paths = set(openapi.json().get("paths", {}).keys())
    assert "/api/v1/design-agent/chat" in paths
    assert "/api/v1/design-agent/chat/{session_id}" in paths


def test_phase_progression(client: TestClient) -> None:
    _mock_llm(
        [
            {
                "reply_nl": "Welkom! Wat voor bedrijf heb je?",
                "phase": 1,
                "brief_updates": {},
                "brief_confirmed": False,
            },
            {
                "reply_nl": "Top, vertel over je diensten.",
                "phase": 2,
                "brief_updates": {
                    "bedrijfsnaam": "Elektro De Vries",
                    "branche": "Elektricien",
                },
                "brief_confirmed": False,
            },
        ]
    )
    r1 = client.post(
        "/api/v1/design-agent/chat",
        json={"message": "Hoi"},
    )
    assert r1.status_code == 200
    body1 = r1.json()
    assert body1["phase"] == 1
    sid = body1["session_id"]

    r2 = client.post(
        "/api/v1/design-agent/chat",
        json={"session_id": sid, "message": "Ik ben Elektro De Vries, elektricien"},
    )
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["phase"] == 2
    assert body2["brief_partial"]["bedrijfsnaam"] == "Elektro De Vries"


def test_missing_diensten_blocks_ready(client: TestClient) -> None:
    _mock_llm(
        [
            {
                "reply_nl": "Bevestig je brief.",
                "phase": 7,
                "brief_updates": {
                    "bedrijfsnaam": "Test BV",
                    "branche": "Elektricien",
                    "doelgroep": "Particulieren",
                    "positionering": "strak",
                    "vehicle": "caddy",
                    "logo_file": "logo.png",
                    "brand_colors": ["#003366"],
                    "mockup_b_sku": "MA-005",
                    "mockup_a_sku": "CS-SET-PRO-ZZP",
                },
                "brief_confirmed": True,
            }
        ]
    )
    resp = client.post(
        "/api/v1/design-agent/chat",
        json={"message": "Ja klopt"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["brief_confirmed"] is True
    assert body["ready_to_generate"] is False


def test_confirm_full_brief_ready(client: TestClient) -> None:
    _mock_llm(
        [
            {
                "reply_nl": "Perfect, ik ga twee voorstellen maken.",
                "phase": 7,
                "brief_updates": {
                    "bedrijfsnaam": "Test BV",
                    "branche": "Elektricien",
                    "diensten": "Storingen en groepenkast",
                    "doelgroep": "Particulieren",
                    "positionering": "strak",
                    "vehicle": "caddy",
                    "logo_file": "logo.png",
                    "brand_colors": ["#003366"],
                    "mockup_b_sku": "MA-005",
                    "mockup_a_sku": "CS-SET-PRO-ZZP",
                },
                "brief_confirmed": True,
            }
        ]
    )
    resp = client.post(
        "/api/v1/design-agent/chat",
        json={"message": "Ja, klopt allemaal"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ready_to_generate"] is True
    assert body["brief_partial"]["diensten"]


def test_get_session(client: TestClient) -> None:
    _mock_llm(
        [
            {
                "reply_nl": "Hallo!",
                "phase": 1,
                "brief_updates": {"bedrijfsnaam": "X"},
                "brief_confirmed": False,
            }
        ]
    )
    post = client.post("/api/v1/design-agent/chat", json={"message": "Hoi"})
    sid = post.json()["session_id"]
    get = client.get(f"/api/v1/design-agent/chat/{sid}")
    assert get.status_code == 200
    assert get.json()["brief_partial"]["bedrijfsnaam"] == "X"


def test_get_session_404(client: TestClient) -> None:
    resp = client.get("/api/v1/design-agent/chat/nonexistent-id")
    assert resp.status_code == 404
