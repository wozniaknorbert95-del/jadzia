"""
Unit tests for Telegram bot logic (command parsing, callback parsing, inline keyboard).
No Telegram API or real HTTP calls.
"""

import pytest
from unittest.mock import patch, AsyncMock

from interfaces.telegram_api import (
    parse_telegram_command,
    parse_callback_approval,
    build_inline_keyboard_approval,
)


# --- parse_telegram_command ---


def test_parse_command_callback_takes_precedence():
    cmd, payload = parse_telegram_command("/status", callback_data="abc-123:approve:yes")
    assert cmd == "callback"
    assert payload == "abc-123:approve:yes"


def test_parse_command_zadanie_with_instruction():
    cmd, payload = parse_telegram_command("/zadanie zmień kolor przycisku")
    assert cmd == "zadanie"
    assert payload == "zmień kolor przycisku"


def test_parse_command_zadanie_empty_rest():
    cmd, payload = parse_telegram_command("/zadanie")
    assert cmd == "zadanie"
    assert payload == ""


def test_parse_command_status():
    for msg in ("/status", "status"):
        cmd, payload = parse_telegram_command(msg)
        assert cmd == "status"
        assert payload == ""


def test_parse_command_cofnij():
    for msg in ("/cofnij", "cofnij"):
        cmd, payload = parse_telegram_command(msg)
        assert cmd == "cofnij"
        assert payload == ""


def test_parse_command_pomoc():
    for msg in ("/pomoc", "pomoc", "/help", "help"):
        cmd, payload = parse_telegram_command(msg)
        assert cmd == "pomoc"
        assert payload == ""


def test_parse_command_approval_tak():
    for msg in ("tak", "Tak", "t", "T", "yes", "YES"):
        cmd, payload = parse_telegram_command(msg)
        assert cmd == "approval"
        assert payload == "true"


def test_parse_command_approval_nie():
    for msg in ("nie", "Nie", "n", "N", "no", "NO"):
        cmd, payload = parse_telegram_command(msg)
        assert cmd == "approval"
        assert payload == "false"


def test_parse_command_plain_message():
    cmd, payload = parse_telegram_command("zmień kolor tła na niebieski")
    assert cmd == "message"
    assert payload == "zmień kolor tła na niebieski"


def test_parse_command_empty_message_no_callback():
    cmd, payload = parse_telegram_command("")
    assert cmd == "message"
    assert payload == ""


# --- parse_callback_approval ---


def test_parse_callback_approval_yes():
    out = parse_callback_approval("task-uuid-123:approve:yes")
    assert out == ("task-uuid-123", True)


def test_parse_callback_approval_no():
    out = parse_callback_approval("task-uuid-456:approve:no")
    assert out == ("task-uuid-456", False)


def test_parse_callback_approval_invalid_format():
    assert parse_callback_approval("") is None
    assert parse_callback_approval("nocolon") is None
    assert parse_callback_approval("one:two") is None
    assert parse_callback_approval("id:other:value") is None  # middle not "approve"


def test_parse_callback_approval_unknown_choice():
    assert parse_callback_approval("id:approve:maybe") is None


# --- build_inline_keyboard_approval ---


def test_build_inline_keyboard_approval_structure():
    out = build_inline_keyboard_approval("tid-789")
    assert "inline_keyboard" in out
    row = out["inline_keyboard"][0]
    assert len(row) == 2
    texts = {b["text"]: b["callback_data"] for b in row}
    assert texts["Tak"] == "tid-789:approve:yes"
    assert texts["Nie"] == "tid-789:approve:no"
