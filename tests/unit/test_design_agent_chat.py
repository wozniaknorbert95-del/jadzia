"""Unit tests for Design Agent GPT chat advisor (mocked LLM)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from agent.inspire import chat_advisor
from agent.inspire.chat_advisor import SESSIONS, set_llm_callable
from api.app import create_app


@pytest.fixture(autouse=True)
def _tier_matrix_env(monkeypatch: pytest.MonkeyPatch) -> None:
    matrix = Path(__file__).resolve().parents[3] / "flexgrafik-inspire" / "brain" / "tier-matrix.json"
    if matrix.is_file():
        monkeypatch.setenv("DA_TIER_MATRIX_PATH", str(matrix))


@pytest.fixture(autouse=True)
def _isolated_rate_store(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from agent import rate_store

    monkeypatch.setenv("DA_RATE_STORE_PATH", str(tmp_path / "rate.json"))
    rate_store.clear_store()


@pytest.fixture(autouse=True)
def clear_sessions(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    from agent.inspire import chat_session_store

    monkeypatch.setenv("DA_CHAT_SESSION_DB", str(tmp_path / "chat-sessions.sqlite3"))
    monkeypatch.setenv("DA_CHAT_ENGINE", "legacy")
    chat_session_store.clear_all()
    SESSIONS.clear()
    set_llm_callable(None)
    yield
    SESSIONS.clear()
    set_llm_callable(None)
    chat_session_store.clear_all()


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
    assert "/api/v1/design-agent/chat/opening" in paths
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
                "reply_nl": "Bevestig je brief via de knop.",
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
    assert body["brief_confirmed"] is False
    assert body["ready_to_generate"] is False


def test_confirm_full_brief_ready(client: TestClient) -> None:
    _mock_llm(
        [
            {
                "reply_nl": "Klik op Bevestigen om mock-ups te maken.",
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
                    "telefoon": "06-12345678",
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
    assert body["brief_confirmed"] is False
    assert body["ready_to_generate"] is True
    assert body["brief_partial"]["diensten"]
    assert body["missing_fields"] == []


def test_missing_fields_in_response(client: TestClient) -> None:
    _mock_llm(
        [
            {
                "reply_nl": "Samenvatting",
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
                "brief_confirmed": False,
            }
        ]
    )
    resp = client.post("/api/v1/design-agent/chat", json={"message": "ok"})
    body = resp.json()
    assert body["ready_to_generate"] is False
    assert "diensten" in body["missing_fields"]


def test_logo_reupload_required_on_get_session(client: TestClient) -> None:
    _mock_llm(
        [
            {
                "reply_nl": "Upload logo",
                "phase": 5,
                "brief_updates": {"logo_file": "logo.png"},
                "brief_confirmed": False,
            }
        ]
    )
    post = client.post("/api/v1/design-agent/chat", json={"message": "logo"})
    sid = post.json()["session_id"]
    get = client.get(f"/api/v1/design-agent/chat/{sid}")
    body = get.json()
    assert body["logo_reupload_required"] is True
    assert body["brief_partial"]["logo_file"] == "logo.png"


def test_parse_summary_fields_backfills_diensten() -> None:
    from agent.inspire.chat_advisor import parse_summary_fields

    brief = {"bedrijfsnaam": "X"}
    reply = "**Diensten:** Storingen en onderhoud\n**Voertuig:** Caddy (caddy)"
    updates = parse_summary_fields(brief, reply)
    assert updates["diensten"] == "Storingen en onderhoud"
    assert updates["vehicle"] == "caddy"


def test_llm_brief_confirmed_flag_ignored(client: TestClient) -> None:
    """LLM must not set server brief_confirmed — UI button only."""
    _mock_llm(
        [
            {
                "reply_nl": "Bedankt!",
                "phase": 7,
                "brief_updates": {"bedrijfsnaam": "X"},
                "brief_confirmed": True,
            }
        ]
    )
    resp = client.post("/api/v1/design-agent/chat", json={"message": "bevestig"})
    assert resp.status_code == 200
    assert resp.json()["brief_confirmed"] is False


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


def test_parse_summary_fields_telefoon_website_slogan() -> None:
    from agent.inspire.chat_advisor import parse_summary_fields

    brief: dict = {}
    reply = (
        "**Telefoon:** 06-12345678\n"
        "**Website:** https://example.nl\n"
        "**Slogan:** Altijd paraat\n"
    )
    updates = parse_summary_fields(brief, reply)
    assert updates["telefoon"] == "06-12345678"
    assert updates["website"] == "https://example.nl"
    assert updates["slogan"] == "Altijd paraat"


def test_chat_turn_multipart_logo(client: TestClient) -> None:
    _mock_llm(
        [
            {
                "reply_nl": "Logo ontvangen!",
                "phase": 5,
                "brief_updates": {},
                "brief_confirmed": False,
            }
        ]
    )
    resp = client.post(
        "/api/v1/design-agent/chat/turn",
        data={"message": "Logo geüpload", "session_id": ""},
        files={"logo": ("logo.png", b"\x89PNG\r\n\x1a\n" + b"x" * 64, "image/png")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["brief_partial"]["logo_file"] == "logo.png"


def test_chat_turn_empty_message_no_logo_400(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/design-agent/chat/turn",
        data={"message": "", "session_id": ""},
    )
    assert resp.status_code == 400


def test_chat_rate_limit_429(client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from agent import rate_store
    from api.routes import design_agent_chat as chat_routes

    store = tmp_path / "chat-rate.json"
    monkeypatch.setenv("DA_RATE_STORE_PATH", str(store))
    rate_store.clear_store()
    monkeypatch.setattr(chat_routes, "_chat_rate_limit", lambda: 1)
    _mock_llm(
        [
            {"reply_nl": "ok", "phase": 1, "brief_updates": {}, "brief_confirmed": False},
            {"reply_nl": "ok2", "phase": 1, "brief_updates": {}, "brief_confirmed": False},
        ]
    )
    r1 = client.post("/api/v1/design-agent/chat", json={"message": "a"})
    assert r1.status_code == 200
    sid = r1.json()["session_id"]
    r2 = client.post("/api/v1/design-agent/chat", json={"message": "b", "session_id": sid})
    r3 = client.post("/api/v1/design-agent/chat", json={"message": "c", "session_id": sid})
    assert r2.status_code == 200
    assert r3.status_code == 429


def test_session_persists_across_memory_clear(client: TestClient) -> None:
    _mock_llm([{"reply_nl": "ok", "phase": 1, "brief_updates": {}, "brief_confirmed": False}])
    resp = client.post("/api/v1/design-agent/chat", json={"message": "hi"})
    sid = resp.json()["session_id"]
    SESSIONS.clear()
    restored = chat_advisor.get_session(sid)
    assert restored is not None
    assert restored.session_id == sid


def test_chat_session_messages_tail(client: TestClient) -> None:
    _mock_llm(
        [
            {"reply_nl": "fase1", "phase": 1, "brief_updates": {}, "brief_confirmed": False},
            {"reply_nl": "fase2", "phase": 2, "brief_updates": {}, "brief_confirmed": False},
        ]
    )
    r1 = client.post("/api/v1/design-agent/chat", json={"message": "a"})
    sid = r1.json()["session_id"]
    client.post("/api/v1/design-agent/chat", json={"message": "b", "session_id": sid})
    get = client.get(f"/api/v1/design-agent/chat/{sid}")
    assert get.status_code == 200
    tail = get.json()["messages_tail"]
    assert len(tail) >= 2
    assert tail[-1]["role"] == "assistant"


def test_tier_resolve_failed_blocks_ready(client: TestClient) -> None:
    _mock_llm(
        [
            {
                "reply_nl": "samenvatting",
                "phase": 7,
                "brief_updates": {
                    "vehicle": "spaceship",
                    "bedrijfsnaam": "X",
                    "branche": "Y",
                    "diensten": "Z",
                    "doelgroep": "A",
                    "positionering": "strak",
                    "logo_file": "l.png",
                    "brand_colors": ["#000"],
                    "telefoon": "06-123",
                },
                "brief_confirmed": False,
            }
        ]
    )
    resp = client.post("/api/v1/design-agent/chat", json={"message": "klaar"})
    data = resp.json()
    assert data["ready_to_generate"] is False
    assert "Voertuigtype niet herkend" in data["reply_nl"]


def test_parse_summary_sets_primary_cta_website() -> None:
    from agent.inspire.chat_advisor import parse_summary_fields

    brief = {"website": "https://x.nl"}
    updates = parse_summary_fields(brief, "Samenvatting")
    assert updates.get("primary_cta") == "website"


def test_parse_user_message_fields_e2e_schilder() -> None:
    from agent.inspire.chat_advisor import parse_user_message_fields

    brief: dict = {}
    msg = (
        "Bedrijfsnaam: Schilder Janssen. Branche: schilder. "
        "Diensten: binnen- en buitenschilderwerk en behangen. "
        "Doelgroep: woningeigenaren en VvE's in Noord-Brabant."
    )
    updates = parse_user_message_fields(brief, msg)
    assert updates["bedrijfsnaam"] == "Schilder Janssen"
    assert updates["branche"] == "schilder"
    assert "buitenschilderwerk" in updates["diensten"]

    brief2 = {}
    veh = parse_user_message_fields(brief2, "Bestelbus L (bus_l), zakelijk gebruik.")
    assert veh["vehicle"] == "bus_l"

    brief3 = {}
    contact = parse_user_message_fields(
        brief3, "Telefoon: 06-98765432. Website: www.janssen-schilder.nl."
    )
    assert contact["telefoon"] == "06-98765432"
    assert contact["website"] == "www.janssen-schilder.nl"
    assert contact["primary_cta"] == "website"


def test_chat_turn_brand_colors_persist(client: TestClient) -> None:
    _mock_llm(
        [
            {
                "reply_nl": "Logo ontvangen!",
                "phase": 5,
                "brief_updates": {},
                "brief_confirmed": False,
            }
        ]
    )
    resp = client.post(
        "/api/v1/design-agent/chat/turn",
        data={
            "message": "Logo geüpload",
            "session_id": "",
            "brand_colors": '["#111111","#222222"]',
        },
        files={"logo": ("logo.png", b"\x89PNG\r\n\x1a\n" + b"x" * 64, "image/png")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["brief_partial"]["brand_colors"] == ["#111111", "#222222"]
    assert body["brief_partial"]["logo_file"] == "logo.png"


def test_ready_without_brand_colors_when_logo_present(client: TestClient) -> None:
    """logo_file satisfies readiness; colors ship at generate (F-077)."""
    _mock_llm(
        [
            {
                "reply_nl": "Samenvatting klaar.",
                "phase": 7,
                "brief_updates": {
                    "bedrijfsnaam": "Test BV",
                    "branche": "schilder",
                    "diensten": "Schilderwerk",
                    "doelgroep": "Particulieren",
                    "positionering": "balanced",
                    "vehicle": "bus_l",
                    "logo_file": "logo.png",
                    "mockup_b_sku": "BLS-SET-LOGO-CONTACT",
                    "mockup_a_sku": "NA-WRAP-PRO",
                    "telefoon": "06-12345678",
                },
                "brief_confirmed": False,
            }
        ]
    )
    resp = client.post("/api/v1/design-agent/chat", json={"message": "klaar"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ready_to_generate"] is True
    assert "brand_colors" not in data["missing_fields"]

