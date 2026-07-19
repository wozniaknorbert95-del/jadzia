"""Propose cutover preflight verdikt (pure build_*)."""

from __future__ import annotations

from agent.marketing.propose_preflight import build_propose_preflight


def _base(**overrides):
    data = {
        "accuracy": {
            "gate_ready": True,
            "n_scored": 20,
            "accuracy": 1.0,
            "gate_reason": "ok",
            "consecutive_weeks_note": "Prefer 2 consecutive weeks",
        },
        "breakers": {
            "allowed": False,
            "trips": [
                {
                    "breaker_id": "CB_SHADOW",
                    "message": "shadow",
                    "severity": "critical",
                }
            ],
        },
        "data_health": {"overall_status": "ok"},
        "mb_mode": "shadow",
        "brain_bus": {"ecosystem_flags": []},
        "memory": {"ok": True, "memory_source": "chroma", "count": 7},
        "tip": "deadbeef",
        "l0_ic_pass": True,
        "purchase_park": True,
    }
    data.update(overrides)
    return build_propose_preflight(**data)


def test_ready_for_go_with_only_cb_shadow():
    out = _base()
    assert out["verdict"] == "READY_FOR_GO"
    assert out["mb_mode_flip"] == "DO_NOT_FLIP"
    assert "GO propose" in out["go_ticket"]
    assert "deadbeef" in out["go_ticket"]
    assert any("2 consecutive" in w for w in out["warns"])


def test_blocked_when_gate_not_ready():
    out = _base(
        accuracy={
            "gate_ready": False,
            "n_scored": 18,
            "accuracy": 1.0,
            "gate_reason": "n_scored_lt_20",
        }
    )
    assert out["verdict"] == "BLOCKED"
    assert any(c["id"] == "accuracy_gate" and not c["ok"] for c in out["checks"])


def test_blocked_on_data_health_red():
    out = _base(data_health={"overall_status": "red"})
    assert out["verdict"] == "BLOCKED"


def test_blocked_on_unexpected_breaker():
    out = _base(
        breakers={
            "allowed": False,
            "trips": [
                {"breaker_id": "CB_SHADOW", "message": "s", "severity": "critical"},
                {"breaker_id": "CB_MARGIN", "message": "m", "severity": "critical"},
            ],
        }
    )
    assert out["verdict"] == "BLOCKED"


def test_blocked_when_already_propose():
    out = _base(mb_mode="propose")
    assert out["verdict"] == "BLOCKED"
