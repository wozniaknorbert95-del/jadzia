"""
Tests for SSH orchestrator: ensure guardrails and state are called.
"""

import pytest
from unittest.mock import patch, MagicMock

from agent.guardrails import OperationType
from agent.tools import ssh_orchestrator


def test_read_file_calls_validate_operation_and_read_file_ssh():
    """read_file calls validate_operation(READ, [path]) and read_file_ssh with full path."""
    with patch("agent.tools.ssh_orchestrator.validate_operation") as mock_validate:
        with patch("agent.tools.ssh_orchestrator.get_path_type_ssh") as mock_type:
            with patch("agent.tools.ssh_orchestrator.read_file_ssh") as mock_read:
                with patch("agent.tools.ssh_orchestrator.log_event") as mock_log:
                    mock_validate.return_value = (True, "", False)
                    mock_type.return_value = "file"
                    mock_read.return_value = "file content"
                    result = ssh_orchestrator.read_file("style.css")
    mock_validate.assert_called_once()
    call_args = mock_validate.call_args[0]
    assert call_args[0] == OperationType.READ
    assert call_args[1] == ["style.css"]
    mock_read.assert_called_once()
    assert "style.css" in str(mock_read.call_args[0][-1]) or "style" in str(mock_read.call_args)
    mock_log.assert_called()
    assert result == "file content"


def test_write_file_calls_validate_validate_content_mark_file_written():
    """write_file calls validate_operation, validate_content, write_file_ssh, mark_file_written, log_event."""
    with patch("agent.tools.ssh_orchestrator.validate_operation") as mock_validate:
        with patch("agent.tools.ssh_orchestrator.validate_content") as mock_validate_content:
            with patch("agent.tools.ssh_orchestrator.read_file_ssh_bytes") as mock_read:
                with patch("agent.tools.ssh_orchestrator.write_file_ssh") as mock_write:
                    with patch("agent.tools.ssh_orchestrator.write_file_ssh_bytes") as mock_write_bytes:
                        with patch("agent.tools.ssh_orchestrator.mark_file_written") as mock_mark:
                            with patch("agent.tools.ssh_orchestrator.log_event"):
                                mock_validate.return_value = (True, "", False)
                                mock_validate_content.return_value = (True, "")
                                mock_read.side_effect = FileNotFoundError()
                                ssh_orchestrator.write_file(
                                    "style.css", "body {}", operation_id="op1", chat_id="c1", source="http"
                                )
    mock_validate.assert_called_once_with(OperationType.WRITE, ["style.css"])
    mock_validate_content.assert_called_once_with("body {}", "style.css")
    mock_mark.assert_called_once()
    call = mock_mark.call_args[0]
    assert call[0] == "style.css"
    assert call[2] == "c1"
    assert call[3] == "http"
