"""
Tests for Phase 3: Flight-Recorder Telemetry & Worker Wake Event.

Covers:
- Ring buffer capacity and overflow
- Event recording and retrieval
- Task lifecycle tracking (enqueued → started → completed/failed)
- Latency percentile calculation
- Aggregate metrics snapshot
- Counter accuracy
- Reset behaviour
- Worker wake event instant dispatch
- /worker/health telemetry integration
"""

import asyncio
import time

import pytest
from unittest.mock import patch, MagicMock

from agent.telemetry import (
    record_event,
    get_recent_events,
    get_metrics,
    reset,
    _percentile,
    _events,
    _task_starts,
    _task_durations,
    _counters,
    _MAX_EVENTS,
)


# ================================================================
# Helpers
# ================================================================


@pytest.fixture(autouse=True)
def _reset_telemetry():
    """Reset telemetry state before each test."""
    reset()
    yield
    reset()


# ================================================================
# 1. Ring Buffer
# ================================================================


class TestRingBuffer:

    def test_events_stored(self):
        record_event("test_event", task_id="t1")
        events = get_recent_events(10)
        assert len(events) == 1
        assert events[0]["type"] == "test_event"
        assert events[0]["task_id"] == "t1"

    def test_newest_first(self):
        record_event("first")
        record_event("second")
        record_event("third")
        events = get_recent_events(10)
        assert events[0]["type"] == "third"
        assert events[2]["type"] == "first"

    def test_limit(self):
        for i in range(10):
            record_event(f"event_{i}")
        events = get_recent_events(3)
        assert len(events) == 3

    def test_overflow_evicts_oldest(self):
        for i in range(_MAX_EVENTS + 50):
            record_event(f"evt_{i}")
        events = get_recent_events(_MAX_EVENTS + 100)
        assert len(events) == _MAX_EVENTS
        # Newest should be the last recorded
        assert events[0]["type"] == f"evt_{_MAX_EVENTS + 49}"

    def test_event_has_required_fields(self):
        record_event("ssh_operation", task_id="t1", chat_id="c1", source="http", data={"cmd": "ls"})
        event = get_recent_events(1)[0]
        assert "type" in event
        assert "timestamp" in event
        assert "monotonic" in event
        assert event["task_id"] == "t1"
        assert event["chat_id"] == "c1"
        assert event["source"] == "http"
        assert event["data"] == {"cmd": "ls"}


# ================================================================
# 2. Task Lifecycle Tracking
# ================================================================


class TestLifecycleTracking:

    def test_enqueued_increments_counter(self):
        record_event("task_enqueued", task_id="t1")
        metrics = get_metrics()
        assert metrics["counters"]["tasks_enqueued"] == 1

    def test_started_records_start_time(self):
        record_event("task_started", task_id="t1")
        metrics = get_metrics()
        assert metrics["counters"]["tasks_started"] == 1

    def test_completed_calculates_duration(self):
        record_event("task_started", task_id="t1")
        time.sleep(0.05)
        record_event("task_completed", task_id="t1")
        metrics = get_metrics()
        assert metrics["counters"]["tasks_completed"] == 1
        assert metrics["task_latency_seconds"]["count"] == 1
        assert metrics["task_latency_seconds"]["mean"] >= 0.04

    def test_failed_calculates_duration(self):
        record_event("task_started", task_id="t2")
        time.sleep(0.05)
        record_event("task_failed", task_id="t2")
        metrics = get_metrics()
        assert metrics["counters"]["tasks_failed"] == 1
        assert metrics["task_latency_seconds"]["count"] == 1

    def test_completed_without_start_no_duration(self):
        """Completing a task that was never started should not add a duration."""
        record_event("task_completed", task_id="orphan")
        metrics = get_metrics()
        assert metrics["counters"]["tasks_completed"] == 1
        assert metrics["task_latency_seconds"]["count"] == 0

    def test_circuit_opened_counter(self):
        record_event("circuit_opened")
        record_event("circuit_opened")
        metrics = get_metrics()
        assert metrics["counters"]["circuit_opens"] == 2

    def test_full_lifecycle(self):
        """enqueued → started → completed with duration tracking."""
        record_event("task_enqueued", task_id="t1")
        record_event("task_started", task_id="t1")
        time.sleep(0.05)
        record_event("task_completed", task_id="t1")
        metrics = get_metrics()
        assert metrics["counters"]["tasks_enqueued"] == 1
        assert metrics["counters"]["tasks_started"] == 1
        assert metrics["counters"]["tasks_completed"] == 1
        assert metrics["task_latency_seconds"]["count"] == 1
        assert metrics["task_latency_seconds"]["p50"] is not None


# ================================================================
# 3. Percentile Calculation
# ================================================================


class TestPercentile:

    def test_empty_data(self):
        assert _percentile([], 50) == 0.0

    def test_single_value(self):
        assert _percentile([5.0], 50) == 5.0
        assert _percentile([5.0], 99) == 5.0

    def test_two_values(self):
        p50 = _percentile([1.0, 3.0], 50)
        assert 1.0 <= p50 <= 3.0

    def test_known_percentiles(self):
        data = sorted([float(i) for i in range(1, 101)])  # 1.0 .. 100.0
        p50 = _percentile(data, 50)
        p99 = _percentile(data, 99)
        assert 49 <= p50 <= 51
        assert 98 <= p99 <= 100

    def test_p0_returns_first(self):
        assert _percentile([1.0, 2.0, 3.0], 0) == 1.0

    def test_p100_returns_last(self):
        assert _percentile([1.0, 2.0, 3.0], 100) == 3.0


# ================================================================
# 4. Aggregate Metrics
# ================================================================


class TestMetrics:

    def test_empty_metrics(self):
        metrics = get_metrics()
        assert metrics["counters"]["tasks_enqueued"] == 0
        assert metrics["task_latency_seconds"]["p50"] is None
        assert metrics["task_latency_seconds"]["count"] == 0

    def test_metrics_with_durations(self):
        # Simulate 3 completed tasks
        for i in range(3):
            record_event("task_started", task_id=f"t{i}")
            time.sleep(0.02)
            record_event("task_completed", task_id=f"t{i}")
        metrics = get_metrics()
        lat = metrics["task_latency_seconds"]
        assert lat["count"] == 3
        assert lat["p50"] is not None
        assert lat["p95"] is not None
        assert lat["p99"] is not None
        assert lat["mean"] is not None
        assert lat["mean"] > 0

    def test_counters_independent(self):
        record_event("task_enqueued")
        record_event("task_enqueued")
        record_event("task_started")
        record_event("task_failed")
        metrics = get_metrics()
        assert metrics["counters"]["tasks_enqueued"] == 2
        assert metrics["counters"]["tasks_started"] == 1
        assert metrics["counters"]["tasks_failed"] == 1
        assert metrics["counters"]["tasks_completed"] == 0


# ================================================================
# 5. Reset
# ================================================================


class TestReset:

    def test_reset_clears_all(self):
        record_event("task_enqueued", task_id="t1")
        record_event("task_started", task_id="t1")
        record_event("task_completed", task_id="t1")
        reset()
        assert len(get_recent_events(100)) == 0
        metrics = get_metrics()
        assert metrics["counters"]["tasks_enqueued"] == 0
        assert metrics["task_latency_seconds"]["count"] == 0


# ================================================================
# 6. Worker Wake Event
# ================================================================


class TestWorkerWakeEvent:

    @pytest.mark.asyncio
    async def test_wake_event_instant_dispatch(self):
        """Worker wake event should unblock sleep immediately."""
        wake = asyncio.Event()
        slept_full = True

        async def simulated_sleep():
            nonlocal slept_full
            wake.clear()
            try:
                await asyncio.wait_for(wake.wait(), timeout=5.0)
                slept_full = False  # Woken early
            except asyncio.TimeoutError:
                slept_full = True

        # Schedule wake signal after 50ms
        async def signal_after_delay():
            await asyncio.sleep(0.05)
            wake.set()

        t1 = asyncio.create_task(simulated_sleep())
        t2 = asyncio.create_task(signal_after_delay())
        await asyncio.gather(t1, t2)
        assert slept_full is False

    @pytest.mark.asyncio
    async def test_wake_event_timeout_if_no_signal(self):
        """Without a signal, wait_for should timeout normally."""
        wake = asyncio.Event()
        wake.clear()
        timed_out = False
        try:
            await asyncio.wait_for(wake.wait(), timeout=0.05)
        except asyncio.TimeoutError:
            timed_out = True
        assert timed_out is True


# ================================================================
# 7. /worker/health Telemetry Integration
# ================================================================


class TestHealthTelemetryIntegration:

    @pytest.mark.asyncio
    async def test_health_includes_telemetry(self):
        from interfaces.api import app
        from httpx import AsyncClient, ASGITransport

        with patch("interfaces.api.test_ssh_connection", return_value=(True, "OK")):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                resp = await client.get("/worker/health")

        assert resp.status_code == 200
        data = resp.json()
        assert "telemetry" in data
        assert "counters" in data["telemetry"]
        assert "task_latency_seconds" in data["telemetry"]
        assert "tasks_enqueued" in data["telemetry"]["counters"]

    @pytest.mark.asyncio
    async def test_health_telemetry_reflects_events(self):
        from interfaces.api import app
        from httpx import AsyncClient, ASGITransport

        # Record some events before checking health
        record_event("task_enqueued", task_id="t1")
        record_event("task_started", task_id="t1")
        record_event("task_completed", task_id="t1")

        with patch("interfaces.api.test_ssh_connection", return_value=(True, "OK")):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                resp = await client.get("/worker/health")

        data = resp.json()
        counters = data["telemetry"]["counters"]
        assert counters["tasks_enqueued"] >= 1
        assert counters["tasks_started"] >= 1
        assert counters["tasks_completed"] >= 1
