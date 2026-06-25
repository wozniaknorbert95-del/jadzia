"""Tests for portal qualification lead persistence."""

import os
import tempfile
from unittest.mock import patch

import pytest

from agent.portal_qualification.lead_store import save_portal_qual_lead


@pytest.fixture
def temp_db(monkeypatch):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr("agent.db.DB_PATH", path)
    # Reset thread-local connection so schema is created on new path
    import agent.db as db_mod

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


def test_save_portal_qual_lead_inserts_row(temp_db):
    ok = save_portal_qual_lead(
        session_id="test-session-abc",
        profile={
            "industry": "bouw",
            "goal": "meer_klanten",
            "vehicle": "bus",
            "budget_tier": "300_700",
        },
        recommended_preset_id="groeier",
    )
    assert ok is True

    from agent.db import get_connection

    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM portal_qual_leads WHERE session_id = ?",
        ("test-session-abc",),
    ).fetchone()
    assert row is not None
    assert row["recommended_preset_id"] == "groeier"
    assert row["industry"] == "bouw"


@patch("agent.portal_qualification.lead_store._maybe_hot_lead_alert")
def test_hot_lead_alert_for_flota(mock_alert, temp_db):
    save_portal_qual_lead(
        session_id="hot-1",
        profile={"budget_tier": "700_plus", "vehicle": "bus"},
        recommended_preset_id="professional-flota",
    )
    mock_alert.assert_called_once()
