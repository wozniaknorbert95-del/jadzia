"""MB shadow eval-pack v2 — accuracy + stratified sample."""

from __future__ import annotations

import uuid

from agent.db import db_insert_marketing_shadow, get_connection
from agent.marketing.shadow_eval import (
    build_eval_pack,
    compute_accuracy,
    record_eval_score,
    select_stratified_pack,
)
from agent.marketing.telegram_proposals import parse_mb_callback


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


def test_record_score_and_accuracy_gate():
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
    assert acc["n_scored"] >= 20
    # 14*1 + 4*0.5 + 2*0 = 16 / 20 = 0.8
    assert acc["accuracy"] == 0.8
    assert acc["gate_ready"] is True


def test_stratified_pack_caps_per_rule():
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


def test_build_eval_pack_v2_shape():
    _seed_shadow("HEU_SHAPE", severity="WATCH")
    pack = build_eval_pack(limit=5, window_days=14, stratified=True)
    assert pack["pack_version"] == "v2_stratified"
    assert "accuracy_snapshot" in pack
    assert "scoring" in pack
    assert isinstance(pack["decisions"], list)
