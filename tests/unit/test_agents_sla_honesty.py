"""OPS-AGENT-SLA-01 — agent sla_ok honesty (DTL clocks + untracked HITL)."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import pytest

from agent.commander.agents_registry import (
    _compute_sla_ok,
    _effective_last_run,
    list_agents,
)
from agent.db import db_commander_upsert_agent_state, db_insert_marketing_raw_ingest


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


def test_untracked_hitl_is_none_even_with_stale_run():
    stale = "2026-07-17T14:21:10+00:00"
    assert _compute_sla_ok("design", None, 86400) is None
    assert _compute_sla_ok("marketing", None, 3600) is None
    assert _compute_sla_ok("marketing", stale, 3600) is None


def test_scheduled_without_run_is_false():
    assert _compute_sla_ok("marketing_brain", None, 3600) is False
    assert _compute_sla_ok("analytics", None, 7200) is False


def test_fresh_last_run_is_true():
    last = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    assert _compute_sla_ok("analytics", last, 7200) is True


def test_stale_last_run_is_false():
    last = (datetime.now(timezone.utc) - timedelta(hours=10)).isoformat()
    assert _compute_sla_ok("analytics", last, 7200) is False


def test_pipeline_prefers_newer_dtl_over_stale_agent_state(temp_db):
    stale = "2026-07-01T00:00:00+00:00"
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    db_commander_upsert_agent_state(
        "analytics",
        {
            "status": "LIVE",
            "expected_interval_seconds": 7200,
            "last_run_at": stale,
            "held_count": 0,
        },
    )
    db_insert_marketing_raw_ingest(
        {
            "source": "ga4",
            "fetched_at": now,
            "checksum": "ga4-newer-1",
            "payload": {},
            "status": "ok",
        }
    )
    last, src = _effective_last_run("analytics", stale)
    assert last == now
    assert src == "dtl:ga4"
    agents = {a["agent_id"]: a for a in list_agents()}
    assert agents["analytics"]["sla_ok"] is True
    assert agents["analytics"]["clock_source"] == "dtl:ga4"


def test_pipeline_keeps_newer_agent_state(temp_db):
    fresh = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    old_dtl = (datetime.now(timezone.utc) - timedelta(hours=3)).replace(microsecond=0).isoformat()
    db_insert_marketing_raw_ingest(
        {
            "source": "ga4",
            "fetched_at": old_dtl,
            "checksum": "ga4-old-1",
            "payload": {},
            "status": "ok",
        }
    )
    last, src = _effective_last_run("analytics", fresh)
    assert last == fresh
    assert src == "agent_state"


def test_pipeline_agents_use_dtl_clock(temp_db):
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    db_insert_marketing_raw_ingest(
        {
            "source": "ga4",
            "fetched_at": now,
            "checksum": "ga4-sla-1",
            "payload": {},
            "status": "ok",
        }
    )
    db_insert_marketing_raw_ingest(
        {
            "source": "leads",
            "fetched_at": now,
            "checksum": "leads-sla-1",
            "payload": {},
            "status": "ok",
        }
    )
    db_insert_marketing_raw_ingest(
        {
            "source": "orders",
            "fetched_at": now,
            "checksum": "orders-sla-1",
            "payload": {},
            "status": "ok",
        }
    )
    agents = {a["agent_id"]: a for a in list_agents()}
    assert agents["analytics"]["sla_ok"] is True
    assert agents["analytics"]["clock_source"] == "dtl:ga4"
    assert agents["sales"]["sla_ok"] is True
    assert agents["sales"]["clock_source"] == "dtl:leads"
    assert agents["operations"]["sla_ok"] is True
    assert agents["operations"]["clock_source"] == "dtl:orders"
    assert agents["design"]["sla_ok"] is None
    assert agents["marketing"]["sla_ok"] is None
    assert agents["marketing_brain"]["sla_ok"] is False


def test_mb_heartbeat_makes_sla_ok(temp_db):
    last = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    db_commander_upsert_agent_state(
        "marketing_brain",
        {
            "status": "LIVE",
            "expected_interval_seconds": 3600,
            "last_run_at": last,
            "held_count": 0,
        },
    )
    agents = {a["agent_id"]: a for a in list_agents()}
    assert agents["marketing_brain"]["sla_ok"] is True
    assert agents["marketing_brain"]["clock_source"] == "agent_state"
