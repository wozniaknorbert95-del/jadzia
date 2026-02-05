"""
Tests for agent/nodes/routing (route_user_input).

Run: pytest tests/test_nodes_routing.py -v
"""

import pytest
from unittest.mock import patch, AsyncMock

from agent.nodes.routing import route_user_input


@pytest.mark.asyncio
async def test_route_commands():
    """Slash commands -> wywołanie odpowiedniego handlera, zwrot z oczekiwaną treścią."""
    with patch("agent.nodes.routing.handle_status", new_callable=AsyncMock) as mock_status:
        mock_status.return_value = ("Agent gotowy", False, None)
        text, awaiting, input_type, _ = await route_user_input("/status", "chat1", "http", AsyncMock())
    mock_status.assert_called_once_with("chat1", "http")
    assert "gotowy" in text or "Agent" in text

    with patch("agent.nodes.routing.handle_help") as mock_help:
        mock_help.return_value = ("JADZIA - Pomoc", False, None)
        text, _, _, _ = await route_user_input("/help", "chat1", "http", AsyncMock())
    mock_help.assert_called_once_with("chat1", "http")
    assert "Pomoc" in text or "JADZIA" in text

    with patch("agent.nodes.routing.handle_rollback", new_callable=AsyncMock) as mock_rb:
        mock_rb.return_value = ("Rollback OK", False, None)
        text, _, _, _ = await route_user_input("cofnij", "chat1", "http", AsyncMock())
    mock_rb.assert_called_once_with("chat1", "http")
    assert "OK" in text or "Rollback" in text


@pytest.mark.asyncio
async def test_route_approval():
    """Intent APPROVAL + state awaiting -> handle_approval called with active task_id."""
    task_id = "test_task_123"
    state = {
        "tasks": {
            task_id: {
                "awaiting_response": True,
                "id": "op-1",
                "awaiting_type": "approval",
            }
        },
        "active_task_id": task_id,
        "task_queue": [],
    }
    # Patch load_state at source (agent.state) so get_active_task_id and has_pending_operation
    # see the mock; also patch routing's reference so direct load_state() calls in routing see it.
    with patch("agent.state.load_state", return_value=state):
        with patch("agent.nodes.routing.classify_intent", new_callable=AsyncMock, return_value="APPROVAL"):
            with patch("agent.nodes.routing.load_state", return_value=state):
                with patch("agent.nodes.routing.handle_approval", new_callable=AsyncMock) as mock_appr:
                    mock_appr.return_value = ("Zatwierdzono", False, None, None)
                    text, _, _, _ = await route_user_input("tak", "chat1", "http", AsyncMock())
    mock_appr.assert_called_once()
    call_args = mock_appr.call_args
    assert call_args[0][3] is True  # approved=True
    assert call_args[1].get("task_id") == task_id


@pytest.mark.asyncio
async def test_route_new_task():
    """Brak state awaiting, intent NEW_TASK -> handle_new_task wywołany."""
    with patch("agent.nodes.routing.classify_intent", new_callable=AsyncMock, return_value="NEW_TASK"):
        with patch("agent.nodes.routing.load_state", return_value=None):
            with patch("agent.nodes.routing.has_pending_operation", return_value=False):
                with patch("agent.nodes.routing.handle_new_task", new_callable=AsyncMock) as mock_task:
                    mock_task.return_value = ("Done", False, None, None)
                    text, awaiting, input_type, _ = await route_user_input(
                        "zmien kolor", "chat1", "http", AsyncMock()
                    )
    mock_task.assert_called_once()
    assert text == "Done"
    assert awaiting is False
