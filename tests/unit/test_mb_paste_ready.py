"""F4b paste_ready v1 builder + governance/Telegram wiring."""

from __future__ import annotations

import os
import tempfile
import uuid
from unittest.mock import patch

import pytest

from agent.db import (
    db_commander_list_tickets,
    db_get_marketing_shadow,
    db_insert_marketing_shadow,
    get_connection,
)
from agent.marketing.governance import (
    approve_and_mint,
    execute_action,
    format_approve_telegram_message,
    mint_approval_token,
)
from agent.marketing.paste_ready import (
    PASTE_READY_VERSION,
    TG_TEXT_MAX,
    build_paste_ready,
    is_paste_executable,
)
from agent.marketing.telegram_proposals import handle_mb_hitl


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
        os.unlink(path)
    except OSError:
        pass


def _shadow(
    *,
    action: str = "propose_boost",
    rule: str = "HEU_ORGANIC_WINNER",
    would: int = 1,
    dims: dict | None = None,
    severity: str = "CRITICAL",
) -> dict:
    aid = f"mb_{uuid.uuid4().hex[:12]}"
    row = {
        "action_id": aid,
        "observed_facts_ref": "test",
        "proposed_action": action,
        "heuristic_rule_id": rule,
        "llm_rationale_nl": f"rationale {action}",
        "would_execute": would,
        "governance_result": "review",
        "mb_mode": "propose",
        "hitl_status": "pending",
        "payload": {
            "severity": severity,
            "dims": dims
            or {
                "post_id": "pg_123",
                "lift_pct": 42.0,
                "quality_clean": True,
            },
            "facts_summary": {
                "margin_avg_pct": 61.0,
                "attribution_coverage_pct": 80.0,
                "red_flags": 0,
            },
        },
    }
    assert db_insert_marketing_shadow(row)
    return db_get_marketing_shadow(aid)


def test_builder_boost_fields():
    shadow = {
        "action_id": "a1",
        "proposed_action": "propose_boost",
        "heuristic_rule_id": "HEU_ORGANIC_WINNER",
        "llm_rationale_nl": "boost me",
        "would_execute": True,
        "payload": {
            "severity": "CRITICAL",
            "dims": {"post_id": "p9", "lift_pct": 55.0, "quality_clean": True},
        },
    }
    paste = build_paste_ready(shadow, "mkt-test01")
    assert paste["version"] == PASTE_READY_VERSION
    assert paste["fields"]["post_id"] == "p9"
    assert paste["budget_hint_eur_day"] == 5
    assert paste["ads_api_create"] == "PARK"
    assert paste["campaign_ref"] == "zzp_branding_check_v1"
    assert paste["create_commander_ticket"] is True
    assert "PARK" in paste["text"]
    assert len(paste["text_tg"]) <= TG_TEXT_MAX


def test_builder_hold_no_commander():
    shadow = {
        "action_id": "a2",
        "proposed_action": "hold",
        "heuristic_rule_id": "HEU_NO_SIGNAL",
        "llm_rationale_nl": "hold",
        "would_execute": False,
        "payload": {"severity": "INFO", "facts_summary": {"red_flags": 0}},
    }
    paste = build_paste_ready(shadow, "mkt-hold01")
    assert paste["create_commander_ticket"] is False
    assert is_paste_executable(shadow) is False
    assert "ACK" in paste["text"] or "observability" in paste["text"].lower()


def test_builder_unknown_generic():
    shadow = {
        "action_id": "a3",
        "proposed_action": "weird_new_action",
        "heuristic_rule_id": "HEU_X",
        "llm_rationale_nl": "x",
        "would_execute": True,
        "payload": {"severity": "ACTION", "dims": {"k": 1}},
    }
    paste = build_paste_ready(shadow, "mkt-gen01")
    assert paste["version"] == 1
    assert paste["fields"]["raw_action"] == "weird_new_action"
    assert paste["text"]


def test_builder_block_scale():
    shadow = {
        "action_id": "a4",
        "proposed_action": "block_scale",
        "heuristic_rule_id": "HEU_MARGIN",
        "llm_rationale_nl": "stop",
        "would_execute": True,
        "payload": {"severity": "CRITICAL", "dims": {"margin_avg_pct": 10}},
    }
    paste = build_paste_ready(shadow, "mkt-blk")
    assert paste["create_commander_ticket"] is True
    assert any("STOP" in c for c in paste["checklist"])


def test_execute_denied_shadow(temp_db, monkeypatch):
    monkeypatch.setenv("MB_MODE", "shadow")
    row = _shadow()
    tok = mint_approval_token(row["action_id"])
    with patch("agent.marketing.governance.get_mb_mode", return_value="shadow"):
        with patch(
            "agent.marketing.circuit_breakers.get_mb_mode",
            return_value="shadow",
        ):
            result = execute_action(row["action_id"], tok["approval_token"])
    assert result["ok"] is False
    assert result.get("error") in ("circuit_breaker", "shadow_mode")
    fresh = db_get_marketing_shadow(row["action_id"])
    assert not (fresh.get("payload") or {}).get("paste_ready")


def test_execute_propose_paste_and_idempotent(temp_db, monkeypatch):
    monkeypatch.setenv("MB_MODE", "propose")
    row = _shadow()
    aid = row["action_id"]
    with patch("agent.marketing.governance.get_mb_mode", return_value="propose"):
        with patch(
            "agent.marketing.circuit_breakers.get_mb_mode",
            return_value="propose",
        ):
            with patch(
                "agent.marketing.circuit_breakers.is_execute_allowed",
                return_value={"allowed": True, "trips": [], "blocked_by": []},
            ):
                t1 = mint_approval_token(aid)
                r1 = execute_action(aid, t1["approval_token"], actor="t1")
                assert r1["ok"] is True
                paste1 = r1["result"]["paste_ready"]
                assert paste1["version"] == 1
                assert paste1["fields"]["post_id"] == "pg_123"
                cid = r1["result"]["commander_ticket_id"]
                assert cid is not None

                t2 = mint_approval_token(aid)
                r2 = execute_action(aid, t2["approval_token"], actor="t2")
                assert r2["ok"] is True
                assert r2.get("cached") is True
                assert r2["result"]["commander_ticket_id"] == cid
                assert r2["result"]["paste_ready"]["ticket_id"] == paste1["ticket_id"]

    tickets = db_commander_list_tickets(limit=20)
    mb = [t for t in tickets if t.get("source") == "mb_propose"]
    assert len(mb) == 1


def test_approve_and_mint_propose_auto(temp_db, monkeypatch):
    monkeypatch.setenv("MB_MODE", "propose")
    row = _shadow()
    with patch("agent.marketing.governance.get_mb_mode", return_value="propose"):
        with patch(
            "agent.marketing.circuit_breakers.is_execute_allowed",
            return_value={"allowed": True, "trips": [], "blocked_by": []},
        ):
            out = approve_and_mint(row["action_id"])
    assert out["ok"] is True
    assert out.get("execute", {}).get("ok") is True
    paste = out["execute"]["result"]["paste_ready"]
    msg = format_approve_telegram_message(out, db_get_marketing_shadow(row["action_id"]))
    assert "approval_token" not in msg
    assert "POST /api" not in msg
    assert "PARK" in msg or "paste-ready" in msg.lower()
    assert paste["version"] == 1


def test_approve_hold_ack_only(temp_db, monkeypatch):
    monkeypatch.setenv("MB_MODE", "propose")
    row = _shadow(action="hold", rule="HEU_NO_SIGNAL", would=0, severity="INFO")
    with patch("agent.marketing.governance.get_mb_mode", return_value="propose"):
        out = approve_and_mint(row["action_id"])
    assert out.get("ack_only") is True
    assert out.get("execute") is None
    msg = format_approve_telegram_message(out, row)
    assert "HOLD" in msg or "ACK" in msg
    assert out.get("approval_token")  # internal
    assert "approval_token" not in msg


def test_tg_callback_approve_no_token_leak(temp_db, monkeypatch):
    monkeypatch.setenv("MB_MODE", "propose")
    row = _shadow()
    with patch("agent.marketing.governance.get_mb_mode", return_value="propose"):
        with patch(
            "agent.marketing.circuit_breakers.is_execute_allowed",
            return_value={"allowed": True, "trips": [], "blocked_by": []},
        ):
            res = handle_mb_hitl("approve", row["action_id"])
    assert res["ok"] is True
    assert "approval_token" not in res
    assert "approval_token" not in (res.get("message") or "")
    assert "PARK" in res["message"] or "paste-ready" in res["message"].lower()


def test_text_tg_max_length():
    shadow = {
        "action_id": "long",
        "proposed_action": "propose_boost",
        "heuristic_rule_id": "HEU_ORGANIC_WINNER",
        "llm_rationale_nl": "x" * 5000,
        "would_execute": True,
        "payload": {
            "severity": "CRITICAL",
            "dims": {"post_id": "p", "lift_pct": 1},
        },
    }
    paste = build_paste_ready(shadow, "mkt-long")
    assert len(paste["text_tg"]) <= TG_TEXT_MAX
