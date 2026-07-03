"""Auth hardening tests — S2-01 production gates and JWT-protected admin routes."""

import os
from unittest.mock import patch

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from core.config import validate_production_config

JWT_SECRET_VALUE = "test-secret-auth-hardening"


def _auth_headers() -> dict[str, str]:
    token = pyjwt.encode({"sub": "test"}, JWT_SECRET_VALUE, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    return TestClient(create_app())


class TestProductionConfigGate:
    def test_validate_passes_when_not_production(self, monkeypatch):
        monkeypatch.delenv("REQUIRE_SECRETS", raising=False)
        monkeypatch.delenv("JADZIA_ENV", raising=False)
        validate_production_config()

    def test_validate_raises_when_require_secrets_and_missing(self, monkeypatch):
        monkeypatch.setenv("REQUIRE_SECRETS", "1")
        monkeypatch.delenv("JWT_SECRET", raising=False)
        monkeypatch.delenv("WC_WEBHOOK_SECRET", raising=False)
        monkeypatch.delenv("LEADS_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="Missing required secrets"):
            validate_production_config()

    def test_create_app_fails_without_secrets_in_production(self, monkeypatch):
        monkeypatch.setenv("JADZIA_ENV", "production")
        monkeypatch.delenv("JWT_SECRET", raising=False)
        monkeypatch.delenv("WC_WEBHOOK_SECRET", raising=False)
        monkeypatch.delenv("LEADS_API_KEY", raising=False)
        with pytest.raises(RuntimeError):
            create_app()


class TestAdminRoutesRequireJwt:
    @pytest.mark.parametrize(
        "method,path,kwargs",
        [
            ("post", "/chat", {"json": {"message": "hi", "chat_id": "t1"}}),
            ("post", "/rollback", {}),
            ("get", "/test-ssh", {}),
            ("post", "/clear", {}),
            ("get", "/logs", {}),
            ("get", "/sessions", {}),
            ("post", "/sessions/cleanup", {"params": {"days": 7}}),
            ("get", "/costs", {}),
            ("post", "/costs/reset", {}),
        ],
    )
    def test_admin_routes_return_401_without_jwt(self, client, method, path, kwargs):
        with patch.dict(os.environ, {"JWT_SECRET": JWT_SECRET_VALUE}, clear=False), patch(
            "api.dependencies.JWT_SECRET",
            JWT_SECRET_VALUE,
        ):
            response = getattr(client, method)(path, **kwargs)
        assert response.status_code == 401

    def test_chat_returns_200_with_jwt(self, client):
        with patch.dict(os.environ, {"JWT_SECRET": JWT_SECRET_VALUE}, clear=False), patch(
            "api.dependencies.JWT_SECRET",
            JWT_SECRET_VALUE,
        ), patch(
            "core.agent.process_message",
            return_value=("ok", False, None),
        ):
            response = client.post(
                "/chat",
                json={"message": "hi", "chat_id": "auth_test"},
                headers=_auth_headers(),
            )
        assert response.status_code == 200
        assert response.json()["response"] == "ok"
