"""
Tests for agent/nodes/commands (handle_status, handle_help).

Run: pytest tests/test_nodes_commands.py -v
"""

import pytest
from unittest.mock import patch

from agent.nodes.commands import handle_status, handle_help


@pytest.mark.asyncio
async def test_handle_status_no_state():
    """Brak state -> odpowiedź 'Agent jest gotowy', 'Brak aktywnych operacji'."""
    with patch("agent.nodes.commands.load_state", return_value=None):
        text, awaiting, input_type = await handle_status("chat1", "http")
    assert "Agent jest gotowy" in text
    assert "Brak aktywnych operacji" in text
    assert awaiting is False
    assert input_type is None


@pytest.mark.asyncio
async def test_handle_status_with_state():
    """Z state -> odpowiedź zawiera STATUS AGENTA i pola."""
    state = {
        "id": "op-123",
        "status": "diff_ready",
        "user_input": "zmien kolor",
        "files_to_modify": ["a.php", "b.php"],
        "files_written": [],
        "awaiting_response": True,
        "awaiting_type": "approval",
    }
    with patch("agent.nodes.commands.load_state", return_value=state):
        text, awaiting, input_type = await handle_status("chat1", "http")
    assert "STATUS AGENTA" in text
    assert "op-123" in text
    assert "diff_ready" in text
    assert "zmien kolor" in text
    assert "Pliki do zmiany: 2" in text
    assert "Pliki zapisane: 0" in text
    assert "Oczekuje odpowiedzi: True" in text
    assert "approval" in text
    assert awaiting is False
    assert input_type is None


def test_handle_help():
    """handle_help zwraca tuple z tekstem pomocy, False, None."""
    text, awaiting, input_type = handle_help("any", "http")
    assert isinstance(text, str)
    assert "JADZIA" in text or "Pomoc" in text
    assert "Komendy" in text or "/status" in text or "/help" in text
    assert awaiting is False
    assert input_type is None
