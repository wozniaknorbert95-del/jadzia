"""
Tests for self-healing deployment: health_check_wordpress and auto-rollback on failure.

Run: pytest tests/test_self_healing.py -v
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from agent.tools.rest import health_check_wordpress


@pytest.mark.asyncio
async def test_health_check_healthy():
    """Test health check with working site (status 200)."""
    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await health_check_wordpress("https://example.com", timeout=10)

    assert result["healthy"] is True
    assert result["status_code"] == 200
    assert "response_time" in result
    assert result["response_time"] >= 0
    assert result["error"] is None


@pytest.mark.asyncio
async def test_health_check_server_error():
    """Test health check with 500 error."""
    mock_response = MagicMock()
    mock_response.status_code = 500

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await health_check_wordpress("https://example.com", timeout=10)

    assert result["healthy"] is False
    assert result["status_code"] == 500
    assert "error" in result
    assert "500" in str(result["error"])


@pytest.mark.asyncio
async def test_health_check_timeout():
    """Test health check with connection timeout."""
    import httpx

    mock_client = MagicMock()
    mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await health_check_wordpress("https://example.com", timeout=5)

    assert result["healthy"] is False
    assert result["error"] is not None
    assert "timeout" in result["error"].lower() or "Timeout" in result["error"]


@pytest.mark.asyncio
async def test_auto_rollback_on_failure():
    """Test that execute_changes triggers rollback on health failure."""
    from agent.nodes.approval import execute_changes

    state = {
        "id": "op-1",
        "dry_run": False,
    }
    new_contents = {"a.php": "<?php echo 1;"}
    mock_handle_rollback = AsyncMock(return_value=("Rollback done.", False, None))

    with patch("agent.nodes.approval.get_stored_contents", return_value=new_contents):
        with patch("agent.nodes.approval.write_file"):
            with patch("agent.nodes.approval.update_operation_status"):
                with patch("agent.nodes.approval.set_awaiting_response"):
                    with patch("agent.nodes.approval.log_event"):
                        with patch("agent.nodes.approval.add_error"):
                            with patch(
                                "agent.tools.rest.health_check_wordpress",
                                new_callable=AsyncMock,
                                return_value={
                                    "healthy": False,
                                    "status_code": 500,
                                    "response_time": 0.5,
                                    "error": "HTTP 500",
                                },
                            ):
                                with patch(
                                    "agent.nodes.commands.handle_rollback",
                                    mock_handle_rollback,
                                ):
                                    with patch("agent.nodes.approval.mark_task_completed", return_value=None):
                                        with patch("interfaces.webhooks.record_deployment_verification"):
                                            with patch("interfaces.webhooks.notify_webhook", new_callable=AsyncMock):
                                                with patch("agent.nodes.approval.asyncio.sleep", new_callable=AsyncMock):
                                                    text, awaiting, input_type, next_task_id = await execute_changes(
                                                        "chat1", "http", state, task_id="task-1"
                                                    )

    mock_handle_rollback.assert_called_once_with("chat1", "http")
    assert "AUTO-ROLLBACK" in text or "auto-rollback" in text.lower()
    assert "DEPLOYMENT FAILED" in text or "failed" in text.lower()
    assert awaiting is False
    assert input_type is None


@pytest.mark.asyncio
async def test_scenario3_forced_auto_rollback_in_test_mode():
    """
    Scenario 3: when test_mode=True and the special marker is present in user_input,
    execute_changes should trigger auto-rollback without calling the real health check.
    """
    from agent.nodes.approval import execute_changes, SCENARIO3_FORCE_ROLLBACK_TOKEN

    state = {
        "id": "op-s3",
        "dry_run": False,
        "test_mode": True,
        "user_input": f"Zmiana dla scenariusza 3 {SCENARIO3_FORCE_ROLLBACK_TOKEN}",
    }
    new_contents = {"a.php": "<?php echo 1;"}
    mock_handle_rollback = AsyncMock(return_value=("Rollback done.", False, None))

    with patch("agent.nodes.approval.get_stored_contents", return_value=new_contents):
        with patch("agent.nodes.approval.write_file"):
            with patch("agent.nodes.approval.update_operation_status"):
                with patch("agent.nodes.approval.set_awaiting_response"):
                    with patch("agent.nodes.approval.log_event"):
                        with patch("agent.nodes.approval.add_error"):
                            # health_check_wordpress should NOT be called when Scenario3 forced failure is active
                            with patch(
                                "agent.tools.rest.health_check_wordpress",
                                new_callable=AsyncMock,
                            ) as mock_health:
                                with patch(
                                    "agent.nodes.commands.handle_rollback",
                                    mock_handle_rollback,
                                ):
                                    with patch("agent.nodes.approval.mark_task_completed", return_value=None):
                                        with patch("interfaces.webhooks.record_deployment_verification"):
                                            with patch("interfaces.webhooks.notify_webhook", new_callable=AsyncMock):
                                                with patch("agent.nodes.approval.asyncio.sleep", new_callable=AsyncMock):
                                                    text, awaiting, input_type, next_task_id = await execute_changes(
                                                        "chat-s3", "http", state, task_id="task-s3"
                                                    )

    # health_check_wordpress should not be hit in forced failure path
    mock_health.assert_not_awaited()
    # Rollback should have been triggered once for this chat/source
    mock_handle_rollback.assert_called_once_with("chat-s3", "http")
    assert "AUTO-ROLLBACK" in text or "auto-rollback" in text.lower()
    assert "DEPLOYMENT FAILED" in text or "failed" in text.lower()
    assert awaiting is False
    assert input_type is None
