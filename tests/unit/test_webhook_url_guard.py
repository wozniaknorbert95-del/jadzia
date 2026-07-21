"""Negative tests for outbound worker callback URL controls."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from api.app import create_app
from api.webhooks import notify_webhook
from core.models import WorkerTaskRequest
from core.webhook_url_guard import CallbackUrlError, redact_callback_url, validate_callback_url


@pytest.fixture
def allowlisted_callback(monkeypatch: pytest.MonkeyPatch) -> str:
    monkeypatch.setenv("WEBHOOK_CALLBACK_ALLOWLIST", "callbacks.example.test")
    monkeypatch.setattr(
        "core.webhook_url_guard._resolve_addresses",
        lambda hostname: {"93.184.216.34"},
    )
    return "https://callbacks.example.test/hooks/worker?token=secret"


def test_validate_callback_url_allows_registered_public_https(allowlisted_callback: str) -> None:
    assert validate_callback_url(allowlisted_callback) == allowlisted_callback


@pytest.mark.parametrize(
    "url",
    (
        "http://callbacks.example.test/hook",
        "https://127.0.0.1/hook",
        "https://169.254.169.254/latest/meta-data",
        "https://[::1]/hook",
        "file:///tmp/callback",
        "gopher://callbacks.example.test/hook",
    ),
)
def test_validate_callback_url_rejects_unsafe_protocols_and_addresses(
    monkeypatch: pytest.MonkeyPatch, url: str
) -> None:
    monkeypatch.setenv(
        "WEBHOOK_CALLBACK_ALLOWLIST",
        "callbacks.example.test,127.0.0.1,169.254.169.254,::1",
    )
    with pytest.raises(CallbackUrlError):
        validate_callback_url(url)


def test_validate_callback_url_rejects_private_dns_resolution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WEBHOOK_CALLBACK_ALLOWLIST", "callbacks.example.test")
    monkeypatch.setattr(
        "core.webhook_url_guard._resolve_addresses",
        lambda hostname: {"10.0.0.8"},
    )

    with pytest.raises(CallbackUrlError, match="non-public"):
        validate_callback_url("https://callbacks.example.test/hook")


def test_worker_request_rejects_unregistered_callback(allowlisted_callback: str) -> None:
    with pytest.raises(ValidationError, match="not allowlisted"):
        WorkerTaskRequest(
            instruction="test",
            chat_id="test",
            webhook_url="https://unregistered.example.test/hook",
        )


def test_worker_api_rejects_unsafe_callback_before_queueing() -> None:
    with patch("api.routes.worker.add_task_to_queue") as add_task:
        response = TestClient(create_app()).post(
            "/worker/task",
            json={
                "instruction": "test",
                "chat_id": "callback-guard",
                "webhook_url": "http://127.0.0.1/internal",
            },
        )

    assert response.status_code == 422
    add_task.assert_not_called()


@pytest.mark.asyncio
async def test_notify_webhook_rejects_stored_private_callback_without_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    callback_url = "https://callbacks.example.test/hooks/worker?token=secret"
    monkeypatch.setenv("WEBHOOK_CALLBACK_ALLOWLIST", "callbacks.example.test")
    monkeypatch.setattr(
        "core.webhook_url_guard._resolve_addresses",
        lambda hostname: {"192.168.1.4"},
    )

    with (
        patch("api.webhooks.httpx.AsyncClient") as mock_client,
        patch("api.webhooks.log_error") as mock_log_error,
    ):
        await notify_webhook(callback_url, "task-1", "completed", {})

    mock_client.return_value.__aenter__.return_value.post.assert_not_called()
    assert "secret" not in str(mock_log_error.call_args)


@pytest.mark.asyncio
async def test_notify_webhook_does_not_follow_redirects(
    allowlisted_callback: str,
) -> None:
    redirect_response = Mock(is_redirect=True)

    with patch("api.webhooks.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=redirect_response
        )
        await notify_webhook(allowlisted_callback, "task-1", "completed", {})

    mock_client.assert_called_once_with(timeout=10.0, follow_redirects=False)
    mock_client.return_value.__aenter__.return_value.post.assert_awaited_once()


def test_redact_callback_url_excludes_path_query_and_credentials() -> None:
    assert (
        redact_callback_url("https://user:pass@callbacks.example.test/hooks?token=secret")
        == "https://callbacks.example.test"
    )
