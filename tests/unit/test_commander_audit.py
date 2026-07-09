"""Audit hash-chain tests (N2)."""

import os
import pytest


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


def test_audit_chain_valid(temp_db):
    from agent.commander.audit import append_audit, verify_audit_chain

    append_audit(
        actor_id="a",
        actor_role="dowodca",
        action="test1",
        source="pytest",
    )
    append_audit(
        actor_id="a",
        actor_role="dowodca",
        action="test2",
        source="pytest",
    )
    result = verify_audit_chain()
    assert result["valid"] is True
    assert result["rows_checked"] >= 2
