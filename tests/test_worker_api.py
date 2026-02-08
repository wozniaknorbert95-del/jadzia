"""
Tests for Worker Task API (FAZA 1).

Run: pytest tests/test_worker_api.py -v
"""

import uuid
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from agent.state import (
    clear_state,
    create_operation,
    load_state,
    get_active_task_id,
    update_operation_status,
    OperationStatus,
)
from interfaces.api import app

WORKER_CHAT_ID = "test_worker_123"
SOURCE = "http"


def _is_uuid(s: str) -> bool:
    try:
        uuid.UUID(s)
        return True
    except (ValueError, TypeError):
        return False


@pytest.fixture(autouse=True)
def clean_worker_state():
    clear_state(WORKER_CHAT_ID, SOURCE)
    yield
    clear_state(WORKER_CHAT_ID, SOURCE)


def test_post_worker_task_then_get():
    """POST /worker/task returns task_id and status=queued (Quick ACK); GET returns task state."""
    client = TestClient(app)
    r = client.post(
        "/worker/task",
        json={"instruction": "zmień kolor przycisku", "chat_id": WORKER_CHAT_ID},
    )

    assert r.status_code == 200, r.text
    data = r.json()
    assert "task_id" in data
    assert _is_uuid(data["task_id"]), f"task_id should be UUID, got {data['task_id']}"
    assert data["status"] == "queued"
    assert "position_in_queue" in data
    assert data["position_in_queue"] >= 1

    task_id = data["task_id"]
    r2 = client.get(f"/worker/task/{task_id}")
    assert r2.status_code == 200, r2.text
    data2 = r2.json()
    assert data2["task_id"] == task_id
    assert "status" in data2
    assert "awaiting_input" in data2
    assert "input_type" in data2
    assert "response" in data2
    assert "operation" in data2
    assert "position_in_queue" in data2


def test_post_worker_task_then_input_then_completed():
    """Create task (Quick ACK) → simulate worker making it active → submit input → GET shows completed."""
    # Step 1: Quick ACK — task is queued
    client = TestClient(app)
    r1 = client.post(
        "/worker/task",
        json={"instruction": "zmień kolor przycisku", "chat_id": WORKER_CHAT_ID},
    )
    assert r1.status_code == 200, r1.text
    task_id = r1.json()["task_id"]
    assert _is_uuid(task_id)
    assert r1.json()["status"] == "queued"

    # Step 2: Simulate worker loop making task active (create_operation sets active_task_id)
    from agent.state import get_next_task_from_queue
    activated = get_next_task_from_queue(WORKER_CHAT_ID, SOURCE)
    assert activated == task_id

    # Step 3: Submit approval input; mock process_message to mark completed
    async def mock_process_message(user_input: str, chat_id: str, source=None, task_id=None, dry_run=False, webhook_url=None, test_mode: bool = False):
        update_operation_status(OperationStatus.COMPLETED, chat_id, SOURCE, task_id=task_id)
        return ("Zrobione.", False, None)

    with patch("interfaces.api.process_message", new_callable=AsyncMock) as mock_pm:
        mock_pm.side_effect = mock_process_message
        r2 = client.post(
            f"/worker/task/{task_id}/input",
            json={"approval": True},
        )
    assert r2.status_code == 200, r2.text
    data2 = r2.json()
    assert data2["task_id"] == task_id

    r3 = client.get(f"/worker/task/{task_id}")
    assert r3.status_code == 200, r3.text
    data3 = r3.json()
    assert data3["status"] == "completed"


def test_worker_task_not_found():
    """GET /worker/task/{task_id} with unknown task_id returns 404."""
    client = TestClient(app)
    r = client.get(f"/worker/task/{uuid.uuid4()}")
    assert r.status_code == 404
    assert "not found" in r.json().get("detail", "").lower()


def test_worker_task_input_requires_approval_or_answer():
    """POST /worker/task/{task_id}/input without approval or answer returns 400."""
    create_operation("dummy", WORKER_CHAT_ID, SOURCE)
    task_id = get_active_task_id(WORKER_CHAT_ID, SOURCE)
    assert task_id

    client = TestClient(app)
    r = client.post(
        f"/worker/task/{task_id}/input",
        json={},
    )
    assert r.status_code == 400
    assert "approval" in r.json().get("detail", "").lower() or "answer" in r.json().get("detail", "").lower()
