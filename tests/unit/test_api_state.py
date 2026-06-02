"""Unit tests for api/_state.py — shared API-level state."""

import pytest

from api._state import _worker_loop_ref, health_metrics


class TestWorkerLoopRef:
    def test_initial_is_none(self):
        assert _worker_loop_ref is None

    @pytest.mark.asyncio
    async def test_can_be_assigned(self):
        import asyncio
        task = asyncio.create_task(asyncio.sleep(0))
        try:
            import api._state as state
            state._worker_loop_ref = task
            assert state._worker_loop_ref is task
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        # Reset
        import api._state as state
        state._worker_loop_ref = None


class TestHealthMetrics:
    def test_initial_structure(self):
        assert "startup_time" in health_metrics
        assert "last_success" in health_metrics
        assert "total_tasks" in health_metrics
        assert "failed_tasks" in health_metrics
        assert "errors_last_hour" in health_metrics
        assert "last_deployment_verification" in health_metrics

    def test_default_values(self):
        assert health_metrics["startup_time"] is None
        assert health_metrics["total_tasks"] == 0
        assert health_metrics["failed_tasks"] == 0
        assert health_metrics["errors_last_hour"] == []

    def test_deployment_verification_defaults(self):
        dv = health_metrics["last_deployment_verification"]
        assert dv["timestamp"] is None
        assert dv["healthy"] is None
        assert dv["auto_rollback_count"] == 0

    def test_can_update_metrics(self):
        health_metrics["total_tasks"] = 5
        assert health_metrics["total_tasks"] == 5
        health_metrics["total_tasks"] = 0  # reset
