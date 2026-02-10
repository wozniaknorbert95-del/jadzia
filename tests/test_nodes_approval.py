"""
Tests for agent/nodes/approval (handle_approval, execute_changes).

Run: pytest tests/test_nodes_approval.py -v
"""

import pytest
from unittest.mock import patch, AsyncMock

from agent.nodes.approval import handle_approval, execute_changes


@pytest.mark.asyncio
async def test_handle_approval_no():
    """Odrzucenie: clear_state wywołane, zwraca tekst o odrzuceniu."""
    with patch("agent.nodes.approval.clear_state") as mock_clear:
        with patch("agent.nodes.approval.log_event"):
            text, awaiting, input_type, _ = await handle_approval(
                "chat1", "http", {"id": "op-1", "awaiting_type": "approval"}, False
            )
    mock_clear.assert_called_once_with("chat1", "http")
    assert "odrzucone" in text or "anulowana" in text
    assert awaiting is False
    assert input_type is None


@pytest.mark.asyncio
async def test_handle_approval_yes():
    """Zatwierdzenie przy awaiting_type=approval: wywołuje write_file, zwraca deploy_approval."""
    state = {"id": "op-1", "awaiting_type": "approval"}
    with patch("agent.nodes.approval.get_stored_contents", return_value={"f.php": "<?php echo 1;"}):
        with patch("agent.nodes.approval.write_file"):
            with patch("agent.nodes.approval.update_operation_status"):
                with patch("agent.nodes.approval.set_awaiting_response"):
                    with patch("agent.nodes.approval.log_event"):
                        with patch("agent.nodes.approval.add_error"):
                            text, awaiting, input_type, _ = await handle_approval(
                                "chat1", "http", state, True
                            )
    assert "Zapisano" in text
    assert awaiting is True
    assert input_type == "deploy_approval"


@pytest.mark.asyncio
async def test_execute_changes():
    """execute_changes: mock write_file, zwraca msg z listą plików i deploy."""
    state = {"id": "op-1"}
    new_contents = {"a.php": "content a", "b.css": "content b"}
    with patch("agent.nodes.approval.get_stored_contents", return_value=new_contents):
        with patch("agent.nodes.approval.write_file") as mock_write:
            with patch("agent.nodes.approval.update_operation_status"):
                with patch("agent.nodes.approval.set_awaiting_response"):
                    with patch("agent.nodes.approval.log_event"):
                        with patch("agent.nodes.approval.add_error"):
                            text, awaiting, input_type, _ = await execute_changes(
                                "chat1", "http", state
                            )
    assert mock_write.call_count == 2
    call_args = mock_write.call_args_list[0][0]
    assert call_args[0] == "a.php"
    assert call_args[1] == "content a"
    assert call_args[2] == "op-1"
    assert call_args[3] == "chat1"
    assert call_args[4] == "http"
    assert "Zapisano" in text
    assert "a.php" in text
    assert "strona" in text.lower() and ("działa" in text.lower() or "sprawdź" in text.lower())
    assert input_type == "deploy_approval"


@pytest.mark.asyncio
async def test_handle_approval_deploy():
    """Zatwierdzenie przy deploy_approval: mock deploy, zwraca Deploy zakonczony."""
    state = {"id": "op-1", "awaiting_type": "deploy_approval"}
    with patch("agent.nodes.approval.deploy", return_value={"status": "ok", "msg": "OK"}):
        with patch("agent.nodes.approval.clear_state") as mock_clear:
            with patch("agent.nodes.approval.update_operation_status"):
                with patch("agent.nodes.approval.log_event"):
                    text, awaiting, input_type, _ = await handle_approval(
                        "chat1", "http", state, True
                    )
    mock_clear.assert_called_once_with("chat1", "http")
    assert "Zadanie zakończone" in text or "zakonczony" in text
    assert awaiting is False
    assert input_type is None
