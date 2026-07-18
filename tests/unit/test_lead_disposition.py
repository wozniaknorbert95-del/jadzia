"""Commander lead disposition (REV-DEMAND-01c)."""

from __future__ import annotations

import os

import pytest

from agent.commander.queue import build_queue
from agent.db import db_create_lead, db_list_leads, db_update_lead_disposition


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
    try:
        os.unlink(path)
    except OSError:
        pass


def test_hot_lead_hidden_when_closed(temp_db):
    lead_id, status = db_create_lead(
        {
            "email": "hot.demand@test.nl",
            "name": "Hot",
            "source": "web",
            "consent_status": True,
            "game_score": 90,
            "reward_tier": None,
        }
    )
    assert status == "success"
    items = build_queue()
    hot = [i for i in items if i.get("queue_type") == "hot_lead"]
    assert any(i["payload"].get("email") == "hot.demand@test.nl" for i in hot)

    assert db_update_lead_disposition(int(lead_id), "closed") is True
    items2 = build_queue()
    hot2 = [i for i in items2 if i.get("queue_type") == "hot_lead"]
    assert not any(i["payload"].get("email") == "hot.demand@test.nl" for i in hot2)

    leads = db_list_leads(limit=5)
    row = next(l for l in leads if l.get("email") == "hot.demand@test.nl")
    assert row["disposition"] == "closed"
