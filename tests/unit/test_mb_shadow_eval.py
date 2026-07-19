"""MB shadow eval-pack v2 — accuracy + stratified sample."""

from __future__ import annotations

import os
import tempfile
import uuid

import pytest

from agent.db import db_insert_marketing_shadow, get_connection
from agent.marketing.shadow_eval import (
    build_eval_pack,
    compute_accuracy,
    record_eval_score,
    select_stratified_pack,
)
from agent.marketing.telegram_proposals import parse_mb_callback


@pytest.fixture
def temp_db(monkeypatch):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr("agent.db.DB_PATH", path)
    import agent.db as db_mod

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
    get_connection()
    yield path
    try:
        if hasattr(db_mod._local, "conn") and db_mod._local.conn:
            db_mod._local.conn.close()
            db_mod._local.conn = None
    except Exception:
        pass


def _seed_shadow(rule: str, severity: str = "ACTION", would: int = 1) -> str:
    aid = f"eva_{uuid.uuid4().hex[:12]}"
    assert db_insert_marketing_shadow(
        {
            "action_id": aid,
            "observed_facts_ref": "test",
            "proposed_action": "test_action",
            "heuristic_rule_id": rule,
            "llm_rationale_nl": f"rationale {rule}",
            "would_execute": would,
            "governance_result": "review",
            "mb_mode": "shadow",
            "hitl_status": "pending",
            "payload": {"severity": severity, "rationale_nl": f"rationale {rule}"},
        }
    )
    return aid


def test_parse_mb_score_callbacks():
    assert parse_mb_callback("mb_score_agree:abc") == ("score_agree", "abc")
    assert parse_mb_callback("mb_score_partial:x") == ("score_partial", "x")
    assert parse_mb_callback("mb_score_disagree:y") == ("score_disagree", "y")


def test_record_score_and_accuracy_gate(temp_db):
    aids = []
    for i in range(20):
        aids.append(_seed_shadow(f"HEU_TEST_{i % 5}", severity="ACTION"))

    for aid in aids[:14]:
        assert record_eval_score(aid, "agree")["ok"]
    for aid in aids[14:18]:
        assert record_eval_score(aid, "partial")["ok"]
    for aid in aids[18:]:
        assert record_eval_score(aid, "disagree")["ok"]

    acc = compute_accuracy(window_days=14)
    assert acc["n_scored"] == 20
    # 14*1 + 4*0.5 + 2*0 = 16 / 20 = 0.8
    assert acc["accuracy"] == 0.8
    assert acc["gate_ready"] is True


def test_stratified_pack_caps_per_rule(temp_db):
    for _ in range(8):
        _seed_shadow("HEU_NO_SIGNAL", severity="INFO", would=0)
    for _ in range(5):
        _seed_shadow("HEU_CPA_SPIKE", severity="CRITICAL", would=1)
    for _ in range(5):
        _seed_shadow("HEU_MARGIN", severity="ACTION", would=1)

    pack = select_stratified_pack(target_n=10, window_days=14, max_per_rule=3)
    assert len(pack) <= 10
    by_rule = {}
    for r in pack:
        rid = r["heuristic_rule_id"]
        by_rule[rid] = by_rule.get(rid, 0) + 1
        assert by_rule[rid] <= 3
    # Prefer non-NO_SIGNAL when rich
    rules = {r["heuristic_rule_id"] for r in pack}
    assert "HEU_CPA_SPIKE" in rules or "HEU_MARGIN" in rules


def test_build_eval_pack_v2_shape(temp_db):
    _seed_shadow("HEU_SHAPE", severity="WATCH")
    pack = build_eval_pack(limit=5, window_days=14, stratified=True)
    assert pack["pack_version"] == "v2_stratified"
    assert "accuracy_snapshot" in pack
    assert "scoring" in pack
    assert isinstance(pack["decisions"], list)


def test_eval_nudge_skips_when_recent(temp_db, monkeypatch):
    from agent.db import db_commander_upsert_agent_state
    from agent.marketing import shadow_eval as se
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    db_commander_upsert_agent_state(
        "mb_eval_nudge",
        {"status": "LIVE", "last_run_at": now, "expected_interval_seconds": 604800},
    )
    called = {"n": 0}

    def _fake(**kwargs):
        called["n"] += 1
        return {"ok": True, "sent": 0}

    monkeypatch.setattr(
        "agent.marketing.telegram_proposals.send_eval_pack_telegram",
        _fake,
    )
    out = se.run_eval_nudge_if_due(interval_seconds=604800)
    assert out.get("skipped") is True
    assert called["n"] == 0


def test_eval_nudge_fires_when_stale(temp_db, monkeypatch):
    from agent.db import db_commander_upsert_agent_state
    from agent.marketing import shadow_eval as se

    db_commander_upsert_agent_state(
        "mb_eval_nudge",
        {
            "status": "LIVE",
            "last_run_at": "2020-01-01T00:00:00+00:00",
            "expected_interval_seconds": 604800,
        },
    )
    called = {"n": 0}

    def _fake(**kwargs):
        called["n"] += 1
        return {"ok": True, "sent": 2, "n_pack": 2}

    monkeypatch.setattr(
        "agent.marketing.telegram_proposals.send_eval_pack_telegram",
        _fake,
    )
    out = se.run_eval_nudge_if_due(interval_seconds=604800)
    assert out.get("skipped") is False
    assert out.get("ok") is True
    assert called["n"] == 1


def test_eval_nudge_disabled():
    from agent.marketing.shadow_eval import run_eval_nudge_if_due

    out = run_eval_nudge_if_due(interval_seconds=0)
    assert out.get("skipped") is True
    assert out.get("reason") == "disabled"


def test_recommend_staff_attribution_hold():
    from agent.marketing.shadow_eval import recommend_staff_score

    rec = recommend_staff_score(
        {
            "heuristic_rule_id": "HEU_ATTRIBUTION_LOW",
            "proposed_action": "hold",
            "would_execute": False,
            "rationale_nl": "Attribution coverage 8%",
        }
    )
    assert rec["eval_score"] == "agree"
    assert "klienci" in rec["pl"].lower() or "reklam" in rec["pl"].lower()


def test_staff_eval_batch_scores(temp_db, monkeypatch):
    from agent.marketing import shadow_eval as se

    aid = _seed_shadow("HEU_ATTRIBUTION_LOW", severity="ACTION", would=0)
    monkeypatch.setattr(
        "agent.marketing.telegram_proposals.send_staff_eval_summary_telegram",
        lambda *a, **k: True,
    )
    out = se.run_staff_eval_batch(limit=5, window_days=14, notify_telegram=True)
    assert out.get("ok") is True
    assert out.get("scored", 0) >= 1
    scored_ids = {r["action_id"] for r in out.get("results") or []}
    assert aid in scored_ids or out.get("scored", 0) >= 1
