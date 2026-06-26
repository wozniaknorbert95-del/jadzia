"""Tests for lead_node (INT-004)."""

import os
import tempfile

import pytest

from agent.nodes.lead_node import process_lead_sync
from core.models import LeadCreateRequest


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


def _payload() -> LeadCreateRequest:
    return LeadCreateRequest(
        email="gamer@zzp.nl",
        name="Gamer",
        source="game",
        consent_status=True,
        game_score=200,
        reward_tier="silver",
    )


def test_process_lead_sync_success(temp_db):
    result = process_lead_sync(_payload())
    assert result.sync_status == "success"
    assert result.lead_id == "1"


def test_process_lead_sync_duplicate(temp_db):
    process_lead_sync(_payload())
    result = process_lead_sync(_payload())
    assert result.sync_status == "duplicate"
    assert result.lead_id == "1"
