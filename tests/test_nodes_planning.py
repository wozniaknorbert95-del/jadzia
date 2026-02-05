"""
Tests for agent/nodes/planning (parse_plan, handle_new_task).

Run: pytest tests/test_nodes_planning.py -v
"""

import pytest
from unittest.mock import patch, AsyncMock

from agent.nodes.planning import parse_plan, handle_new_task


def test_parse_plan_valid():
    """Wejście z prawidłowym JSON -> dict z files_to_modify, files_to_read."""
    raw = 'x\n{"files_to_modify": ["a.php"], "files_to_read": ["b.css"], "steps": ["Step 1"]}\ny'
    out = parse_plan(raw)
    assert out["files_to_modify"] == ["a.php"]
    assert out["files_to_read"] == ["b.css"]
    assert out["steps"] == ["Step 1"]


def test_parse_plan_invalid():
    """Wejście bez/niepoprawny JSON -> fallback dict z understood_intent, pustymi listami."""
    out = parse_plan("no json here")
    assert "understood_intent" in out
    assert out.get("files_to_read") == []
    assert out.get("files_to_modify") == []
    assert "steps" in out
    assert "recommendations" in out
    assert out.get("recommendations") == []
    assert "risks" in out

    out2 = parse_plan("{ invalid }")
    assert "understood_intent" in out2
    assert out2.get("files_to_modify") == []


@pytest.mark.asyncio
async def test_handle_new_task_simple():
    """handle_new_task: mock call_claude i generate_changes, zwraca wynik z generate_changes."""
    plan_json = '{"files_to_modify": ["x.php"], "files_to_read": [], "questions": [], "steps": []}'
    async def mock_call_claude(*args, **kwargs):
        return plan_json

    async def mock_generate_changes(*args, **kwargs):
        return ("Done", False, None, None)

    with patch("agent.nodes.planning.create_operation") as mock_create:
        with patch("agent.nodes.planning.update_operation_status"):
            with patch("agent.nodes.planning.log_event"):
                with patch("agent.nodes.planning.classify_task_type"):
                    with patch("agent.nodes.planning.get_file_map"):
                        with patch("agent.nodes.planning.get_context_for_task") as mock_ctx:
                            mock_ctx.return_value = {"planner_context": "ctx", "system_prompt": "sys"}
                            with patch("agent.nodes.planning.generate_changes", side_effect=mock_generate_changes):
                                text, awaiting, input_type, _ = await handle_new_task(
                                    "zmien kolor przycisku",
                                    "chat1",
                                    "http",
                                    mock_call_claude,
                                )
    mock_create.assert_called_once()
    assert text == "Done"
    assert awaiting is False
    assert input_type is None
