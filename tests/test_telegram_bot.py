"""
Unit tests for Telegram bot logic (command parsing, callback parsing, inline keyboard).
No Telegram API or real HTTP calls.
"""

import pytest
from unittest.mock import patch, AsyncMock

from agent.telegram_validator import normalize_telegram_update
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


def test_parse_command_pomoc_with_bot_username():
    """Telegram sends /pomoc@BotName in groups; must still recognize as pomoc."""
    cmd, payload = parse_telegram_command("/pomoc@SomeBot")
    assert cmd == "pomoc"
    assert payload == ""


def test_parse_command_status_with_bot_username():
    """Telegram sends /status@BotName in groups; must still recognize as status."""
    cmd, payload = parse_telegram_command("/status@JadziaBot")
    assert cmd == "status"
    assert payload == ""


def test_parse_command_zadanie_with_bot_username_and_payload():
    """Telegram sends /zadanie@BotName instruction in groups; payload must be the rest."""
    cmd, payload = parse_telegram_command("/zadanie@Bot nowe zadanie")
    assert cmd == "zadanie"
    assert payload == "nowe zadanie"


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


# --- normalize_telegram_update (native Telegram Update -> TelegramWebhookRequest) ---


def test_normalize_telegram_update_message():
    """Minimal Update with message yields TelegramWebhookRequest with user_id, chat_id, message_id, message."""
    body = {
        "update_id": 123,
        "message": {
            "message_id": 1,
            "from": {"id": 456, "first_name": "Test"},
            "chat": {"id": 456, "type": "private"},
            "text": "/pomoc",
        },
    }
    out = normalize_telegram_update(body)
    assert out is not None
    assert out.user_id == "456"
    assert out.chat_id == "456"
    assert out.message_id == 1
    assert out.message == "/pomoc"
    assert out.callback_data is None


def test_normalize_telegram_update_callback_query():
    """Update with callback_query yields request with callback_data set."""
    body = {
        "update_id": 124,
        "callback_query": {
            "id": "cb1",
            "from": {"id": 789, "first_name": "User"},
            "message": {"message_id": 2, "chat": {"id": 789, "type": "private"}},
            "data": "task-xyz:approve:yes",
        },
    }
    out = normalize_telegram_update(body)
    assert out is not None
    assert out.user_id == "789"
    assert out.chat_id == "789"
    assert out.message_id == 2
    assert out.message == ""
    assert out.callback_data == "task-xyz:approve:yes"


def test_normalize_telegram_update_callback_query_no_message():
    """CallbackQuery without message uses from.id for chat_id and message_id 0."""
    body = {
        "update_id": 125,
        "callback_query": {
            "id": "cb2",
            "from": {"id": 999, "first_name": "U"},
            "data": "tid:approve:no",
        },
    }
    out = normalize_telegram_update(body)
    assert out is not None
    assert out.user_id == "999"
    assert out.chat_id == "999"
    assert out.message_id == 0
    assert out.callback_data == "tid:approve:no"


def test_normalize_telegram_update_empty():
    """Update with only update_id (no message, no callback_query) returns None."""
    assert normalize_telegram_update({"update_id": 1}) is None


def test_normalize_telegram_update_no_update_id():
    """Body without update_id returns None (n8n format is not normalized here)."""
    assert normalize_telegram_update({"user_id": "1", "chat_id": "1", "message": "hi", "message_id": 1}) is None


def test_normalize_telegram_update_callback_empty_data_returns_none():
    """CallbackQuery with empty or missing data returns None."""
    body = {
        "update_id": 126,
        "callback_query": {
            "id": "cb3",
            "from": {"id": 1, "first_name": "X"},
            "data": "",
        },
    }
    assert normalize_telegram_update(body) is None


# --- _send_telegram_replies (sendMessage integration) ---


@pytest.mark.asyncio
async def test_send_telegram_replies_calls_send_message_when_token_set():
    """When TELEGRAM_BOT_TOKEN is set and response has messages, sendMessage is called."""
    from interfaces.telegram_api import _send_telegram_replies, TelegramWebhookResponse, TELEGRAM_BOT_TOKEN
    from unittest.mock import AsyncMock, patch

    response = TelegramWebhookResponse(
        success=True,
        messages=[{"text": "Hello", "parse_mode": "MarkdownV2"}],
    )
    with patch("interfaces.telegram_api.TELEGRAM_BOT_TOKEN", "fake-token"):
        with patch("interfaces.telegram_api.httpx.AsyncClient") as mock_client_cls:
            mock_post = AsyncMock(return_value=type("R", (), {"raise_for_status": lambda: None})())
            mock_client_cls.return_value.__aenter__.return_value.post = mock_post
            await _send_telegram_replies("123", response, None)
    if TELEGRAM_BOT_TOKEN or "fake-token":
        assert mock_post.call_count >= 1
        send_message_calls = [c for c in mock_post.call_args_list if "sendMessage" in str(c[0][0])]
        assert len(send_message_calls) >= 1
        assert send_message_calls[0][1]["json"]["chat_id"] == "123"
        assert send_message_calls[0][1]["json"]["text"] == "Hello"


@pytest.mark.asyncio
async def test_send_telegram_replies_no_call_when_no_messages():
    """When response has no messages, no HTTP call to Telegram."""
    from interfaces.telegram_api import _send_telegram_replies, TelegramWebhookResponse
    from unittest.mock import AsyncMock, patch

    response = TelegramWebhookResponse(success=True, messages=[])
    with patch("interfaces.telegram_api.TELEGRAM_BOT_TOKEN", "fake-token"):
        with patch("interfaces.telegram_api.httpx.AsyncClient") as mock_client_cls:
            mock_post = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value.post = mock_post
            await _send_telegram_replies("123", response, None)
    mock_post.assert_not_called()
