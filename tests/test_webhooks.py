"""Tests for webhook notifications."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from api.webhooks import notify_webhook


@pytest.mark.asyncio
async def test_notify_webhook_success():
    """Webhook notification should POST to URL."""
    webhook_url = "https://callbacks.example.test/callback"
    task_id = "test_task_1"

    with patch("api.webhooks.httpx.AsyncClient") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.is_redirect = False
        mock_response.raise_for_status = Mock()

        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        with patch("api.webhooks.validate_callback_url", return_value=webhook_url):
            await notify_webhook(
                webhook_url=webhook_url,
                task_id=task_id,
                status="completed",
                result={"files": ["test.css"]},
            )

        mock_client.return_value.__aenter__.return_value.post.assert_called_once()
        call_args = mock_client.return_value.__aenter__.return_value.post.call_args
        assert call_args[0][0] == webhook_url
        assert call_args[1]["json"]["task_id"] == task_id
        assert call_args[1]["json"]["status"] == "completed"


@pytest.mark.asyncio
async def test_notify_webhook_failure_does_not_raise():
    """Webhook failure should not raise exception."""
    webhook_url = "https://callbacks.example.test/callback"

    with patch("api.webhooks.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            side_effect=Exception("Connection failed")
        )

        with patch("api.webhooks.validate_callback_url", return_value=webhook_url):
            await notify_webhook(
                webhook_url=webhook_url,
                task_id="test",
                status="completed",
                result={},
            )


@pytest.mark.asyncio
async def test_webhook_called_on_task_completion():
    """execute_changes should call webhook when task completes (dry_run path)."""
    from agent.nodes.approval import execute_changes

    task_id = "webhook_task_1"
    webhook_url = "https://callbacks.example.test/webhook"
    state = {
        "tasks": {
            task_id: {
                "id": "op_1",
                "dry_run": True,
                "webhook_url": webhook_url,
                "diffs": {"test.css": {"old": "a", "new": "b"}},
            }
        },
        "active_task_id": task_id,
    }

    with patch("agent.nodes.approval.get_stored_diffs", return_value={"test.css": "diff"}):
        with patch("agent.nodes.approval.mark_task_completed", return_value=None):
            with patch(
                "api.webhooks.notify_webhook",
                new_callable=AsyncMock,
            ) as mock_webhook:
                await execute_changes("test", "http", state, task_id=task_id)

                mock_webhook.assert_called_once()
                # notify_webhook(webhook_url, task_id, status, result) - positional only
                args = mock_webhook.call_args[0]
                assert args[0] == webhook_url
                assert args[1] == task_id
                assert args[2] == "completed"
                assert args[3].get("dry_run") is True and "files_modified" in args[3]
