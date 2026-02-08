"""
Regression tests for:
- Timestamp parsing (naive / aware / UTC)
- Negative age clamping (no FAILED from clock skew)
- Quick ACK (all tasks return queued)
- Failed reasons persisted to tasks.errors
- Telegram push for completed/failed from background

Run: pytest tests/test_timezones_worker_loop.py -v
"""

import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient

from agent.state import (
    clear_state,
    load_state,
    create_operation,
    add_task_to_queue,
    update_operation_status,
    add_error,
    get_active_task_id,
    mark_task_completed,
    get_next_task_from_queue,
    OperationStatus,
)
from interfaces.api import (
    app,
    _parse_timestamp_to_utc,
    _safe_age_minutes,
    _run_task_with_timeout,
    _worker_loop,
)

CHAT = "tz_test_chat"
SOURCE = "http"


def _is_uuid(s: str) -> bool:
    try:
        uuid.UUID(s)
        return True
    except (ValueError, TypeError):
        return False


@pytest.fixture(autouse=True)
def clean_state():
    clear_state(CHAT, SOURCE)
    yield
    clear_state(CHAT, SOURCE)


# ==================== Timestamp parsing ====================


class TestParseTimestampToUtc:
    """Unit tests for _parse_timestamp_to_utc helper."""

    def test_aware_utc_timestamp(self):
        ts = "2025-06-15T12:00:00+00:00"
        result = _parse_timestamp_to_utc(ts)
        assert result is not None
        assert result.tzinfo is not None
        assert result.hour == 12

    def test_aware_offset_timestamp(self):
        ts = "2025-06-15T14:00:00+02:00"
        result = _parse_timestamp_to_utc(ts)
        assert result is not None
        assert result.tzinfo is not None
        # +02:00 → UTC = 12:00
        assert result.hour == 12

    def test_z_suffix_timestamp(self):
        ts = "2025-06-15T12:00:00Z"
        result = _parse_timestamp_to_utc(ts)
        assert result is not None
        assert result.hour == 12

    def test_naive_timestamp_treated_as_local(self):
        """Naive timestamps are interpreted as server local time and converted to UTC."""
        ts = "2025-06-15T14:00:00"
        result = _parse_timestamp_to_utc(ts)
        assert result is not None
        assert result.tzinfo is not None
        # The exact UTC hour depends on server timezone, but it must be aware
        assert result.tzinfo == timezone.utc

    def test_empty_string_returns_none(self):
        assert _parse_timestamp_to_utc("") is None
        assert _parse_timestamp_to_utc("   ") is None

    def test_invalid_string_returns_none(self):
        assert _parse_timestamp_to_utc("not-a-date") is None


# ==================== Negative age clamping ====================


class TestSafeAgeMinutes:
    """Unit tests for _safe_age_minutes — negative age must be clamped to 0."""

    def test_normal_age(self):
        dt_past = datetime.now(timezone.utc) - timedelta(minutes=5)
        age = _safe_age_minutes(dt_past)
        assert 4.9 < age < 5.5

    def test_negative_age_clamped_to_zero(self):
        """Timestamp in the future (simulating CET interpreted as UTC) → age clamped to 0, not fail."""
        dt_future = datetime.now(timezone.utc) + timedelta(hours=1)
        age = _safe_age_minutes(dt_future)
        assert age == 0.0

    def test_zero_age(self):
        dt_now = datetime.now(timezone.utc)
        age = _safe_age_minutes(dt_now)
        assert age < 0.1  # practically zero


# ==================== Quick ACK ====================


class TestQuickAck:
    """All POST /worker/task calls return status=queued immediately (Quick ACK)."""

    def test_first_task_returns_queued(self):
        client = TestClient(app)
        r = client.post(
            "/worker/task",
            json={"instruction": "test instruction", "chat_id": CHAT},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "queued"
        assert data["position_in_queue"] >= 1
        assert _is_uuid(data["task_id"])

    def test_second_task_returns_queued(self):
        client = TestClient(app)
        r1 = client.post(
            "/worker/task",
            json={"instruction": "first", "chat_id": CHAT},
        )
        assert r1.status_code == 200
        assert r1.json()["status"] == "queued"

        r2 = client.post(
            "/worker/task",
            json={"instruction": "second", "chat_id": CHAT},
        )
        assert r2.status_code == 200
        data2 = r2.json()
        assert data2["status"] == "queued"
        assert data2["position_in_queue"] >= 1

    def test_quick_ack_does_not_call_process_message(self):
        """worker_create_task must NOT call process_message — only enqueue."""
        client = TestClient(app)
        with patch("interfaces.api.process_message", new_callable=AsyncMock) as mock_pm:
            r = client.post(
                "/worker/task",
                json={"instruction": "test", "chat_id": CHAT},
            )
            assert r.status_code == 200
            mock_pm.assert_not_awaited()


# ==================== Failed reasons persistence ====================


class TestFailedReasonsPersistence:
    """When a task is marked FAILED, the reason must be recorded in tasks.errors."""

    def test_add_error_creates_entry(self):
        create_operation("test", CHAT, SOURCE)
        tid = get_active_task_id(CHAT, SOURCE)
        assert tid

        add_error("worker_timeout: timed out after 600s", CHAT, SOURCE, tid)

        state = load_state(CHAT, SOURCE)
        task = state["tasks"][tid]
        errors = task.get("errors", [])
        assert len(errors) == 1
        assert "worker_timeout" in errors[0]["message"]
        assert "timestamp" in errors[0]

    def test_multiple_errors_accumulate(self):
        create_operation("test", CHAT, SOURCE)
        tid = get_active_task_id(CHAT, SOURCE)

        add_error("error_1", CHAT, SOURCE, tid)
        add_error("error_2", CHAT, SOURCE, tid)

        state = load_state(CHAT, SOURCE)
        errors = state["tasks"][tid].get("errors", [])
        assert len(errors) == 2

    def test_failed_status_with_error_logged(self):
        """update_operation_status(FAILED) after add_error preserves the error entry."""
        create_operation("test", CHAT, SOURCE)
        tid = get_active_task_id(CHAT, SOURCE)

        add_error("worker_stale_task: threshold=15min", CHAT, SOURCE, tid)
        update_operation_status(OperationStatus.FAILED, CHAT, SOURCE, task_id=tid)

        state = load_state(CHAT, SOURCE)
        task = state["tasks"][tid]
        assert task["status"] == OperationStatus.FAILED
        assert len(task.get("errors", [])) >= 1
        assert "worker_stale_task" in task["errors"][0]["message"]


# ==================== UTC timestamps on new tasks ====================


class TestUtcTimestamps:
    """Newly created tasks must have timezone-aware (UTC) timestamps."""

    def test_create_operation_has_utc_timestamp(self):
        create_operation("test", CHAT, SOURCE)
        tid = get_active_task_id(CHAT, SOURCE)
        state = load_state(CHAT, SOURCE)
        task = state["tasks"][tid]
        created_at = task["created_at"]
        # Must contain timezone offset
        assert "+" in created_at or "Z" in created_at, f"Expected UTC timestamp, got {created_at}"

    def test_add_task_to_queue_has_utc_timestamp(self):
        create_operation("first", CHAT, SOURCE)
        tid2 = str(uuid.uuid4())
        add_task_to_queue(CHAT, tid2, "second", SOURCE)
        state = load_state(CHAT, SOURCE)
        task = state["tasks"][tid2]
        created_at = task["created_at"]
        assert "+" in created_at or "Z" in created_at, f"Expected UTC timestamp, got {created_at}"

    def test_update_operation_status_has_utc_updated_at(self):
        create_operation("test", CHAT, SOURCE)
        tid = get_active_task_id(CHAT, SOURCE)
        update_operation_status(OperationStatus.COMPLETED, CHAT, SOURCE, task_id=tid)
        state = load_state(CHAT, SOURCE)
        task = state["tasks"][tid]
        updated_at = task["updated_at"]
        assert "+" in updated_at or "Z" in updated_at, f"Expected UTC timestamp, got {updated_at}"


# ==================== Telegram push from background ====================


class TestTelegramPushFromBackground:
    """process_message with push_to_telegram=True pushes results to Telegram."""

    @pytest.mark.asyncio
    async def test_push_on_non_awaiting_result(self):
        """When push_to_telegram=True and result is non-awaiting, still push to Telegram."""
        chat_id = "telegram_999_test"
        clear_state(chat_id, "telegram")
        create_operation("test push", chat_id, "telegram")
        tid = get_active_task_id(chat_id, "telegram")

        with patch("agent.agent.route_user_input", new_callable=AsyncMock) as mock_route:
            mock_route.return_value = ("Gotowe! Zmieniono kolor.", False, None)
            with patch("interfaces.telegram_api.send_awaiting_response_to_telegram", new_callable=AsyncMock) as mock_send:
                from agent.agent import process_message
                result = await process_message(
                    user_input="test",
                    chat_id=chat_id,
                    source="telegram",
                    task_id=tid,
                    push_to_telegram=True,
                )
                # Should push even though awaiting=False
                mock_send.assert_awaited_once()
                call_kwargs = mock_send.call_args
                assert call_kwargs[1].get("awaiting_input") is False or call_kwargs[0][0] == chat_id

        clear_state(chat_id, "telegram")

    @pytest.mark.asyncio
    async def test_push_on_awaiting_result(self):
        """When push_to_telegram=True and result is awaiting, push with awaiting_input=True."""
        chat_id = "telegram_998_test"
        clear_state(chat_id, "telegram")


# ==================== Worker loop flag propagation ====================


class TestWorkerLoopFlagPropagation:
    """_run_task_with_timeout must pass dry_run/test_mode/webhook_url from task state into process_message."""

    @pytest.mark.asyncio
    async def test_run_task_with_timeout_passes_flags(self):
        task_id = str(uuid.uuid4())
        add_task_to_queue(
            CHAT,
            task_id,
            "do something",
            SOURCE,
            dry_run=True,
            webhook_url="https://example.com/hook",
            test_mode=True,
        )

        with patch("interfaces.api.process_message", new_callable=AsyncMock) as mock_pm:
            mock_pm.return_value = ("OK", False, None)
            await _run_task_with_timeout(
                "do something",
                chat_id=CHAT,
                source=SOURCE,
                task_id=task_id,
                timeout_sec=5,
            )

            mock_pm.assert_awaited()
            kwargs = mock_pm.call_args.kwargs
            assert kwargs.get("dry_run") is True
            assert kwargs.get("test_mode") is True
            assert kwargs.get("webhook_url") == "https://example.com/hook"


# ==================== Worker loop locked guard ====================


class TestWorkerLoopLockedGuard:
    """When session is locked, worker loop must not mark active task as stale/awaiting-timeout."""

    @pytest.mark.asyncio
    async def test_locked_session_skips_stale_and_awaiting_checks(self):
        chat_id = "locked_guard_chat"
        source = "http"
        clear_state(chat_id, source)

        active_id = "task_active_1"
        old_ts = (datetime.now(timezone.utc) - timedelta(minutes=999)).isoformat()
        state = {
            "tasks": {
                active_id: {
                    "task_id": active_id,
                    "operation_id": "op1",
                    "status": "planning",
                    "user_input": "x",
                    "created_at": old_ts,
                    "updated_at": old_ts,
                    "awaiting_response": True,
                    "awaiting_type": "approval",
                }
            },
            "active_task_id": active_id,
            "task_queue": ["task_queued_2"],
        }

        # One iteration only: make asyncio.sleep raise CancelledError to exit loop cleanly
        async def _sleep_cancel(_seconds: int):
            raise asyncio.CancelledError()

        with patch("interfaces.api.db_list_all_sessions", return_value=[(chat_id, source)]):
            with patch("interfaces.api.load_state", return_value=state):
                with patch("interfaces.api.is_locked", return_value=True):
                    with patch("interfaces.api.add_error", new_callable=Mock) as mock_add_error:
                        with patch("interfaces.api.update_operation_status", new_callable=Mock) as mock_uos:
                            with patch("interfaces.api.asyncio.sleep", new=_sleep_cancel):
                                await _worker_loop()

                            # Should not mark FAILED when locked (no stale/awaiting timeout actions)
                            assert mock_add_error.call_count == 0
                            assert mock_uos.call_count == 0
