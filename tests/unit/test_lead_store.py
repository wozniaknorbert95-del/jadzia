"""Tests for leads table persistence (INT-004)."""

import os
import tempfile

import pytest

from agent.db import db_create_lead, db_get_lead_by_email, db_get_lead_by_id


@pytest.fixture
def temp_db(monkeypatch):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr("agent.db.DB_PATH", path)
    import agent.db as db_mod

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


def _sample_lead(email: str = "player@example.nl") -> dict:
    return {
        "email": email,
        "name": "Test Player",
        "source": "game",
        "consent_status": True,
        "game_score": 150,
        "reward_tier": "bronze",
    }


def test_db_create_lead_inserts_row(temp_db):
    lead_id, status = db_create_lead(_sample_lead())
    assert status == "success"
    assert lead_id == "1"

    row = db_get_lead_by_email("player@example.nl")
    assert row is not None
    assert row["source"] == "game"
    assert row["game_score"] == 150


def test_db_create_lead_duplicate_email(temp_db):
    db_create_lead(_sample_lead())
    lead_id, status = db_create_lead(_sample_lead())
    assert status == "duplicate"
    assert lead_id == "1"


def test_db_create_lead_rejects_no_consent(temp_db):
    data = _sample_lead()
    data["consent_status"] = False
    lead_id, status = db_create_lead(data)
    assert status == "fail"
    assert lead_id is None


def test_db_get_lead_by_id(temp_db):
    lead_id, _ = db_create_lead(_sample_lead("other@example.nl"))
    row = db_get_lead_by_id(int(lead_id))
    assert row is not None
    assert row["lead_id"] == lead_id
