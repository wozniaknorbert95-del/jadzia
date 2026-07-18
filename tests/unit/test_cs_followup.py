"""COI-CS-01 queue mapping tests."""

import os

import pytest

from agent.commander.cs_followup import spawn_cs_followup_ticket
from agent.commander.queue import build_queue


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

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
    try:
        os.unlink(path)
    except OSError:
        pass


def test_spawn_cs_followup_maps_to_queue(temp_db):
    tid = spawn_cs_followup_ticket(order_id="ORD-CS-1", customer_hint="test@flexgrafik.nl")
    assert tid is not None
    items = build_queue()
    cs = [i for i in items if i["queue_type"] == "cs_followup"]
    assert len(cs) >= 1
    assert cs[0]["severity"] == "ACTION"
    assert cs[0]["payload"]["ticket_id"] == tid
