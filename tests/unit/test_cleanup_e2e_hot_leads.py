"""Regression tests: legacy cleanup must not delete revenue history."""

import importlib.util
import os
import sqlite3
from pathlib import Path

import pytest

from agent.commander.queue import build_queue
from agent.db import db_create_lead, db_list_leads
from agent.revenue.reconciliation import (
    apply_unpersisted_classifications,
    build_reconciliation_report,
)


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


def _load_cleanup_mod():
    script = Path(__file__).resolve().parents[2] / "deployment" / "cleanup-e2e-hot-leads.py"
    spec = importlib.util.spec_from_file_location("cleanup_e2e_hot_leads", script)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_cleanup_finds_e2e_but_deletion_is_blocked(temp_db):
    mod = _load_cleanup_mod()

    db_create_lead(
        {
            "email": "deploy02-int004-test@flexgrafik.nl",
            "name": "Deploy02 Smoke",
            "source": "game",
            "game_score": 420,
            "consent_status": True,
        }
    )
    db_create_lead(
        {
            "email": "int004-e2e-20260626@flexgrafik.nl",
            "name": "E2E Deploy02",
            "source": "game",
            "game_score": 250,
            "consent_status": True,
        }
    )
    db_create_lead(
        {
            "email": "jan@bouw.com",
            "name": "JanBouw",
            "source": "game",
            "game_score": 3563,
            "consent_status": True,
        }
    )

    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    matches = mod.find_e2e_leads(conn)
    assert len(matches) == 2
    with pytest.raises(RuntimeError, match="Revenue history deletion is disabled"):
        mod.delete_leads(conn, [int(m["id"]) for m in matches])
    conn.close()

    remaining = db_list_leads(limit=20)
    emails = {r["email"] for r in remaining}
    assert "jan@bouw.com" in emails
    assert any(e.startswith("deploy02-") for e in emails)
    assert any(e.startswith("int004-e2e-") for e in emails)

    apply_unpersisted_classifications(build_reconciliation_report())
    items = build_queue()
    hot = [i for i in items if i["queue_type"] == "hot_lead"]
    assert all("deploy02" not in (i.get("title") or "").lower() for i in hot)
    assert any("jan@bouw.com" in (i.get("title") or "") for i in hot)
