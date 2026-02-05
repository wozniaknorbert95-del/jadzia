"""
Tests for quality assurance validation (agent/nodes/quality.py).

Run: pytest tests/test_quality.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from agent.nodes.quality import syntax_check_css, validate_changes, syntax_check_php


def test_css_valid():
    """Test CSS validation with valid CSS."""
    css = """
    .container {
        color: #333;
        padding: 10px;
    }
    """
    result = syntax_check_css(css)
    assert result["valid"] is True
    assert len(result["errors"]) == 0


def test_css_unbalanced_braces():
    """Test CSS validation catches unbalanced braces."""
    css = """
    .container {
        color: #333;
    """
    result = syntax_check_css(css)
    assert result["valid"] is False
    assert any("Unbalanced braces" in e for e in result["errors"])


def test_css_orphaned_semicolon():
    """Test CSS validation warns about orphaned semicolons."""
    css = """
    .container { color: red; }
    ;
    """
    result = syntax_check_css(css)
    assert len(result["warnings"]) > 0


@pytest.mark.asyncio
async def test_php_validation_valid():
    """Test PHP validation with valid code."""
    php_code = "<?php echo 'hello'; ?>"

    mock_ssh = MagicMock()
    mock_ssh.run_command = AsyncMock(
        return_value={
            "stdout": "No syntax errors detected in -\n",
            "stderr": "",
            "exit_code": 0,
        }
    )

    result = await syntax_check_php(php_code, mock_ssh)

    assert result["valid"] is True
    assert result["error"] is None


@pytest.mark.asyncio
async def test_php_validation_syntax_error():
    """Test PHP validation catches syntax errors."""
    php_code = "<?php echo 'unclosed"

    mock_ssh = MagicMock()
    mock_ssh.run_command = AsyncMock(
        return_value={
            "stdout": "",
            "stderr": "PHP Parse error: syntax error, unexpected end of file in - on line 1\n",
            "exit_code": 255,
        }
    )

    result = await syntax_check_php(php_code, mock_ssh)

    assert result["valid"] is False
    assert result["error"] is not None
    assert result["line"] == 1


@pytest.mark.asyncio
async def test_validate_changes_all_valid():
    """Test validate_changes with all valid files."""
    diffs = {
        "test.css": {"new": ".class { color: red; }"},
        "test.php": {"new": "<?php echo 'test'; ?>"},
    }

    mock_ssh = MagicMock()
    mock_ssh.run_command = AsyncMock(
        return_value={
            "stdout": "No syntax errors detected in -\n",
            "stderr": "",
            "exit_code": 0,
        }
    )

    result = await validate_changes(diffs, mock_ssh)

    assert result["valid"] is True
    assert len(result["errors"]) == 0


@pytest.mark.asyncio
async def test_validate_changes_with_errors():
    """Test validate_changes catches errors (CSS unbalanced + PHP security)."""
    diffs = {
        "test.css": {"new": ".class { color: red; "},
        "test.php": {"new": "<?php eval('bad'); ?>"},
    }

    mock_ssh = MagicMock()
    mock_ssh.run_command = AsyncMock(
        return_value={
            "stdout": "No syntax errors detected in -\n",
            "stderr": "",
            "exit_code": 0,
        }
    )

    result = await validate_changes(diffs, mock_ssh)

    assert result["valid"] is False
    assert "test.css" in result["errors"]
    assert "test.php" in result["errors"]
