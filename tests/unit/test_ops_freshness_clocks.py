"""OPS-FRESHNESS-01 — clocks for analytics freshness must be pipeline/health, not business quiet."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import pytest

from agent.commander import sla
from agent.db import db_commander_set_setting, db_insert_marketing_raw_ingest


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
        if hasattr(db_mod._local, "conn") and db_mod._local.conn:
            db_mod._local.conn.close()
            db_mod._local.conn = None
        os.unlink(path)
    except OSError:
        pass


def test_dtl_ingest_clock_not_business_event(temp_db):
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    db_insert_marketing_raw_ingest(
        {
            "source": "orders",
            "fetched_at": now,
            "checksum": "orders-fresh-1",
            "payload": {"count": 1},
            "status": "ok",
        }
    )
    assert sla.dtl_ingest_fetched_at("orders") == now
    assert sla.freshness_status("orders", sla.dtl_ingest_fetched_at("orders"))["status"] == "ok"


def test_worker_heartbeat_uses_health_last_ok_not_dowodca(temp_db):
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    db_commander_set_setting("health:last_ok", json.dumps(now))
    db_commander_set_setting(
        "dowodca_last_active_at",
        json.dumps("2020-01-01T00:00:00+00:00"),
    )
    assert sla.worker_heartbeat_at() == now
    assert sla.freshness_status("worker", sla.worker_heartbeat_at())["status"] == "ok"


def test_worker_heartbeat_falls_back_to_dtl(temp_db):
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    db_insert_marketing_raw_ingest(
        {
            "source": "ga4",
            "fetched_at": now,
            "checksum": "ga4-fresh-1",
            "payload": {},
            "status": "ok",
        }
    )
    assert sla.worker_heartbeat_at() == now
