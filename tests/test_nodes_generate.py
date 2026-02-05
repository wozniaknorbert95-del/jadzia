"""
Tests for agent/nodes/generate (truncate, smart_truncate, generate_changes).

Run: pytest tests/test_nodes_generate.py -v
"""

import pytest
from unittest.mock import patch, AsyncMock

from agent.nodes.generate import (
    truncate_file_content,
    smart_truncate_for_task,
    generate_changes,
)


def test_truncate_file_content():
    """Krótki tekst nie skracany; długi zwraca tuple z POMINIĘTO."""
    short = "abc"
    out, changed = truncate_file_content(short, max_size=10000)
    assert out == short
    assert changed is False

    long_text = "x" * 20000
    out, changed = truncate_file_content(long_text, max_size=10000)
    assert changed is True
    assert "[... POMINIĘTO" in out
    assert len(out) <= 10200


def test_smart_truncate_css():
    """Content CSS z .button; task o kolorze .button -> znajduje selektor."""
    content = "body { margin: 0; }\n.button { color: red; }\n.footer { }"
    task = "zmień kolor .button"
    result = smart_truncate_for_task(content, task, "style.css")
    assert ".button" in result
    assert "color: red" in result or "red" in result


@pytest.mark.asyncio
async def test_generate_changes():
    """generate_changes: mock read_file, call_claude, get_path_type, validate_changes; zwraca Potwierdzasz i approval."""
    plan = {
        "files_to_modify": ["a.php"],
        "files_to_read": [],
        "understood_intent": "test",
        "steps": [],
    }
    validation_passed = {"valid": True, "errors": {}, "warnings": {}, "details": {}}
    with patch("agent.nodes.generate.load_state", return_value={"id": "op-1"}):
        with patch("agent.nodes.generate.get_path_type", return_value="file"):
            with patch("agent.nodes.generate.read_file", return_value="<?php echo 1;"):
                with patch("agent.nodes.generate.update_operation_status"):
                    with patch("agent.nodes.generate.store_diffs"):
                        with patch("agent.nodes.generate.store_new_contents", return_value=True):
                            with patch("agent.nodes.generate.set_awaiting_response"):
                                with patch("agent.nodes.generate.log_event"):
                                    with patch("agent.nodes.generate.get_minimal_context", return_value=""):
                                        with patch("agent.nodes.generate.get_coder_prompt", return_value="prompt"):
                                            with patch(
                                                "agent.nodes.quality.validate_changes",
                                                new_callable=AsyncMock,
                                                return_value=validation_passed,
                                            ):
                                                with patch("agent.nodes.generate.get_active_task_id", return_value=None):
                                                    async def mock_call_claude(*args, **kwargs):
                                                        return "<?php echo 2;"
                                                    text, awaiting, input_type, _ = await generate_changes(
                                                        "zmien plik",
                                                        "chat1",
                                                        "http",
                                                        plan,
                                                        None,
                                                        mock_call_claude,
                                                    )
    assert "Potwierdzasz" in text or "PLAN" in text
    assert awaiting is True
    assert input_type == "approval"
