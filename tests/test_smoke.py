"""Smoke test — demonstruje co Jadzia potrafi, bez mockowania.

Uruchom: python -m pytest tests/test_smoke.py -v --no-header

Pokazuje:
  1. Root health check (GET /)
  2. Health endpoint (GET /health)
  3. Status endpoint (GET /status)
  4. Worker API — create task (POST /worker/task)
  5. Worker API — get task (GET /worker/task/{id})
  6. Worker API — submit input (POST /worker/task/{id}/input)
  7. Chat endpoint (POST /chat)
  8. Rollback (POST /rollback)
  9. Clear state (POST /clear)
 10. Logs (GET /logs)
 11. Test SSH (GET /test-ssh)
 12. Worker tasks cleanup (POST /worker/tasks/cleanup)
"""

import uuid
import pytest
from fastapi.testclient import TestClient

from api.app import create_app

app = create_app()
client = TestClient(app)


def _is_uuid(val: str) -> bool:
    try:
        uuid.UUID(str(val))
        return True
    except (ValueError, TypeError):
        return False


class TestSmokeRoot:
    """1. Podstawowe health checki"""

    def test_root_health(self):
        r = client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["agent"] == "JADZIA"
        assert "version" in data

    def test_health_endpoint(self):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        # health moze byc ok lub degraded
        assert data["status"] in ("ok", "warning", "error")


class TestSmokeStatus:
    """2. Status agenta — zawsze powinien odpowiedziec"""

    def test_status_idle(self):
        r = client.get("/status")
        assert r.status_code == 200
        data = r.json()
        # idle lub z operacja
        assert "status" in data


class TestSmokeWorkerAPI:
    """3. Worker Task API — Quick ACK, GET, input"""

    CHAT_ID = "smoke_test_chat"

    def test_create_task_returns_queued(self):
        r = client.post(
            "/worker/task",
            json={"instruction": "zmień kolor przycisku na niebieski", "chat_id": self.CHAT_ID},
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert _is_uuid(data["task_id"])
        assert data["status"] == "queued"
        assert data["position_in_queue"] >= 1
        assert data["chat_id"] == self.CHAT_ID
        # dry_run domyślnie false
        assert data["dry_run"] is False

    def test_get_created_task(self):
        # najpierw stworz task
        r1 = client.post(
            "/worker/task",
            json={"instruction": "test get task", "chat_id": self.CHAT_ID},
        )
        task_id = r1.json()["task_id"]

        r2 = client.get(f"/worker/task/{task_id}")
        assert r2.status_code == 200, r2.text
        data = r2.json()
        assert data["task_id"] == task_id
        assert "status" in data
        assert "awaiting_input" in data

    def test_get_nonexistent_task_returns_404(self):
        r = client.get(f"/worker/task/{uuid.uuid4()}")
        assert r.status_code == 404

    def test_create_task_with_dry_run(self):
        r = client.post(
            "/worker/task?dry_run=true",
            json={"instruction": "suchy przebieg", "chat_id": self.CHAT_ID},
        )
        assert r.status_code == 200, r.text
        assert r.json()["dry_run"] is True

    def test_create_task_with_test_mode(self):
        r = client.post(
            "/worker/task",
            json={"instruction": "tryb testowy", "chat_id": self.CHAT_ID, "test_mode": True},
        )
        assert r.status_code == 200, r.text
        assert r.json()["test_mode"] is True


class TestSmokeChat:
    """4. Chat endpoint — podstawowe pytanie"""

    def test_chat_returns_response(self):
        r = client.post("/chat", json={"message": "co potrafisz?", "chat_id": "smoke_user"})
        # Moze byc 200 lub 500 jesli brak klucza API
        assert r.status_code in (200, 500), r.text
        if r.status_code == 200:
            data = r.json()
            assert "response" in data
            assert "awaiting_input" in data


class TestSmokeRollback:
    """5. Rollback — czysci stan"""

    def test_rollback_returns_status(self):
        r = client.post("/rollback")
        assert r.status_code == 200, r.text
        data = r.json()
        assert "status" in data


class TestSmokeMaintenance:
    """6. Endpointy utrzymaniowe"""

    def test_clear_state(self):
        r = client.post("/clear")
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["status"] == "ok"

    def test_logs(self):
        r = client.get("/logs?limit=5")
        assert r.status_code == 200, r.text
        data = r.json()
        assert "logs" in data
        assert isinstance(data["logs"], list)

    def test_ssh_endpoint(self):
        r = client.get("/test-ssh")
        assert r.status_code == 200, r.text


class TestSmokeWorkerCleanup:
    """7. Worker tasks cleanup"""

    def test_cleanup_nonexistent_tasks(self):
        r = client.post(
            "/worker/tasks/cleanup",
            json={"task_ids": [str(uuid.uuid4())], "reason": "smoke_test"},
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert any(k in data for k in ("status", "message", "not_found"))


class TestSmokeTelegram:
    """8. Telegram health (bez tokena — warning)"""

    def test_telegram_health(self):
        r = client.get("/telegram/health")
        # Telegram router moze byc nie zarejestrowany jesli TELEGRAM_BOT_ENABLED != 1
        if r.status_code == 404:
            pytest.skip("Telegram router disabled")
        assert r.status_code == 200, r.text
        data = r.json()
        assert "status" in data
        assert "service" in data
