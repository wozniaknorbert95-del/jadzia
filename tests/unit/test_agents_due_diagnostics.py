"""Desk diagnostics agents_due — run-due dry read-only contract (9-04)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from agent.demand_os.commander_status import build_demand_os_status


def _seed_sales_overdue(p: Path, age_h: float = 24.0) -> None:
    old = (datetime.now(timezone.utc) - timedelta(hours=age_h)).isoformat()
    p.write_text(
        json.dumps(
            {
                "sales": {
                    "role": "sales",
                    "last_run_at": old,
                    "last_action": "sync_hot",
                    "run_count": 7,
                }
            }
        ),
        encoding="utf-8",
    )


def test_agents_due_present_in_diagnostics(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("DEMAND_OS_AGENTS_HEARTBEAT", str(tmp_path / "hb.json"))
    st = build_demand_os_status()
    due = st["diagnostics"]["agents_due"]
    assert due["mode"] == "read_only"
    assert due["source"].startswith("worker.due_actions")
    assert isinstance(due["count"], int)
    assert isinstance(due["items"], list)
    # never-ran cadence roles are due by definition
    assert due["count"] >= 1
    roles = {i["role"] for i in due["items"]}
    assert "sales" in roles


def test_agents_due_reflects_overdue_only(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    p = tmp_path / "hb.json"
    monkeypatch.setenv("DEMAND_OS_AGENTS_HEARTBEAT", str(p))
    fresh = datetime.now(timezone.utc).isoformat()
    beats = {
        role: {"role": role, "last_run_at": fresh, "run_count": 1}
        for role in ("growth_lead", "sales", "validator", "icp_brain", "cre")
    }
    p.write_text(json.dumps(beats), encoding="utf-8")
    st = build_demand_os_status()
    assert st["diagnostics"]["agents_due"]["count"] == 0
    assert st["diagnostics"]["agents_due"]["items"] == []
    _seed_sales_overdue(p)
    st2 = build_demand_os_status()
    due2 = st2["diagnostics"]["agents_due"]
    assert due2["count"] >= 1
    sales_items = [i for i in due2["items"] if i["role"] == "sales"]
    assert sales_items and sales_items[0]["reason"] == "overdue"


def test_agents_due_never_dispatches(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Read-only contract: building status must not dispatch (no heartbeat write,
    no run_count bump) — desk diagnostics is observability, not control."""
    p = tmp_path / "hb.json"
    monkeypatch.setenv("DEMAND_OS_AGENTS_HEARTBEAT", str(p))
    _seed_sales_overdue(p)
    before = p.read_text(encoding="utf-8")
    st = build_demand_os_status()
    assert st["diagnostics"]["agents_due"]["count"] >= 1, "precondition: sales overdue"
    assert p.read_text(encoding="utf-8") == before, "status build must not write heartbeats"
