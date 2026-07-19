"""MKT-BRAIN-PRO F1 — heuristics, shadow, Telegram HITL (no side-effects)."""

from __future__ import annotations

import os
from unittest.mock import patch

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from agent.db import (
    db_get_marketing_shadow,
    db_list_marketing_hypotheses,
    db_list_marketing_shadow,
    db_upsert_order,
    get_connection,
)
from agent.marketing.decision_engine import run_decision_cycle
from agent.marketing.heuristics import evaluate
from agent.marketing.runtime import run_marketing_brain_cycle
from agent.marketing.telegram_proposals import handle_mb_hitl, parse_mb_callback
from api.app import create_app

JWT_SECRET_VALUE = "test-secret-mb-f1"


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


def test_f1_schema_tables(temp_db):
    conn = get_connection()
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    for name in ("marketing_shadow_log", "marketing_hypotheses", "brain_events"):
        assert name in tables


def test_heuristics_profit_watchdog():
    decisions = evaluate(
        {
            "quality_flags": [],
            "margin_avg_pct": 0.25,
            "attribution_coverage_pct": 90.0,
            "organic_candidates": [],
        }
    )
    ids = [d.heuristic_rule_id for d in decisions]
    assert "HEU_PROFIT_WATCHDOG" in ids
    assert any(d.proposed_action == "block_scale" for d in decisions)


def test_heuristics_organic_winner():
    decisions = evaluate(
        {
            "quality_flags": [],
            "margin_avg_pct": 0.55,
            "attribution_coverage_pct": 90.0,
            "organic_candidates": [
                {"post_id": "p1", "lift_pct": 62.0, "quality_clean": True}
            ],
        }
    )
    assert any(d.heuristic_rule_id == "HEU_ORGANIC_WINNER" for d in decisions)


def test_decision_cycle_persists_shadow(temp_db, monkeypatch):
    monkeypatch.setenv("MB_MODE", "shadow")
    db_upsert_order(
        {
            "order_id": "mb-1",
            "status": "completed",
            "items": [{"sku": "X", "qty": 1, "price": 199}],
            "customer": {"email": "a@test.nl", "name": "A"},
            "total_gross": 199.0,
            "payment_id": "pay1",
            "attribution": {"utm_source": "meta", "utm_medium": "paid"},
        }
    )
    from agent.marketing.dtl.margin import ingest_order_margins
    from agent.marketing.dtl.attribution import ingest_attribution

    ingest_order_margins()
    ingest_attribution()

    with patch("agent.marketing.decision_engine.get_mb_mode", return_value="shadow"):
        result = run_decision_cycle()
    assert result["decisions_evaluated"] >= 1
    assert len(result["records"]) >= 1
    shadows = db_list_marketing_shadow(limit=10)
    assert len(shadows) >= 1
    assert shadows[0]["mb_mode"] == "shadow"
    hyps = db_list_marketing_hypotheses(limit=10)
    assert len(hyps) >= 1


def test_mb_callback_parse_and_hitl_shadow(temp_db, monkeypatch):
    monkeypatch.setenv("MB_MODE", "shadow")
    with patch("agent.marketing.decision_engine.get_mb_mode", return_value="shadow"):
        cycle = run_decision_cycle()
    action_id = cycle["records"][0]["action_id"]
    assert parse_mb_callback(f"mb_approve:{action_id}") == ("approve", action_id)
    assert parse_mb_callback(f"mb_deny:{action_id}") == ("deny", action_id)

    ok = handle_mb_hitl("approve", action_id)
    assert ok["ok"] is True
    assert ok["side_effect"] is False
    assert "SHADOW" in ok["message"]
    row = db_get_marketing_shadow(action_id)
    assert row["hitl_status"] == "approved"


def test_runtime_cycle_no_telegram(temp_db, monkeypatch):
    monkeypatch.setenv("MB_MODE", "shadow")
    with patch(
        "agent.marketing.telegram_proposals.send_mb_proposal_telegram",
        return_value=False,
    ):
        summary = run_marketing_brain_cycle(send_telegram=True)
    assert summary["ok"] is True


def test_shadow_api(temp_db):
    client = TestClient(create_app())
    token = pyjwt.encode(
        {"sub": "norbert", "role": "dowodca"},
        JWT_SECRET_VALUE,
        algorithm="HS256",
    )
    headers = {"Authorization": f"Bearer {token}"}
    with patch.dict(os.environ, {"JWT_SECRET": JWT_SECRET_VALUE}, clear=False), patch(
        "api.dependencies.JWT_SECRET",
        JWT_SECRET_VALUE,
    ):
        r = client.get("/api/v1/commander/marketing/shadow", headers=headers)
    assert r.status_code == 200
    assert "shadow" in r.json()
    assert "hypotheses" in r.json()
