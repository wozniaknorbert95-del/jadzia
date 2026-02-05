"""
CI-oriented E2E tests for Worker Task API: Scenarios 2, 3, 4 in test_mode.

- Scenario 2: Happy path (test_mode, no rollback) -> status completed.
- Scenario 3: Forced auto-rollback with [SCENARIO3_FORCE_ROLLBACK] -> log + completion.
- Scenario 4: test_mode + dry_run -> status completed, dry_run true.

Run: pytest tests/test_worker_scenarios_ci.py -v
"""

import json
import uuid
from unittest.mock import patch, AsyncMock

import pytest
from fastapi.testclient import TestClient

from agent.state import clear_state
from agent.log import get_recent_logs
from interfaces.api import app

SOURCE = "http"

# Minimal plan JSON (parse_plan expects this shape)
PLAN_JSON = {
    "understood_intent": "Zmień kolor przycisku",
    "files_to_modify": ["style.css"],
    "files_to_read": [],
    "steps": ["Edytuj style.css"],
    "recommendations": [],
    "risks": [],
}


def _plan_response():
    return json.dumps(PLAN_JSON, ensure_ascii=False)


def _coder_response():
    return "button { color: red; }"


def _intent_new_task_response():
    """Intent classifier response so route_user_input reaches handle_new_task and task is persisted."""
    return json.dumps({"intent": "NEW_TASK", "confidence": 0.9, "reasoning": "test"})


def _intent_approval_response():
    """Intent classifier response for POST input 'tak' so handle_approval is called."""
    return json.dumps({"intent": "APPROVAL", "confidence": 0.9, "reasoning": "test"})


def run_worker_task_until_terminal(
    client: TestClient,
    chat_id: str,
    instruction: str,
    test_mode: bool = True,
    dry_run: bool = False,
    max_steps: int = 15,
) -> tuple[dict, str]:
    """
    POST /worker/task, then loop GET /worker/task/{id} and POST /worker/task/{id}/input
    until status is completed or error. Returns (final_response_body, task_id).
    """
    params = {}
    if dry_run:
        params["dry_run"] = "true"
    r = client.post(
        "/worker/task",
        json={
            "instruction": instruction,
            "chat_id": chat_id,
            "test_mode": test_mode,
        },
        params=params,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    task_id = data["task_id"]
    assert task_id

    for _ in range(max_steps):
        r2 = client.get(f"/worker/task/{task_id}")
        assert r2.status_code == 200, r2.text
        body = r2.json()
        if body.get("status") in ("completed", "error"):
            return body, task_id
        if body.get("awaiting_input"):
            r3 = client.post(
                f"/worker/task/{task_id}/input",
                json={"approval": True},
            )
            assert r3.status_code == 200, r3.text

    return body, task_id


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def isolate_logs(tmp_path, monkeypatch):
    log_file = tmp_path / "agent.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("agent.log.LOG_FILE", log_file)
    yield log_file


@pytest.mark.asyncio
async def test_scenario2_happy_path_test_mode(client, isolate_logs):
    """Scenario 2: test_mode=true, no rollback marker -> status completed."""
    chat_id = f"ci_s2_{uuid.uuid4().hex[:8]}"
    clear_state(chat_id, SOURCE)

    with patch("agent.agent.call_claude_with_retry", new_callable=AsyncMock) as mock_claude:
        mock_claude.side_effect = [
            _intent_new_task_response(),
            _plan_response(),
            _coder_response(),
            _intent_approval_response(),
            _intent_approval_response(),
            _intent_approval_response(),
            _intent_approval_response(),
        ]
        with patch("agent.nodes.planning.list_files", return_value=["style.css"]):
            with patch("agent.nodes.generate.get_path_type", return_value="file"):
                with patch("agent.nodes.generate.read_file", return_value="button { color: black; }"):
                    with patch("agent.nodes.generate.list_directory", return_value=(True, [], None)):
                        with patch("agent.nodes.approval.write_file"):
                            with patch(
                                "agent.tools.rest.health_check_wordpress",
                                new_callable=AsyncMock,
                                return_value={
                                    "healthy": True,
                                    "status_code": 200,
                                    "response_time": 0.1,
                                    "error": None,
                                },
                            ):
                                with patch(
                                    "agent.nodes.quality.validate_changes",
                                    new_callable=AsyncMock,
                                    return_value={"valid": True, "errors": {}, "warnings": {}},
                                ):
                                    with patch("agent.nodes.approval.asyncio.sleep", new_callable=AsyncMock):
                                        with patch(
                                            "agent.tools.deploy",
                                            return_value={"status": "ok", "msg": "Deploy OK"},
                                        ):
                                            final, task_id = run_worker_task_until_terminal(
                                                client, chat_id, "Zmień kolor przycisku na czerwony", test_mode=True
                                            )

    assert final["status"] == "completed", final
    assert final.get("test_mode") is True
    logs = get_recent_logs(limit=50)
    assert any(
        "test_auto_approve" in (e.get("message") or "") or e.get("event_type") == "user_approved"
        for e in logs
    )


@pytest.mark.asyncio
async def test_scenario3_forced_auto_rollback(client, isolate_logs):
    """Scenario 3: test_mode + [SCENARIO3_FORCE_ROLLBACK] -> auto-rollback, log marker."""
    from agent.nodes.approval import SCENARIO3_FORCE_ROLLBACK_TOKEN

    chat_id = f"ci_s3_{uuid.uuid4().hex[:8]}"
    clear_state(chat_id, SOURCE)
    instruction = f"Zmień przycisk {SCENARIO3_FORCE_ROLLBACK_TOKEN}"

    with patch("agent.agent.call_claude_with_retry", new_callable=AsyncMock) as mock_claude:
        mock_claude.side_effect = [
            _intent_new_task_response(),
            _plan_response(),
            _coder_response(),
            _intent_approval_response(),
            _intent_approval_response(),
            _intent_approval_response(),
        ]
        with patch("agent.nodes.planning.list_files", return_value=["style.css"]):
            with patch("agent.nodes.generate.get_path_type", return_value="file"):
                with patch("agent.nodes.generate.read_file", return_value="button { color: black; }"):
                    with patch("agent.nodes.generate.list_directory", return_value=(True, [], None)):
                        with patch("agent.nodes.approval.write_file"):
                            with patch(
                                "agent.tools.rest.health_check_wordpress",
                                new_callable=AsyncMock,
                            ) as mock_health:
                                with patch(
                                    "agent.nodes.quality.validate_changes",
                                    new_callable=AsyncMock,
                                    return_value={"valid": True, "errors": {}, "warnings": {}},
                                ):
                                    with patch("agent.nodes.approval.asyncio.sleep", new_callable=AsyncMock):
                                        with patch(
                                            "agent.nodes.commands.handle_rollback",
                                            new_callable=AsyncMock,
                                            return_value=("Rollback done.", False, None),
                                        ):
                                            final, task_id = run_worker_task_until_terminal(
                                                client, chat_id, instruction, test_mode=True
                                            )

    mock_health.assert_not_awaited()
    assert final["status"] == "completed"
    assert final.get("test_mode") is True
    logs = get_recent_logs(limit=50)
    log_text = json.dumps([e for e in logs], ensure_ascii=False)
    assert "[SCENARIO3] AUTO-ROLLBACK VERIFICATION" in log_text


@pytest.mark.asyncio
async def test_scenario4_test_mode_dry_run(client, isolate_logs):
    """Scenario 4: test_mode + dry_run -> status completed, dry_run true, no real writes."""
    chat_id = f"ci_s4_{uuid.uuid4().hex[:8]}"
    clear_state(chat_id, SOURCE)

    with patch("agent.agent.call_claude_with_retry", new_callable=AsyncMock) as mock_claude:
        mock_claude.side_effect = [
            _intent_new_task_response(),
            _plan_response(),
            _coder_response(),
            _intent_approval_response(),
            _intent_approval_response(),
        ]
        with patch("agent.nodes.planning.list_files", return_value=["style.css"]):
            with patch("agent.nodes.generate.get_path_type", return_value="file"):
                with patch("agent.nodes.generate.read_file", return_value="button { color: black; }"):
                    with patch("agent.nodes.generate.list_directory", return_value=(True, [], None)):
                        with patch(
                            "agent.nodes.quality.validate_changes",
                            new_callable=AsyncMock,
                            return_value={"valid": True, "errors": {}, "warnings": {}},
                        ):
                            final, task_id = run_worker_task_until_terminal(
                                client,
                                chat_id,
                                "Podgląd zmiany koloru",
                                test_mode=True,
                                dry_run=True,
                            )

    assert final["status"] == "completed", final
    assert final.get("dry_run") is True
    assert final.get("test_mode") is True
