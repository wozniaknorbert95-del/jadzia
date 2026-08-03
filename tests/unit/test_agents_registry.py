"""Demand OS agent registry — SoT contract, unified dispatch, hub/CLI wiring."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from agent.demand_os.agents import (
    AGENT_REGISTRY,
    all_roles,
    dispatch,
    get_agent,
    list_agents,
)

ROOT = Path(__file__).resolve().parents[2]

EXPECTED_ROLES = {
    "growth_lead": 1,
    "icp_brain": 1,
    "tt": 1,
    "sales": 1,
    "validator": 1,
    "cf": 2,
    "fb": 2,
    "blog": 3,
    "cre": 3,
}


def test_registry_covers_all_waves():
    assert set(all_roles()) == set(EXPECTED_ROLES)
    for role, wave in EXPECTED_ROLES.items():
        spec = AGENT_REGISTRY[role]
        assert spec["wave"] == wave
        assert callable(spec["runner"])
        assert spec["actions"], f"{role} must declare actions"
        assert set(spec["mutating_actions"]) <= set(spec["actions"])
        assert spec["label"]
        assert spec["kpi"]


def test_get_agent_normalizes():
    assert get_agent("  Growth_Lead ") is AGENT_REGISTRY["growth_lead"]
    assert get_agent("nope") is None


def test_list_agents_honest_projection(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("DEMAND_OS_MARKETING_HITL", raising=False)
    rows = list_agents()
    assert len(rows) == len(EXPECTED_ROLES)
    by_role = {r["role"]: r for r in rows}
    for role in EXPECTED_ROLES:
        row = by_role[role]
        assert row["shell"] is True
        assert row["marketing"] == "PARKED_LAST"
        assert row["actions"]
    for gated in ("tt", "cf", "fb", "blog"):
        assert by_role[gated]["live_gated"] is True
        assert by_role[gated]["live_allowed"] is False
        assert "PARKED" in by_role[gated]["blocked_reason"]
    for open_role in ("growth_lead", "sales", "validator", "cre", "icp_brain"):
        assert by_role[open_role]["live_allowed"] is True
        assert by_role[open_role]["blocked_reason"] == ""


def test_list_agents_live_after_go(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DEMAND_OS_MARKETING_HITL", "GO")
    rows = {r["role"]: r for r in list_agents()}
    assert rows["cf"]["live_allowed"] is True
    assert rows["cf"]["marketing"] == "HITL_LIVE"


def test_dispatch_unknown_role_fails_explicit():
    out = dispatch("bogus", action="status")
    assert out["ok"] is False
    assert out["result"] is None
    assert "unknown role" in out["error"]
    assert out["wave"] is None


def test_dispatch_disallowed_action_fails_explicit():
    out = dispatch("cf", action="publish_live")
    assert out["ok"] is False
    assert "not allowed" in out["error"]
    assert out["wave"] == 2


@pytest.mark.parametrize(
    "role,action",
    [
        ("growth_lead", "status"),
        ("growth_lead", "money_check"),
        ("icp_brain", "show"),
        ("tt", "queue"),
        ("sales", "list_hot"),
        ("validator", "compliance"),
        ("cf", "brief"),
        ("cf", "proof"),
        ("fb", "allowlist"),
        ("blog", "status"),
        ("cre", "status"),
    ],
)
def test_dispatch_readonly_smoke(monkeypatch: pytest.MonkeyPatch, role: str, action: str):
    monkeypatch.delenv("DEMAND_OS_MARKETING_HITL", raising=False)
    out = dispatch(role, action=action)
    assert out["ok"] is True, out.get("error")
    assert out["role"] == role
    assert out["wave"] == EXPECTED_ROLES[role]
    assert out["action"] == action
    assert out["result"] is not None
    assert out["marketing"] == "PARKED_LAST"
    assert "raw" in out


def test_dispatch_runner_exception_never_raises(monkeypatch: pytest.MonkeyPatch):
    def boom(role: str, **kwargs):
        raise RuntimeError("shell exploded")

    monkeypatch.setitem(AGENT_REGISTRY["cre"], "runner", boom)
    out = dispatch("cre", action="status")
    assert out["ok"] is False
    assert "shell exploded" in out["error"]


def _run_hub(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / "tools" / "demand_os_hub.py"), *argv],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_hub_agents_list_cli():
    proc = _run_hub("agents", "list")
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["count"] == len(EXPECTED_ROLES)
    assert payload["agents"][0]["shell"] is True


def test_hub_agents_list_wave_filter():
    proc = _run_hub("agents", "list", "--wave", "2")
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["count"] == 2
    assert {a["role"] for a in payload["agents"]} == {"cf", "fb"}


def test_hub_agents_run_readonly_ok():
    proc = _run_hub("agents", "run", "--role", "validator", "--action", "compliance")
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["role"] == "validator"


def test_hub_agents_run_mutating_blocked():
    proc = _run_hub("agents", "run", "--role", "growth_lead", "--action", "sync_starts")
    assert proc.returncode == 1
    payload = json.loads(proc.stdout)
    assert payload["ok"] is False
    assert "dedicated hub subcommand" in payload["error"]


def test_legacy_cli_uses_registry():
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "demand_os_agents.py"),
            "--role",
            "cf",
            "--action",
            "brief",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["role"] == "cf"
    assert payload["action"] == "brief"
    assert payload["raw"]["role"] == "cf"


def test_legacy_cli_mutating_defaults_dry():
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "demand_os_agents.py"),
            "--role",
            "growth_lead",
            "--action",
            "sync_starts",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["raw"]["result"]["dry_run"] is True
