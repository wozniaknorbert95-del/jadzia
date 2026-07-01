"""Integration tests for the new api/app.py (create_app) routes.

Run: pytest tests/test_api_integration.py -v
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from api.app import create_app


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _get_routes(app):
    """Return set of (method, path) registered on the app."""
    routes = set()
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            for method in route.methods:
                if method != "HEAD":
                    routes.add((method, route.path))
    return routes


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def app():
    """Create a fresh FastAPI app for each test (no startup events triggered)."""
    return create_app()


@pytest.fixture
def client(app):
    """TestClient without context manager — startup events NOT fired."""
    return TestClient(app)


# ──────────────────────────────────────────────
# Route registration
# ──────────────────────────────────────────────

class TestRouteRegistration:
    """Verify create_app() registers all expected routers."""

    def test_all_expected_routes_registered(self, app):
        routes = _get_routes(app)

        expected = {
            ("GET", "/"),
            ("GET", "/health"),
            ("GET", "/status"),
            ("POST", "/rollback"),
            ("GET", "/test-ssh"),
            ("POST", "/clear"),
            ("GET", "/logs"),
            ("POST", "/chat"),
            ("POST", "/api/v1/widget/chat"),
            ("POST", "/api/v1/portal/qualify"),
            ("POST", "/api/v1/leads"),
            ("GET", "/api/v1/analytics/snapshot"),
            ("GET", "/api/v1/content-calendar"),
            ("POST", "/api/v1/content-calendar"),
            ("PATCH", "/api/v1/content-calendar/{entry_id}"),
            ("GET", "/api/v1/content-calendar/suggestions/orders"),
            ("POST", "/api/v1/content-calendar/{entry_id}/publish"),
            ("GET", "/api/v1/content-calendar/{entry_id}/publish-status"),
            ("POST", "/webhooks/woocommerce/order"),
            ("POST", "/worker/task"),
            ("GET", "/worker/task/{task_id}"),
            ("POST", "/worker/task/{task_id}/input"),
            ("POST", "/worker/tasks/cleanup"),
            ("GET", "/worker/dashboard"),
            ("GET", "/worker/health"),
            ("GET", "/costs"),
            ("POST", "/costs/reset"),
            ("POST", "/costs/estimate"),
            ("GET", "/sessions"),
            ("POST", "/sessions/cleanup"),
            # FastAPI auto-generated
            ("GET", "/docs"),
            ("GET", "/docs/oauth2-redirect"),
            ("GET", "/redoc"),
            ("GET", "/openapi.json"),
        }

        missing = expected - routes
        extra = routes - expected

        assert not missing, f"Missing routes: {missing}"
        assert not extra, f"Unexpected routes: {extra}"

    def test_telegram_router_not_included_by_default(self, app):
        routes = _get_routes(app)
        telegram = {r for r in routes if "telegram" in r[1].lower()}
        assert len(telegram) == 0, f"Telegram routes present without env: {telegram}"


# ──────────────────────────────────────────────
# Health endpoints
# ──────────────────────────────────────────────

class TestHealthEndpoints:

    def test_root_health(self, client):
        r = client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["agent"] == "JADZIA"

    def test_health_check(self, client):
        with patch("agent.tools.rest.health_check", return_value={"status": "ok", "shop": "ok"}):
            r = client.get("/health")
        assert r.status_code == 200

    def test_status_idle_when_no_state(self, client):
        with patch("agent.state.load_state", return_value=None):
            r = client.get("/status")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "idle", f"Expected idle, got {data}"
        assert data["operation"] is None

    def test_status_with_active_state(self, client):
        fake_state = {
            "tasks": {
                "task-1": {
                    "id": "op_123",
                    "status": "planning",
                    "user_input": "change color",
                    "created_at": "2026-01-01T00:00:00+00:00",
                    "files_to_modify": [],
                    "written_files": {},
                    "awaiting_response": False,
                }
            },
            "active_task_id": "task-1",
        }
        with patch("agent.state.load_state", return_value=fake_state):
            r = client.get("/status")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "planning"
        assert data["operation"] is not None
        assert data["operation"]["id"] == "op_123"

    def test_logs(self, client):
        fake_logs = [{"ts": "2026-01-01T00:00:00+00:00", "msg": "test"}]
        with patch("agent.log.get_recent_logs", return_value=fake_logs):
            r = client.get("/logs?limit=2")
        assert r.status_code == 200
        data = r.json()
        assert "logs" in data
        assert len(data["logs"]) == 1

    def test_clear_state(self, client):
        with patch("agent.state.force_unlock", return_value=True), \
             patch("agent.state.clear_state") as mock_clear:
            r = client.post("/clear")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        mock_clear.assert_called_once()

    def test_rollback(self, client):
        with patch("agent.tools.rest.rollback",
                   return_value={"status": "ok", "restored": [], "errors": [], "msg": "OK"}), \
             patch("agent.alerts.send_alert"), \
             patch("agent.state.clear_state"):
            r = client.post("/rollback")
        assert r.status_code == 200

    def test_test_ssh(self, client):
        with patch("agent.tools.rest.test_ssh_connection", return_value=(True, "SSH OK")):
            r = client.get("/test-ssh")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


# ──────────────────────────────────────────────
# Worker endpoints (no JWT — dev/CI mode)
# ──────────────────────────────────────────────

class TestWorkerEndpointsNoAuth:

    def test_create_task(self, client):
        with patch("api.routes.worker.add_task_to_queue", return_value=1):
            r = client.post(
                "/worker/task",
                json={"instruction": "test task", "chat_id": "ci_test"},
            )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "queued"
        assert data["position_in_queue"] >= 1
        assert "task_id" in data

    def test_get_task_not_found(self, client):
        with patch("api.routes.worker.find_session_by_task_id", return_value=None):
            r = client.get("/worker/task/nonexistent-id")
        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()

    def test_get_task_found(self, client):
        fake_session = ("ci_test", "http")
        fake_payload = {
            "id": "op_1",
            "status": "planning",
            "awaiting_response": False,
            "awaiting_type": None,
            "last_response": "",
            "user_input": "test",
            "plan": None,
            "diffs": {},
            "files_to_modify": [],
            "created_at": "2026-01-01T00:00:00+00:00",
            "dry_run": False,
            "test_mode": False,
        }
        with patch("api.routes.worker.find_session_by_task_id", return_value=fake_session), \
             patch("api.routes.worker.find_task_by_id", return_value=fake_payload), \
             patch("api.routes.worker.load_state", return_value={
                 "tasks": {"task-1": fake_payload},
                 "active_task_id": "task-1",
                 "task_queue": [],
             }):
            r = client.get("/worker/task/task-1")
        assert r.status_code == 200
        data = r.json()
        assert data["task_id"] == "task-1"
        assert "status" in data

    def test_create_task_locked(self, client):
        from agent.state import LockError
        with patch("api.routes.worker.add_task_to_queue", side_effect=LockError("locked")):
            r = client.post(
                "/worker/task",
                json={"instruction": "test", "chat_id": "ci_test"},
            )
        assert r.status_code == 503

    def test_worker_health(self, client):
        with patch("api._state._worker_loop_ref", None), \
             patch("api._state.health_metrics", {"startup_time": None, "errors_last_hour": [], "failed_tasks": 0}):
            r = client.get("/worker/health")
        assert r.status_code == 200
        data = r.json()
        assert "status" in data

    def test_worker_dashboard_db_unavailable(self, client):
        with patch("agent.db.db_get_dashboard_metrics", side_effect=RuntimeError("db down")):
            r = client.get("/worker/dashboard")
        assert r.status_code == 200
        data = r.json()
        assert data.get("error") == "db_unavailable"
        assert data.get("total_tasks") == 0


# ──────────────────────────────────────────────
# Session endpoints
# ──────────────────────────────────────────────

class TestSessionEndpoints:

    def test_list_sessions(self, client):
        fake = [{"chat_id": "test", "source": "http"}]
        with patch("api.routes.sessions.list_active_sessions", return_value=fake):
            r = client.get("/sessions")
        assert r.status_code == 200
        data = r.json()
        assert "sessions" in data
        assert len(data["sessions"]) == 1

    def test_cleanup_sessions(self, client):
        with patch("api.routes.sessions.cleanup_old_sessions", return_value=3):
            r = client.post("/sessions/cleanup?days=7")
        assert r.status_code == 200
        data = r.json()
        assert data["removed"] == 3


# ──────────────────────────────────────────────
# Cost endpoints
# ──────────────────────────────────────────────

class TestCostEndpoints:

    def test_cost_estimate(self, client):
        # tiktoken not installed in CI; inject mock into sys.modules
        mock_tiktoken = MagicMock()
        mock_tiktoken.encoding_for_model.return_value.encode.return_value = [1, 2, 3]
        with patch.dict("sys.modules", {"tiktoken": mock_tiktoken}):
            r = client.post("/costs/estimate", json={"message": "Hello, how much?"})
        assert r.status_code == 200
        data = r.json()
        assert "estimated_cost" in data
        assert "estimated_input_tokens" in data
        assert data["estimated_cost"] >= 0


# ──────────────────────────────────────────────
# JWT auth
# ──────────────────────────────────────────────

class TestJWTAuth:

    JWT_SECRET_VALUE = "test-secret-for-integration-tests"

    def test_worker_task_returns_401_without_token(self, client):
        with patch.dict(os.environ, {"JWT_SECRET": self.JWT_SECRET_VALUE}, clear=False), \
             patch("api.dependencies.JWT_SECRET", self.JWT_SECRET_VALUE):
            r = client.post("/worker/task", json={"instruction": "test", "chat_id": "test"})
        assert r.status_code == 401

    def test_worker_task_returns_200_with_valid_token(self, client):
        import jwt as pyjwt
        token = pyjwt.encode({"sub": "test"}, self.JWT_SECRET_VALUE, algorithm="HS256")

        with patch.dict(os.environ, {"JWT_SECRET": self.JWT_SECRET_VALUE}, clear=False), \
             patch("api.dependencies.JWT_SECRET", self.JWT_SECRET_VALUE), \
             patch("api.routes.worker.add_task_to_queue", return_value=1):
            r = client.post(
                "/worker/task",
                json={"instruction": "test", "chat_id": "ci_test"},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert r.status_code == 200

    def test_worker_task_returns_401_with_invalid_token(self, client):
        with patch.dict(os.environ, {"JWT_SECRET": self.JWT_SECRET_VALUE}, clear=False), \
             patch("api.dependencies.JWT_SECRET", self.JWT_SECRET_VALUE):
            r = client.post(
                "/worker/task",
                json={"instruction": "test", "chat_id": "ci_test"},
                headers={"Authorization": "Bearer invalid-token"},
            )
        assert r.status_code == 401


# ──────────────────────────────────────────────
# Error handling
# ──────────────────────────────────────────────

class TestErrorHandling:

    def test_404_on_unknown_route(self, client):
        r = client.get("/nonexistent")
        assert r.status_code == 404

    def test_422_on_invalid_json_body(self, client):
        r = client.post("/chat", json={"invalid": "data"})
        assert r.status_code == 422

    def test_500_on_unhandled_exception(self, client):
        # Use a separate client that doesn't propagate exceptions
        no_raise_client = TestClient(create_app(), raise_server_exceptions=False)
        with patch("agent.tools.rest.health_check", side_effect=RuntimeError("boom")):
            r = no_raise_client.get("/health")
        assert r.status_code == 500
