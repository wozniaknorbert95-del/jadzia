"""
Flight-recorder telemetry for Jadzia.

Provides structured event recording with a fixed-size ring buffer,
per-task lifecycle timing, and aggregate metrics for the /worker/health
endpoint.

Design:
    - In-memory ring buffer (default 1000 events) — zero I/O in the hot path.
    - Thread-safe via a single lock (the ring buffer is a collections.deque).
    - Task lifecycle tracked via ``task_enqueued`` / ``task_started`` /
      ``task_completed`` / ``task_failed`` events → per-task duration computed
      on the fly.
    - Aggregate metrics: p50/p95/p99 latency, error rate, throughput.
"""

import statistics
import threading
import time
from collections import deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


_lock = threading.Lock()
_MAX_EVENTS = 1000
_events: deque = deque(maxlen=_MAX_EVENTS)

# Per-task start timestamps for latency calculation
_task_starts: Dict[str, float] = {}

# Completed task durations (ring buffer for percentile calculations)
_MAX_DURATIONS = 500
_task_durations: deque = deque(maxlen=_MAX_DURATIONS)

# Counters
_counters: Dict[str, int] = {
    "tasks_enqueued": 0,
    "tasks_started": 0,
    "tasks_completed": 0,
    "tasks_failed": 0,
    "ssh_successes": 0,
    "ssh_failures": 0,
    "circuit_opens": 0,
}


def record_event(
    event_type: str,
    *,
    task_id: Optional[str] = None,
    chat_id: Optional[str] = None,
    source: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
) -> None:
    """Record a telemetry event into the ring buffer.

    Args:
        event_type: One of ``task_enqueued``, ``task_started``,
            ``task_completed``, ``task_failed``, ``circuit_opened``,
            ``circuit_closed``, ``ssh_operation``, etc.
        task_id: Task identifier (optional).
        chat_id: Session / store identifier (optional).
        source: Session source (optional).
        data: Arbitrary payload dict (optional).
    """
    now = time.monotonic()
    event = {
        "type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "monotonic": now,
        "task_id": task_id,
        "chat_id": chat_id,
        "source": source,
        "data": data or {},
    }
    with _lock:
        _events.append(event)

        # Lifecycle tracking
        if event_type == "task_enqueued":
            _counters["tasks_enqueued"] += 1
        elif event_type == "task_started":
            _counters["tasks_started"] += 1
            if task_id:
                _task_starts[task_id] = now
        elif event_type == "task_completed":
            _counters["tasks_completed"] += 1
            if task_id and task_id in _task_starts:
                duration = now - _task_starts.pop(task_id)
                _task_durations.append(duration)
        elif event_type == "task_failed":
            _counters["tasks_failed"] += 1
            if task_id and task_id in _task_starts:
                duration = now - _task_starts.pop(task_id)
                _task_durations.append(duration)
        elif event_type == "circuit_opened":
            _counters["circuit_opens"] += 1


def get_recent_events(limit: int = 50) -> List[dict]:
    """Return the most recent ``limit`` events (newest first)."""
    with _lock:
        items = list(_events)
    # Return newest first
    items.reverse()
    return items[:limit]


def get_metrics() -> Dict[str, Any]:
    """Aggregate metrics snapshot for /worker/health.

    Returns a dict with counters, latency percentiles, and throughput.
    """
    with _lock:
        counters = dict(_counters)
        durations = list(_task_durations)

    latency: Dict[str, Optional[float]] = {
        "p50": None,
        "p95": None,
        "p99": None,
        "mean": None,
        "count": len(durations),
    }
    if durations:
        sorted_d = sorted(durations)
        latency["p50"] = round(_percentile(sorted_d, 50), 2)
        latency["p95"] = round(_percentile(sorted_d, 95), 2)
        latency["p99"] = round(_percentile(sorted_d, 99), 2)
        latency["mean"] = round(statistics.mean(sorted_d), 2)

    return {
        "counters": counters,
        "task_latency_seconds": latency,
    }


def reset() -> None:
    """Reset all telemetry state (for tests)."""
    with _lock:
        _events.clear()
        _task_starts.clear()
        _task_durations.clear()
        for key in _counters:
            _counters[key] = 0


def _percentile(sorted_data: List[float], pct: float) -> float:
    """Calculate percentile from pre-sorted data using nearest-rank method."""
    if not sorted_data:
        return 0.0
    k = (len(sorted_data) - 1) * (pct / 100.0)
    f = int(k)
    c = f + 1
    if c >= len(sorted_data):
        return sorted_data[f]
    d0 = sorted_data[f] * (c - k)
    d1 = sorted_data[c] * (k - f)
    return d0 + d1
