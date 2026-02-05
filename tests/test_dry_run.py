"""Tests for dry-run mode."""
import pytest
from unittest.mock import patch, AsyncMock

from agent.nodes.approval import execute_changes


@pytest.mark.asyncio
async def test_dry_run_skips_file_writes():
    """Dry-run mode should not write files."""
    chat_id = "test_dry"
    task_id = "dry_task_1"
    source = "http"
    state = {
        "chat_id": chat_id,
        "source": source,
        "tasks": {
            task_id: {
                "id": "op_1",
                "dry_run": True,
                "diffs": {"test.php": "diff content"},
            }
        },
        "active_task_id": task_id,
        "task_queue": [],
    }

    with patch("agent.nodes.approval.write_file", new_callable=AsyncMock) as mock_write:
        with patch("agent.nodes.approval.get_stored_diffs", return_value={"test.php": "diff"}):
            with patch("agent.nodes.approval.mark_task_completed", return_value=None):
                response, awaiting, input_type, next_id = await execute_changes(
                    chat_id, source, state, task_id=task_id
                )

    mock_write.assert_not_called()
    assert "DRY-RUN" in response
    assert "test.php" in response
    assert awaiting is False
    assert input_type is None


@pytest.mark.asyncio
async def test_normal_mode_writes_files():
    """Normal mode (dry_run=False) should write files."""
    chat_id = "test_normal"
    task_id = "normal_task_1"
    source = "http"
    state = {
        "chat_id": chat_id,
        "source": source,
        "tasks": {
            task_id: {
                "id": "op_1",
                "dry_run": False,
                "diffs": {"test.css": "diff"},
                "new_contents": {"test.css": "new content"},
            }
        },
        "active_task_id": task_id,
        "task_queue": [],
    }

    with patch("agent.nodes.approval.get_stored_contents", return_value={"test.css": "new content"}):
        with patch("agent.nodes.approval.write_file") as mock_write:
            with patch("agent.nodes.approval.update_operation_status"):
                with patch("agent.nodes.approval.set_awaiting_response"):
                    with patch("agent.nodes.approval.log_event"):
                        with patch("agent.nodes.approval.add_error"):
                            response, awaiting, input_type, _ = await execute_changes(
                                chat_id, source, state, task_id=task_id
                            )

    mock_write.assert_called_once()
    assert mock_write.call_args[0][0] == "test.css"
    assert "Zapisano" in response or "deploy" in response.lower()


def test_worker_api_dry_run_parameter():
    """Worker API should accept and return dry_run parameter."""
    from contextlib import nullcontext
    from fastapi.testclient import TestClient
    from interfaces.api import app
    from agent.state import OperationStatus

    client = TestClient(app)

    # POST with dry_run=true: simulate queued path so we get 200 with dry_run=True
    with patch("interfaces.api.agent_lock", lambda **kw: nullcontext()):
        with patch("interfaces.api.load_state") as mock_load:
            with patch("interfaces.api.get_active_task_id", return_value="active-123"):
                with patch("interfaces.api.add_task_to_queue", return_value=1) as mock_add:
                    mock_load.return_value = {
                        "chat_id": "test_dry_api",
                        "source": "http",
                        "tasks": {"active-123": {"status": OperationStatus.PLANNING}},
                        "active_task_id": "active-123",
                        "task_queue": [],
                    }
                    response = client.post(
                        "/worker/task?dry_run=true",
                        json={"instruction": "test", "chat_id": "test_dry_api"},
                    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data.get("dry_run") is True
    mock_add.assert_called_once()
    # add_task_to_queue should receive dry_run=True (keyword)
    assert mock_add.call_args.kwargs.get("dry_run") is True

    # POST without dry_run: simulate same queued path, default dry_run=False
    with patch("interfaces.api.agent_lock", lambda **kw: nullcontext()):
        with patch("interfaces.api.load_state") as mock_load2:
            with patch("interfaces.api.get_active_task_id", return_value="active-456"):
                with patch("interfaces.api.add_task_to_queue", return_value=1) as mock_add2:
                    mock_load2.return_value = {
                        "chat_id": "test_normal_api",
                        "source": "http",
                        "tasks": {"active-456": {"status": OperationStatus.PLANNING}},
                        "active_task_id": "active-456",
                        "task_queue": [],
                    }
                    response2 = client.post(
                        "/worker/task",
                        json={"instruction": "test", "chat_id": "test_normal_api"},
                    )
    assert response2.status_code == 200, response2.text
    data2 = response2.json()
    assert data2.get("dry_run") is False
    assert mock_add2.call_args.kwargs.get("dry_run") is False
