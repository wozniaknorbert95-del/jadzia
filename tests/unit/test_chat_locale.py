"""Chat locale — opening PL/EN via orchestrator bridge."""

from __future__ import annotations

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
    monkeypatch.setenv("INSPIRE_REPO_PATH", str(_INSPIRE_ROOT))
    monkeypatch.setenv("DA_CHAT_ENGINE", "orchestrator")
    monkeypatch.setenv("DA_CHAT_SESSION_DB", str(tmp_path / "chat-locale.sqlite3"))
    monkeypatch.setenv("DA_RATE_STORE_PATH", str(tmp_path / "rate.json"))
    from agent import rate_store

    rate_store.clear_store()
    chat_session_store.clear_all()
    SESSIONS.clear()
    yield
    SESSIONS.clear()
    chat_session_store.clear_all()


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_opening_pl(client: TestClient) -> None:
    r = client.get("/api/v1/design-agent/chat/opening", params={"locale": "pl-PL"})
    assert r.status_code == 200
    body = r.json()
    assert "nazwa firmy" in body["reply"].lower()
    assert body["reply"] == body["reply_nl"]
    assert body["locale"] == "pl-PL"


def test_opening_en(client: TestClient) -> None:
    r = client.get("/api/v1/design-agent/chat/opening", params={"locale": "en-GB"})
    assert r.status_code == 200
    body = r.json()
    assert "company name" in body["reply"].lower()
    assert body["locale"] == "en-GB"


def test_opening_default_nl(client: TestClient) -> None:
    r = client.get("/api/v1/design-agent/chat/opening")
    assert r.status_code == 200
    body = r.json()
    assert "bedrijfsnaam" in body["reply_nl"].lower()
    assert body.get("locale", "nl-NL") == "nl-NL"
