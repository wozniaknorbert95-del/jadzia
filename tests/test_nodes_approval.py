"""
Tests for agent/nodes/approval (handle_approval, execute_changes).

Run: pytest tests/test_nodes_approval.py -v
"""

import pytest
from unittest.mock import patch, AsyncMock

from agent.nodes.approval import handle_approval, execute_changes
from agent.state import OperationStatus


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
async def test_execute_changes_partial_write_rolls_back_and_never_completes():
    """Second-file failure must ROLLED_BACK / FAILED — never COMPLETED."""
    state = {"id": "op-partial", "dry_run": False}
    new_contents = {"a.php": "ok", "b.php": "fail"}

    def _write(path, content, *args, **kwargs):
        if path == "b.php":
            raise RuntimeError("simulated write failure")

    statuses: list[str] = []

    def _status(status, *args, **kwargs):
        statuses.append(status)

    with patch("agent.nodes.approval.get_stored_contents", return_value=new_contents):
        with patch("agent.nodes.approval.write_file", side_effect=_write) as mock_write:
            with patch("agent.nodes.approval.update_operation_status", side_effect=_status):
                with patch("agent.nodes.approval.log_event"):
                    with patch("agent.nodes.approval.add_error"):
                        with patch("agent.nodes.approval.send_alert"):
                            with patch(
                                "agent.tools.rest.rollback",
                                return_value={
                                    "status": "ok",
                                    "msg": "restored 1",
                                    "restored": ["a.php"],
                                },
                            ) as mock_rollback:
                                text, awaiting, input_type, next_id = await execute_changes(
                                    "chat1", "http", state
                                )

    assert mock_write.call_count == 2
    mock_rollback.assert_called_once()
    assert OperationStatus.COMPLETED not in statuses
    assert OperationStatus.ROLLED_BACK in statuses
    assert awaiting is False
    assert input_type is None
    assert next_id is None
    assert "Blad zapisu" in text or "b.php" in text


@pytest.mark.asyncio
async def test_execute_changes_all_fail_marks_failed_without_rollback():
    state = {"id": "op-fail", "dry_run": False}
    new_contents = {"a.php": "x"}

    with patch("agent.nodes.approval.get_stored_contents", return_value=new_contents):
        with patch("agent.nodes.approval.write_file", side_effect=RuntimeError("boom")):
            with patch("agent.nodes.approval.update_operation_status") as mock_status:
                with patch("agent.nodes.approval.log_event"):
                    with patch("agent.nodes.approval.add_error"):
                        with patch("agent.nodes.approval.send_alert"):
                            with patch("agent.tools.rest.rollback") as mock_rollback:
                                text, awaiting, _, _ = await execute_changes(
                                    "chat1", "http", state
                                )

    mock_rollback.assert_not_called()
    assert any(c.args[0] == OperationStatus.FAILED for c in mock_status.call_args_list)
    assert awaiting is False
    assert "boom" in text or "Blad" in text



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
