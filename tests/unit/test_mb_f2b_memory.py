"""MKT-BRAIN-PRO F2b — campaign memory + SQL degrade."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from agent.db import db_insert_marketing_shadow, get_connection
from agent.marketing.campaign_memory import (
    enrich_decision_with_memory,
    memory_status,
    query_similar,
    sync_from_shadow,
    upsert_decision,
)
from agent.marketing.decision_engine import run_decision_cycle
from agent.marketing.heuristics import Decision


@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    import tempfile

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr("agent.db.DB_PATH", path)
    monkeypatch.setenv("MB_CHROMA_PATH", str(tmp_path / "chroma"))
    import agent.db as db_mod

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
    get_connection()  # init schema
    yield path
    try:
        if hasattr(db_mod._local, "conn") and db_mod._local.conn:
            db_mod._local.conn.close()
            db_mod._local.conn = None
        os.unlink(path)
    except OSError:
        pass


def test_sql_fallback_when_chroma_missing(temp_db, monkeypatch):
    monkeypatch.setattr(
        "agent.marketing.campaign_memory._chroma_available",
        lambda: False,
    )
    db_insert_marketing_shadow(
        {
            "action_id": "mb_neg_1",
            "proposed_action": "block_scale",
            "heuristic_rule_id": "HEU_PROFIT_WATCHDOG",
            "llm_rationale_nl": "margin floor breached",
            "governance_result": "deny",
            "hitl_status": "denied",
            "payload": {"severity": "CRITICAL"},
        }
    )
    q = query_similar("HEU_PROFIT_WATCHDOG block_scale margin", top_k=3)
    assert q["memory_source"] == "sql_fallback"
    assert q["ok"] is True
    assert any(h.get("action_id") == "mb_neg_1" for h in q["hits"])


def test_upsert_and_query_chroma_or_fallback(temp_db):
    row = {
        "action_id": "mb_mem_1",
        "proposed_action": "propose_boost",
        "heuristic_rule_id": "HEU_ORGANIC_WINNER",
        "llm_rationale_nl": "organic lift high",
        "governance_result": "deny",
        "hitl_status": "denied",
        "payload": {"severity": "ACTION"},
    }
    up = upsert_decision(row)
    assert up.get("memory_source") in ("chroma", "sql_fallback")
    q = query_similar("HEU_ORGANIC_WINNER propose_boost organic", top_k=3)
    assert q["ok"] is True
    assert q["memory_source"] in ("chroma", "sql_fallback")


def test_enrich_adds_warning_on_negative(temp_db, monkeypatch):
    monkeypatch.setattr(
        "agent.marketing.campaign_memory._chroma_available",
        lambda: False,
    )
    db_insert_marketing_shadow(
        {
            "action_id": "mb_neg_2",
            "proposed_action": "propose_boost",
            "heuristic_rule_id": "HEU_ORGANIC_WINNER",
            "llm_rationale_nl": "boost organic",
            "governance_result": "deny",
            "hitl_status": "denied",
        }
    )
    d = Decision(
        proposed_action="propose_boost",
        heuristic_rule_id="HEU_ORGANIC_WINNER",
        would_execute=False,
        governance_result="review",
        rationale_nl="boost organic winner",
        severity="ACTION",
    )
    en = enrich_decision_with_memory(d)
    assert en["memory_source"] == "sql_fallback"
    assert en["memory_negative_hits"] >= 1
    assert "MEMORY WARNING" in (en.get("memory_warning") or "")


def test_decision_cycle_includes_memory(temp_db, monkeypatch):
    monkeypatch.setenv("MB_MODE", "shadow")
    with patch(
        "agent.marketing.campaign_memory._chroma_available",
        return_value=False,
    ):
        cycle = run_decision_cycle()
    assert "records" in cycle
    assert len(cycle["records"]) >= 1
    rec = cycle["records"][0]
    assert rec.get("memory_source") in ("chroma", "sql_fallback")


def test_memory_status_and_sync(temp_db, monkeypatch):
    monkeypatch.setattr(
        "agent.marketing.campaign_memory._chroma_available",
        lambda: False,
    )
    st = memory_status()
    assert st["ok"] is True
    assert st["chroma_installed"] is False
    sync = sync_from_shadow(limit=10)
    assert sync["ok"] is True
