"""Health metrics wiring — process-local store must reflect runtime failures."""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

import api._state as api_state
from api.app import create_app
from api.webhooks import record_task_failure, set_health_metrics


def test_forced_failure_visible_on_worker_health(monkeypatch) -> None:
    monkeypatch.setenv("JADZIA_ENV", "development")
    monkeypatch.setenv("PUBLIC_API_DOCS_ENABLED", "1")
    metrics = {
        "startup_time": "2026-07-21T00:00:00+00:00",
        "last_success": None,
        "total_tasks": 0,
        "failed_tasks": 0,
        "errors_last_hour": [],
        "last_deployment_verification": {
            "timestamp": None,
            "healthy": None,
            "auto_rollback_count": 0,
        },
    }
    api_state.health_metrics = metrics
    set_health_metrics(metrics)

    record_task_failure("forced failure for health gate")

    app = create_app()
    with patch(
        "agent.db.db_get_worker_health_session_counts",
        return_value=(0, 0, 0, 0),
    ):
        with patch("agent.db.db_health_check", return_value=True):
            with patch(
                "agent.tools.rest.test_ssh_connection",
                return_value=(True, "ok"),
            ):
                client = TestClient(app)
                response = client.get("/worker/health")

    assert response.status_code == 200
    body = response.json()
    assert body["failed_tasks_total"] >= 1
    assert body["errors_last_hour"] >= 1
