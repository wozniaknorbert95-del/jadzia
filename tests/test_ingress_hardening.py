"""Negative contracts for AUD-REM-INGRESS-01 public boundaries."""

from __future__ import annotations

import os
import tempfile
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient


@pytest.fixture
def temp_db(monkeypatch: pytest.MonkeyPatch):
    import agent.db as db_mod

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr(db_mod, "DB_PATH", path)
    if getattr(db_mod._local, "conn", None):
        db_mod._local.conn.close()
    db_mod._local.conn = None
    yield
    if getattr(db_mod._local, "conn", None):
        db_mod._local.conn.close()
    db_mod._local.conn = None
    try:
        os.unlink(path)
    except PermissionError:
        pass


def _widget_result() -> dict:
    return {"reply": "ok", "lead": {}}


def test_widget_mints_unknown_session_and_reuses_issued_one(temp_db):
    from api.app import create_app

    client = TestClient(create_app())
    with patch(
        "agent.customer_agent.process_customer_message",
        new_callable=AsyncMock,
        return_value=_widget_result(),
    ) as process:
        first = client.post(
            "/api/v1/widget/chat",
            json={"session_id": "attacker-controlled", "message": "hello"},
        )
        assert first.status_code == 200
        issued = first.json()["session_id"]
        assert uuid.UUID(issued).version == 4
        assert issued != "attacker-controlled"

        second = client.post(
            "/api/v1/widget/chat",
            json={"session_id": issued, "message": "again"},
        )

    assert second.status_code == 200
    assert second.json()["session_id"] == issued
    assert process.await_args_list[0].kwargs["session_id"] == issued
    assert process.await_args_list[1].kwargs["session_id"] == issued


def test_widget_rejects_oversized_body_before_llm(temp_db):
    from api.app import create_app

    client = TestClient(create_app())
    with patch("agent.customer_agent.process_customer_message", new_callable=AsyncMock) as process:
        response = client.post(
            "/api/v1/widget/chat",
            content=b'{"message":"' + b"x" * 9_000 + b'"}',
            headers={"Content-Type": "application/json"},
        )

    assert response.status_code == 413
    process.assert_not_awaited()


def test_widget_rate_limit_returns_429(temp_db, monkeypatch: pytest.MonkeyPatch):
    from api.app import create_app

    monkeypatch.setenv("WIDGET_CHAT_RATE_LIMIT", "1")
    client = TestClient(create_app())
    with patch(
        "agent.customer_agent.process_customer_message",
        new_callable=AsyncMock,
        return_value=_widget_result(),
    ):
        session_id = str(uuid.uuid4())
        first = client.post(
            "/api/v1/widget/chat",
            json={"session_id": session_id, "message": "one"},
        )
        second = client.post(
            "/api/v1/widget/chat",
            json={"session_id": first.json()["session_id"], "message": "two"},
        )

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.headers["retry-after"] == "3600"


def test_native_telegram_secret_and_replay_claim_are_durable(
    temp_db,
    monkeypatch: pytest.MonkeyPatch,
):
    from agent.db import db_claim_ingress_replay
    from agent.telegram_validator import validate_native_telegram_secret

    monkeypatch.setattr("agent.telegram_validator.TELEGRAM_WEBHOOK_SECRET", "native-secret")
    with pytest.raises(HTTPException, match="Missing X-Telegram"):
        validate_native_telegram_secret(None)
    with pytest.raises(HTTPException, match="Invalid Telegram"):
        validate_native_telegram_secret("wrong")
    assert validate_native_telegram_secret("native-secret") is True

    assert db_claim_ingress_replay("telegram_update", "42", ttl_sec=300) is True
    import agent.db as db_mod

    db_mod._local.conn.close()
    db_mod._local.conn = None
    assert db_claim_ingress_replay("telegram_update", "42", ttl_sec=300) is False


def test_telegram_rejects_oversized_native_update_before_processing(temp_db):
    from fastapi import FastAPI

    from api.telegram import router as telegram_router

    app = FastAPI()
    app.include_router(telegram_router)
    client = TestClient(app)
    response = client.post(
        "/telegram/webhook",
        content=b'{"update_id":1,"message":"' + b"x" * 66_000 + b'"}',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 413


def test_brain_bus_requires_correlation_and_accepts_event_once(
    temp_db,
    monkeypatch: pytest.MonkeyPatch,
):
    from api.app import create_app

    monkeypatch.setenv("BRAIN_BUS_SECRET", "brain-secret")
    client = TestClient(create_app())
    base = {
        "event_type": "system.health.recovered",
        "source_brain": "vcms",
        "payload": {"conflicts": 0},
    }
    missing = client.post(
        "/api/v1/brain-bus/events",
        headers={"X-Brain-Bus-Secret": "brain-secret"},
        json=base,
    )
    oversized = client.post(
        "/api/v1/brain-bus/events",
        headers={"X-Brain-Bus-Secret": "brain-secret"},
        json={**base, "correlation_id": "large-payload", "payload": {"text": "x" * 8_193}},
    )
    event = {**base, "correlation_id": "ingress-replay-test"}
    first = client.post(
        "/api/v1/brain-bus/events?process=false",
        headers={"X-Brain-Bus-Secret": "brain-secret"},
        json=event,
    )
    second = client.post(
        "/api/v1/brain-bus/events?process=false",
        headers={"X-Brain-Bus-Secret": "brain-secret"},
        json=event,
    )

    assert missing.status_code == 422
    assert oversized.status_code == 422
    assert first.status_code == 200
    assert second.json() == {
        "ok": True,
        "duplicate": True,
        "correlation_id": "ingress-replay-test",
    }


def test_production_hides_api_metadata_by_default(monkeypatch: pytest.MonkeyPatch):
    from api.app import create_app

    monkeypatch.setenv("JADZIA_ENV", "production")
    monkeypatch.setenv("JWT_SECRET", "x" * 32)
    monkeypatch.setenv("WC_WEBHOOK_SECRET", "wc-secret")
    monkeypatch.setenv("LEADS_API_KEY", "leads-secret")
    app = create_app()

    assert app.docs_url is None
    assert app.redoc_url is None
    assert app.openapi_url is None
    client = TestClient(app)
    assert client.get("/docs").status_code == 404
    assert client.get("/redoc").status_code == 404
    assert client.get("/openapi.json").status_code == 404
