"""Escalation and health monitor tests (N6, N16)."""

import json
import os
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

JWT_SECRET_VALUE = "test-escalation"


@contextmanager
def jwt_env():
    with patch.dict(os.environ, {"JWT_SECRET": JWT_SECRET_VALUE}, clear=False):
        yield


@pytest.fixture
def temp_db(monkeypatch):
    import tempfile

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr("agent.db.DB_PATH", path)
    import agent.db as db_mod

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
    yield path


def test_health_monitor_down_alert(temp_db, monkeypatch):
    from agent.commander.health_monitor import check_commander_health
    from agent.db import db_commander_set_setting

    old = datetime.now(timezone.utc) - timedelta(minutes=6)
    db_commander_set_setting("health:down_since", json.dumps(old.isoformat()))
    monkeypatch.setattr("agent.commander.health_monitor._http_ok", lambda url: False)
    msg = check_commander_health()
    assert msg is not None
    assert "unreachable" in msg.lower()


def test_escalation_dedup(temp_db, monkeypatch):
    from agent.commander.escalation import check_sla_escalations
    from agent.db import db_commander_create_ticket, db_commander_set_setting

    db_commander_set_setting("delegat_email", json.dumps("d@test.nl"))
    db_commander_create_ticket("Old ticket", "desc", "pytest")
    sent = []

    monkeypatch.setattr(
        "agent.commander.escalation._send_telegram",
        lambda msg, chat_id=None: sent.append(msg),
    )
    monkeypatch.setattr("agent.commander.escalation._silent_agents", lambda: [])
    monkeypatch.setattr(
        "agent.commander.escalation.build_queue",
        lambda: [
            {
                "id": "ticket-1",
                "severity": "CRITICAL",
                "title": "T",
                "age_hours": 48,
                "sla_status": "red",
            }
        ],
    )
    n1 = check_sla_escalations()
    n2 = check_sla_escalations()
    assert n1 >= 1
    assert n2 == 0


def test_send_delegat_email_skipped_without_host(monkeypatch):
    from agent.commander.escalation import _send_delegat_email

    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_PASSWORD", raising=False)
    assert _send_delegat_email("subj", "body", "d@test.nl") is False


def test_send_delegat_email_ok(monkeypatch):
    from agent.commander import escalation as esc

    monkeypatch.setenv("SMTP_HOST", "smtp.test.local")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "sender@test.nl")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")
    monkeypatch.setenv("SMTP_FROM", "sender@test.nl")

    class _FakeSMTP:
        def __init__(self, host, port, timeout=15):
            self.host = host
            self.port = port
            self.timeout = timeout
            self.started_tls = False
            self.logged_in = None
            self.sent = None

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def starttls(self):
            self.started_tls = True

        def login(self, user, password):
            self.logged_in = (user, password)

        def send_message(self, msg):
            self.sent = msg

    fake = {"smtp": None}

    def _factory(*args, **kwargs):
        fake["smtp"] = _FakeSMTP(*args, **kwargs)
        return fake["smtp"]

    monkeypatch.setattr(esc.smtplib, "SMTP", _factory)
    assert esc._send_delegat_email("SLA", "body text", "d@test.nl") is True
    smtp = fake["smtp"]
    assert smtp is not None
    assert smtp.started_tls is True
    assert smtp.logged_in == ("sender@test.nl", "secret")
    assert smtp.sent["To"] == "d@test.nl"
    assert smtp.sent["Subject"] == "SLA"
