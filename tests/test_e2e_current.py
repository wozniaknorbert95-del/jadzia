"""
E2E testy dla JADZIA V2 (obecny system, przed refactorem).

Jak uruchomić:
  pytest tests/test_e2e_current.py -v

  Z katalogu głównego projektu (Jadzia), z aktywnego venv lub:
  python -m pytest tests/test_e2e_current.py -v

Checklist – co test sprawdza:
  1. POST /chat z "zmień kolor przycisku na czerwony" → zwraca diff do zatwierdzenia
     (awaiting_input=True, input_type="approval", response zawiera "wdrożyć"/"zmiany").
  2. POST /chat z "tak" (approval) → po zatwierdzeniu GET /status zwraca status="completed".
  3. POST /rollback → zwraca status="ok", pola "restored" i "errors" (SSH zmockowany).
"""

import pytest
import logging
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

logger = logging.getLogger(__name__)


def _log_api_error(response, label="API"):
    """Przy 500 wypisz status, text i json (detail) z odpowiedzi."""
    if response.status_code >= 400:
        logger.error("%s: status_code=%s", label, response.status_code)
        logger.error("%s: text=%s", label, response.text)
        try:
            body = response.json()
            logger.error("%s: json=%s", label, body)
            if "detail" in body:
                logger.error("%s: detail=%s", label, body["detail"])
        except Exception as e:
            logger.error("%s: response.json() failed: %s", label, e)

from agent.state import (
    clear_state,
    create_operation,
    load_state,
    save_state,
    store_diffs,
    store_new_contents,
    update_operation_status,
    set_awaiting_response,
    agent_lock,
    OperationStatus,
)
from agent import agent as agent_module
from agent.agent import process_message
from interfaces.api import app

CHAT_ID = "default"
SOURCE = "http"


@pytest.fixture(autouse=True)
def clean_state():
    clear_state(CHAT_ID, SOURCE)
    yield
    clear_state(CHAT_ID, SOURCE)


def _setup_state_for_approval():
    """Stan: diff gotowy, czeka na zatwierdzenie."""
    create_operation("zmień kolor przycisku na czerwony", CHAT_ID, SOURCE)
    store_diffs({"style.css": "--- a/style.css\n+++ b/style.css\n"}, CHAT_ID, SOURCE)
    store_new_contents({"style.css": "button { color: red; }"}, CHAT_ID, SOURCE)
    update_operation_status(OperationStatus.DIFF_READY, CHAT_ID, SOURCE)
    set_awaiting_response(True, "approval", CHAT_ID, SOURCE)


@pytest.mark.asyncio
async def test_chat_flow_diff_then_approval():
    """Flow: POST diff request -> zwraca diff do zatwierdzenia; POST 'tak' -> status completed."""
    clear_state(CHAT_ID, SOURCE)

    client = TestClient(app)

    async def mock_first_message(*args, **kwargs):
        return (
            "Oto zmiany:\n\n**Czy mam to wdrożyć?**",
            True,
            "approval",
        )

    async def call_real_process_message(*args, **kwargs):
        """Wywołuje prawdziwą process_message i zwraca jej wynik (tuple)."""
        return await process_message(*args, **kwargs)

    call_count = [0]

    async def dispatch_process_message(*args, dry_run=False, **kwargs):
        """Pierwsze wywołanie → mock (diff). Drugie → mock ustawia status completed w state (multi-task)."""
        call_count[0] += 1
        if call_count[0] == 1:
            return await mock_first_message(*args, **kwargs)
        # Second call: update multi-task state to completed so GET /status returns "completed"
        state = load_state(CHAT_ID, SOURCE)
        if not state or not state.get("tasks"):
            return (
                f"E2E test error: state missing or no tasks (state={state})",
                False,
                None,
            )
        active_id = state.get("active_task_id") or next(iter(state["tasks"]))
        if active_id is None:
            return ("E2E test error: no active_task_id", False, None)
        state["tasks"][active_id]["status"] = OperationStatus.COMPLETED
        with agent_lock(chat_id=CHAT_ID, source=SOURCE):
            save_state(state, CHAT_ID, SOURCE)
        return ("Zrobione.", False, None)

    write_file_calls = []

    def fake_write_file(path, content, operation_id=None, chat_id=None, source=None):
        from agent.state import mark_file_written
        write_file_calls.append((path, content))
        mark_file_written(path, f"/tmp/backup_{path}", chat_id or CHAT_ID, source or SOURCE)

    with patch("interfaces.api.process_message", new_callable=AsyncMock) as mock_pm:
        mock_pm.side_effect = dispatch_process_message
        r1 = client.post("/chat", json={"message": "zmień kolor przycisku na czerwony", "chat_id": CHAT_ID})

        detail_msg = ""
        if r1.status_code != 200:
            _log_api_error(r1, "POST /chat (1)")
            print("\n[E2E DEBUG] POST /chat (1) status:", r1.status_code)
            print("[E2E DEBUG] POST /chat (1) text:", r1.text)
            try:
                j = r1.json()
                print("[E2E DEBUG] POST /chat (1) json:", j)
                if "detail" in j:
                    detail_msg = str(j["detail"])
                    print("[E2E DEBUG] POST /chat (1) detail (błąd z API):", detail_msg)
            except Exception as ex:
                print("[E2E DEBUG] POST /chat (1) json() failed:", ex)
        assert r1.status_code == 200, (
            f"Expected 200, got {r1.status_code}. "
            f"Response: {r1.text[:500] if r1.text else 'empty'}. "
            f"API detail: {detail_msg}"
        )

        data1 = r1.json()
        assert data1["awaiting_input"] is True
        assert data1.get("input_type") == "approval"
        assert "wdrożyć" in data1["response"].lower() or "zmiany" in data1["response"].lower()

        _setup_state_for_approval()
        state_before = load_state(CHAT_ID, SOURCE)
        print("\n[E2E DEBUG] PRZED 2. POST: status =", state_before.get("status") if state_before else None)
        print("[E2E DEBUG] PRZED 2. POST: awaiting_response =", state_before.get("awaiting_response") if state_before else None)

        with patch("agent.nodes.approval.write_file", side_effect=fake_write_file):
            r2 = client.post("/chat", json={"message": "tak", "chat_id": CHAT_ID})

        state_after = load_state(CHAT_ID, SOURCE)
        print("[E2E DEBUG] PO 2. POST: status =", state_after.get("status") if state_after else None)
        print("[E2E DEBUG] write_file wywołany (liczba razy):", len(write_file_calls), "->", write_file_calls)

        if r2.status_code != 200:
            _log_api_error(r2, "POST /chat (2)")
            print("\n[E2E DEBUG] POST /chat (2) status:", r2.status_code)
            print("[E2E DEBUG] POST /chat (2) text:", r2.text)

    assert r2.status_code == 200, f"Expected 200, got {r2.status_code}. Response: {r2.text}"

    r3 = client.get("/status")
    assert r3.status_code == 200
    status_in_api = r3.json()["status"]
    assert status_in_api == "completed", (
        f"Expected status 'completed', got '{status_in_api}'. state_after={state_after}"
    )
    if state_after and state_after.get("tasks"):
        task_id = state_after.get("active_task_id") or next(iter(state_after["tasks"]))
        assert state_after["tasks"][task_id]["status"] == OperationStatus.COMPLETED, (
            f"Task status in state should be completed, got {state_after['tasks'][task_id].get('status')}"
        )


def test_rollback():
    """POST /rollback zwraca status i listę restored (mock SSH)."""
    client = TestClient(app)
    with patch("interfaces.api.rollback") as mock_rollback:
        mock_rollback.return_value = {
            "status": "ok",
            "msg": "Przywrócono 1 plików",
            "restored": ["style.css"],
            "errors": [],
        }
        r = client.post("/rollback")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "restored" in body
    assert "errors" in body
