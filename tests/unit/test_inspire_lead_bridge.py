"""REV-DEMAND-03: INSPIRE chat → durable lead on email+consent."""

from __future__ import annotations

import os
import tempfile

import pytest

from agent.inspire.chat_advisor import (
    _extract_inspire_email,
    _has_inspire_consent,
    _maybe_persist_inspire_lead,
    process_chat_turn,
    set_llm_callable,
    SESSIONS,
)


def _isolate_db(monkeypatch):
    import agent.db as db_mod

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr(db_mod, "DB_PATH", path)
    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
    return path


def _cleanup_db(path: str) -> None:
    import agent.db as db_mod

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture(autouse=True)
def _clear_inspire(monkeypatch, tmp_path):
    from agent.inspire import chat_session_store

    monkeypatch.setenv("DA_CHAT_SESSION_DB", str(tmp_path / "chat-sessions.sqlite3"))
    monkeypatch.setenv("DA_CHAT_ENGINE", "legacy")
    chat_session_store.clear_all()
    SESSIONS.clear()
    set_llm_callable(None)
    yield
    SESSIONS.clear()
    set_llm_callable(None)
    chat_session_store.clear_all()


def test_extract_email_and_consent_helpers():
    assert _extract_inspire_email("mail jan@bouw.nl please", None, None) == "jan@bouw.nl"
    assert (
        _extract_inspire_email(
            "hi",
            {"email": "x@y.nl"},
            None,
        )
        == "x@y.nl"
    )
    assert _has_inspire_consent("akkoord toestemming", None, None) is True
    assert _has_inspire_consent("hoi", {"consent_lead_storage": True}, None) is True
    assert _has_inspire_consent("hoi", None, None) is False


def test_persist_requires_email_and_consent(monkeypatch):
    path = _isolate_db(monkeypatch)
    assert (
        _maybe_persist_inspire_lead(
            session_id="s1",
            message="jan@bouw.nl",
            field_updates=None,
            brief_partial=None,
        )
        is None
    )
    assert (
        _maybe_persist_inspire_lead(
            session_id="s1",
            message="akkoord",
            field_updates=None,
            brief_partial=None,
        )
        is None
    )
    lead_id = _maybe_persist_inspire_lead(
        session_id="s1",
        message="Bel me jan.inspire@test.nl akkoord toestemming",
        field_updates=None,
        brief_partial={"bedrijfsnaam": "Bouw BV"},
    )
    assert lead_id
    from agent.db import db_get_lead_by_email

    lead = db_get_lead_by_email("jan.inspire@test.nl")
    assert lead is not None
    assert lead["source"] == "inspire"
    assert lead["name"] == "Bouw BV"
    _cleanup_db(path)


def test_process_chat_turn_returns_lead_id(monkeypatch):
    path = _isolate_db(monkeypatch)

    def llm(_messages):
        return {
            "reply_nl": "Bedankt, we bewaren je gegevens.",
            "phase": 2,
            "brief_updates": {},
            "brief_confirmed": False,
        }

    set_llm_callable(llm)
    result = process_chat_turn(
        session_id="inspire-lead-1",
        message="Mijn mail is lead03@flex.test.nl en akkoord toestemming",
    )
    assert result.lead_id
    from agent.db import db_get_lead_by_email

    assert db_get_lead_by_email("lead03@flex.test.nl") is not None
    _cleanup_db(path)


def test_persist_db_failure_soft(monkeypatch):
    path = _isolate_db(monkeypatch)
    from unittest.mock import patch

    with patch("agent.db.db_create_lead", side_effect=RuntimeError("db down")):
        assert (
            _maybe_persist_inspire_lead(
                session_id="s-fail",
                message="x@y.nl akkoord",
                field_updates=None,
                brief_partial=None,
            )
            is None
        )
    _cleanup_db(path)


def test_process_chat_turn_no_lead_without_consent(monkeypatch):
    path = _isolate_db(monkeypatch)

    def llm(_messages):
        return {
            "reply_nl": "Ok",
            "phase": 1,
            "brief_updates": {},
            "brief_confirmed": False,
        }

    set_llm_callable(llm)
    result = process_chat_turn(
        session_id="inspire-nolead",
        message="Mail me op alone@flex.test.nl",
    )
    assert result.lead_id is None
    from agent.db import db_get_lead_by_email

    assert db_get_lead_by_email("alone@flex.test.nl") is None
    _cleanup_db(path)
