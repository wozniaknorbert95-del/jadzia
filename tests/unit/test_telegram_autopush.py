"""TELEGRAM_AUTOPUSH_ENABLED kill-switch."""

import logging

from agent.telegram_autopush import telegram_autopush_enabled


def test_autopush_default_off(monkeypatch):
    monkeypatch.delenv("TELEGRAM_AUTOPUSH_ENABLED", raising=False)
    assert telegram_autopush_enabled() is False


def test_autopush_off_explicit(monkeypatch):
    monkeypatch.setenv("TELEGRAM_AUTOPUSH_ENABLED", "0")
    assert telegram_autopush_enabled() is False
    monkeypatch.setenv("TELEGRAM_AUTOPUSH_ENABLED", "false")
    assert telegram_autopush_enabled() is False


def test_autopush_on(monkeypatch):
    monkeypatch.setenv("TELEGRAM_AUTOPUSH_ENABLED", "1")
    assert telegram_autopush_enabled() is True
    monkeypatch.setenv("TELEGRAM_AUTOPUSH_ENABLED", "true")
    assert telegram_autopush_enabled() is True


def test_alert_sync_skipped_when_autopush_off(monkeypatch, caplog):
    from agent.customer_agent import _send_telegram_alert_sync

    monkeypatch.setenv("TELEGRAM_AUTOPUSH_ENABLED", "0")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
    monkeypatch.setenv("TELEGRAM_ADMIN_CHAT_ID", "1")
    called = []

    class _FakeClient:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, *a, **k):
            called.append(1)
            raise AssertionError("should not send")

    monkeypatch.setattr(
        "agent.customer_agent.httpx.Client",
        lambda *a, **k: _FakeClient(),
    )
    with caplog.at_level(logging.INFO):
        _send_telegram_alert_sync("spam test")
    assert called == []
    assert any("autopush skipped" in r.message for r in caplog.records)


def test_escalation_tg_skipped_when_autopush_off(monkeypatch, caplog):
    from agent.commander.escalation import _send_telegram

    monkeypatch.setenv("TELEGRAM_AUTOPUSH_ENABLED", "0")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
    monkeypatch.setenv("TELEGRAM_ADMIN_CHAT_ID", "1")
    with caplog.at_level(logging.INFO):
        _send_telegram("SLA spam")
    assert any("autopush skipped" in r.message for r in caplog.records)
