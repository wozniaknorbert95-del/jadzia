"""
Tests for concurrent tasks (multi-task queue, FIFO, thread safety, completion triggers next).

Run: pytest tests/test_concurrent_tasks.py -v
"""

import uuid
import pytest
from unittest.mock import patch, AsyncMock
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi.testclient import TestClient

from agent.state import (
    clear_state,
    load_state,
    create_operation,
    add_task_to_queue,
    get_next_task_from_queue,
    get_active_task_id,
    find_task_by_id,
    find_session_by_task_id,
    mark_task_completed,
    update_operation_status,
    OperationStatus,
)
from interfaces.api import app

CHAT_A = "concurrent_chat_a"
CHAT_B = "concurrent_chat_b"
SOURCE = "http"


def _is_uuid(s: str) -> bool:
    try:
        uuid.UUID(s)
        return True
    except (ValueError, TypeError):
        return False


@pytest.fixture(autouse=True)
def clean_concurrent_state():
    clear_state(CHAT_A, SOURCE)
    clear_state(CHAT_B, SOURCE)
    yield
    clear_state(CHAT_A, SOURCE)
    clear_state(CHAT_B, SOURCE)


def test_multiple_tasks_queued():
    """POST two tasks to same session; second returns status queued and position_in_queue > 0."""
    async def mock_process_message(user_input: str, chat_id: str, source=None, task_id=None, dry_run=False, webhook_url=None, test_mode: bool = False):
        create_operation(user_input, chat_id, source or "http", task_id=task_id)
        return ("First task response", True, "approval")

    client = TestClient(app)
    with patch("interfaces.api.process_message", new_callable=AsyncMock) as mock_pm:
        mock_pm.side_effect = mock_process_message
        r1 = client.post("/worker/task", json={"instruction": "first", "chat_id": CHAT_A})
        assert r1.status_code == 200, r1.text
        d1 = r1.json()
        assert d1["status"] in ("processing", "created")
        assert d1["position_in_queue"] == 0
        task_id_1 = d1["task_id"]

        r2 = client.post("/worker/task", json={"instruction": "second", "chat_id": CHAT_A})
        assert r2.status_code == 200, r2.text
        d2 = r2.json()
        assert d2["status"] == "queued"
        assert d2["position_in_queue"] >= 1
        assert _is_uuid(d2["task_id"])

    r_get = client.get(f"/worker/task/{d2['task_id']}")
    assert r_get.status_code == 200
    assert r_get.json().get("position_in_queue", 0) >= 1


def test_task_processing_order():
    """Enqueue 2 tasks; complete first; second becomes active (FIFO)."""
    create_operation("first", CHAT_A, SOURCE)
    state = load_state(CHAT_A, SOURCE)
    tid1 = get_active_task_id(CHAT_A, SOURCE)
    assert tid1

    tid2 = str(uuid.uuid4())
    add_task_to_queue(CHAT_A, tid2, "second", SOURCE)
    assert get_active_task_id(CHAT_A, SOURCE) == tid1

    next_id = mark_task_completed(CHAT_A, tid1, SOURCE)
    assert next_id == tid2
    assert get_active_task_id(CHAT_A, SOURCE) == tid2


def test_active_task_blocks_new():
    """With one active task, POST another; assert it is queued, not started immediately."""
    async def mock_process_message(user_input: str, chat_id: str, source=None, task_id=None, dry_run=False, webhook_url=None, test_mode: bool = False):
        create_operation(user_input, chat_id, source or "http", task_id=task_id)
        return ("OK", False, None)

    client = TestClient(app)
    with patch("interfaces.api.process_message", new_callable=AsyncMock) as mock_pm:
        mock_pm.side_effect = mock_process_message
        r1 = client.post("/worker/task", json={"instruction": "active", "chat_id": CHAT_A})
        assert r1.status_code == 200
        assert r1.json()["position_in_queue"] == 0

        r2 = client.post("/worker/task", json={"instruction": "blocked", "chat_id": CHAT_A})
        assert r2.status_code == 200
        assert r2.json()["status"] == "queued"
        assert r2.json()["position_in_queue"] >= 1


def test_thread_safe_state_writes():
    """Concurrent add_task_to_queue / update_operation_status do not corrupt state."""
    create_operation("base", CHAT_A, SOURCE)
    base_tid = get_active_task_id(CHAT_A, SOURCE)

    def add_one(i):
        tid = str(uuid.uuid4())
        add_task_to_queue(CHAT_A, tid, f"instruction_{i}", SOURCE)
        return tid

    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = [ex.submit(add_one, i) for i in range(10)]
        ids = [f.result() for f in as_completed(futures)]

    state = load_state(CHAT_A, SOURCE)
    assert state is not None
    tasks = state.get("tasks", {})
    queue = state.get("task_queue", [])
    assert base_tid in tasks
    for tid in ids:
        assert tid in tasks
    assert len(queue) == 10
    assert len(set(queue)) == 10
    assert len(tasks) == 11


def test_task_completion_triggers_next():
    """One active, one queued; complete active (mock); next task becomes active."""
    create_operation("first", CHAT_A, SOURCE)
    tid1 = get_active_task_id(CHAT_A, SOURCE)
    tid2 = str(uuid.uuid4())
    add_task_to_queue(CHAT_A, tid2, "second_instruction", SOURCE)

    next_id = mark_task_completed(CHAT_A, tid1, SOURCE)
    assert next_id == tid2
    state = load_state(CHAT_A, SOURCE)
    assert state.get("active_task_id") == tid2
    assert tid2 not in state.get("task_queue", [])


def test_find_task_across_sessions():
    """Create tasks in two chat_ids; find_session_by_task_id and GET return correct session/task."""
    create_operation("task in A", CHAT_A, SOURCE)
    create_operation("task in B", CHAT_B, SOURCE)
    tid_a = get_active_task_id(CHAT_A, SOURCE)
    tid_b = get_active_task_id(CHAT_B, SOURCE)
    assert tid_a and tid_b and tid_a != tid_b

    session_a = find_session_by_task_id(tid_a)
    session_b = find_session_by_task_id(tid_b)
    assert session_a == (CHAT_A, SOURCE)
    assert session_b == (CHAT_B, SOURCE)

    task_a = find_task_by_id(CHAT_A, tid_a, SOURCE)
    task_b = find_task_by_id(CHAT_B, tid_b, SOURCE)
    assert task_a is not None and task_a.get("user_input") == "task in A"
    assert task_b is not None and task_b.get("user_input") == "task in B"

    client = TestClient(app)
    r_a = client.get(f"/worker/task/{tid_a}")
    r_b = client.get(f"/worker/task/{tid_b}")
    assert r_a.status_code == 200 and r_a.json()["task_id"] == tid_a
    assert r_b.status_code == 200 and r_b.json()["task_id"] == tid_b
    assert "operation" in r_a.json() and "operation" in r_b.json()
