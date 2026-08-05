"""Agents worker loop — due logic, live_gated exclusion, dry/apply honesty."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent.demand_os.agents import worker
from agent.demand_os.agents.worker import due_actions, run_due


def _seed_heartbeat(path: Path, role: str, *, age_hours: float, action: str = "status"):
    from datetime import datetime, timedelta, timezone

    ts = (datetime.now(timezone.utc) - timedelta(hours=age_hours)).isoformat()
    data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    data[role] = {"role": role, "last_run_at": ts, "last_action": action, "run_count": 1}
    path.write_text(json.dumps(data), encoding="utf-8")


def test_due_all_when_no_heartbeat(tmp_path: Path):
    due = due_actions(path=tmp_path / "hb.json")
    assert due  # every cadence entry is due when never ran
    assert all(d["reason"] == "never_ran" for d in due)
    roles = {d["role"] for d in due}
    assert "growth_lead" in roles and "sales" in roles
    # live_gated roles are never in the cadence map output
    assert not ({"tt", "cf", "fb", "blog"} & roles)


def test_due_respects_fresh_heartbeat(tmp_path: Path):
    hb = tmp_path / "hb.json"
    for role in ("growth_lead", "sales", "validator", "icp_brain", "cre"):
        _seed_heartbeat(hb, role, age_hours=1.0)
    assert due_actions(path=hb) == []


def test_due_skips_live_gated_and_actions_not_in_registry(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Defensive branches: live_gated cadence role excluded (belt-and-braces —
    worker is tool-only), cadence action missing from registry spec skipped."""
    monkeypatch.setattr(
        worker,
        "AGENT_REGISTRY",
        {
            "growth_lead": {"live_gated": True, "actions": ["sync_starts"]},
            "sales": {"actions": ["list_hot"]},
        },
    )
    monkeypatch.setattr(
        worker,
        "CADENCE",
        {"growth_lead": {"sync_starts": 24.0}, "sales": {"sync_hot": 6.0}},
    )
    assert due_actions(path=tmp_path / "hb.json") == []


def test_due_sales_overdue_at_6h(tmp_path: Path):
    hb = tmp_path / "hb.json"
    _seed_heartbeat(hb, "sales", age_hours=7.0)
    for role in ("growth_lead", "validator", "icp_brain", "cre"):
        _seed_heartbeat(hb, role, age_hours=1.0)
    due = due_actions(path=hb)
    assert due and all(d["role"] == "sales" for d in due)
    assert all(d["reason"] == "overdue" for d in due)


def test_cadence_map_covers_only_registry_actions():
    for role, actions in worker.CADENCE.items():
        from agent.demand_os.agents.registry import AGENT_REGISTRY

        spec = AGENT_REGISTRY[role]
        assert not spec["live_gated"], f"{role} must be tool-side"
        for action in actions:
            assert action in spec["actions"], f"{role}.{action} not in registry"


def test_run_due_dry_run_dispatches_nothing(tmp_path: Path):
    out = run_due(dry_run=True, path=tmp_path / "hb.json")
    assert out["ok"] is True
    assert out["mode"] == "dry_run"
    assert out["dispatched"] == 0
    assert all(r["status"] == "dry_run" for r in out["runs"])


def test_run_due_apply_dispatches_and_records(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("DEMAND_OS_A2A_BUS", str(tmp_path / "bus.jsonl"))
    monkeypatch.setenv("DEMAND_OS_SET_NOW", str(tmp_path / "set-now"))
    (tmp_path / "set-now").mkdir()
    hb = tmp_path / "hb.json"
    monkeypatch.setenv("DEMAND_OS_AGENTS_HEARTBEAT", str(hb))
    out = run_due(dry_run=False, path=hb)
    assert out["ok"] is True
    assert out["mode"] == "apply"
    assert out["dispatched"] + out["errors"] == len(out["runs"])
    # auto-heartbeat: after apply, at least one cadence role has a fresh record
    beats = json.loads(hb.read_text(encoding="utf-8")) if hb.is_file() else {}
    assert beats, "apply must record heartbeats via dispatch auto-heartbeat"
