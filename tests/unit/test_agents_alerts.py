"""Worker failure alerts — reader contract + doctor worker_failures (9-06 OPT-B)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from agent.demand_os.agents.alerts import active_alerts, default_alerts_path


def _line(ts: datetime, **extra) -> str:
    rec = {"ts": ts.isoformat(timespec="seconds"), "unit": "demand-os-agents-worker.service",
           "kind": "onfailure", "source": "systemd", "resolved": False}
    rec.update(extra)
    return json.dumps(rec)


def test_missing_file_means_no_alerts(tmp_path: Path):
    assert active_alerts(path=tmp_path / "nope.jsonl") == []


def test_fresh_unresolved_alert_is_active(tmp_path: Path):
    p = tmp_path / "ALERTS.jsonl"
    now = datetime.now(timezone.utc)
    p.write_text(_line(now - timedelta(minutes=5)) + "\n", encoding="utf-8")
    out = active_alerts(path=p)
    assert len(out) == 1
    assert out[0]["kind"] == "onfailure"


def test_old_alert_auto_expires(tmp_path: Path):
    p = tmp_path / "ALERTS.jsonl"
    now = datetime.now(timezone.utc)
    p.write_text(_line(now - timedelta(hours=25)) + "\n", encoding="utf-8")
    assert active_alerts(path=p) == []


def test_resolved_alert_ignored(tmp_path: Path):
    p = tmp_path / "ALERTS.jsonl"
    now = datetime.now(timezone.utc)
    p.write_text(_line(now - timedelta(minutes=1), resolved=True) + "\n", encoding="utf-8")
    assert active_alerts(path=p) == []


def test_bad_lines_are_tolerated(tmp_path: Path):
    """A half-written or corrupt line must never kill the doctor check."""
    p = tmp_path / "ALERTS.jsonl"
    now = datetime.now(timezone.utc)
    p.write_text(
        '{"ts": "not-a-date"}\n'
        "{broken json\n"
        '"plain string"\n'
        "\n"
        + _line(now - timedelta(minutes=2))
        + "\n",
        encoding="utf-8",
    )
    out = active_alerts(path=p)
    assert len(out) == 1


def test_default_path_env_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("DEMAND_OS_ALERTS_LOG", str(tmp_path / "custom.jsonl"))
    assert default_alerts_path() == tmp_path / "custom.jsonl"


def test_doctor_worker_failures_advisory_and_blocking(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Same severity contract as agents_staleness: advisory dev / blocking prod."""
    from agent.demand_os.doctor import run_doctor

    p = tmp_path / "ALERTS.jsonl"
    now = datetime.now(timezone.utc)
    p.write_text(_line(now - timedelta(minutes=3)) + "\n", encoding="utf-8")
    monkeypatch.setenv("DEMAND_OS_ALERTS_LOG", str(p))

    monkeypatch.delenv("DEMAND_OS_STALENESS_BLOCKING", raising=False)
    rep = run_doctor()
    check = next(c for c in rep.checks if c["name"] == "worker_failures")
    assert check["ok"] is False and "[advisory]" in check["detail"]
    assert "1 failure(s) <24h" in check["detail"]
    assert rep.ok is True, "advisory mode must not fail doctor"

    monkeypatch.setenv("DEMAND_OS_STALENESS_BLOCKING", "1")
    rep2 = run_doctor()
    check2 = next(c for c in rep2.checks if c["name"] == "worker_failures")
    assert check2["ok"] is False and "[blocking]" in check2["detail"]
    assert rep2.ok is False
    assert any("worker_failures FAIL (blocking mode)" in e for e in rep2.errors)

    monkeypatch.delenv("DEMAND_OS_STALENESS_BLOCKING", raising=False)
    p.unlink()
    rep3 = run_doctor()
    check3 = next(c for c in rep3.checks if c["name"] == "worker_failures")
    assert check3["ok"] is True and "no active worker failures" in check3["detail"]


def test_hub_run_due_exit_code_reflects_role_errors(monkeypatch: pytest.MonkeyPatch):
    """F3 class: errors>0 must exit 2 so systemd OnFailure fires (worker.py
    honest envelope keeps ok=True on per-role errors)."""
    import argparse

    from tools.demand_os_hub import cmd_agents_run_due

    args = argparse.Namespace(apply=True)
    monkeypatch.setattr(
        "agent.demand_os.agents.worker.run_due",
        lambda dry_run: {"ok": True, "errors": 2, "runs": [], "due": []},
    )
    assert cmd_agents_run_due(args) == 2
    monkeypatch.setattr(
        "agent.demand_os.agents.worker.run_due",
        lambda dry_run: {"ok": True, "errors": 0, "runs": [], "due": []},
    )
    assert cmd_agents_run_due(args) == 0
    monkeypatch.setattr(
        "agent.demand_os.agents.worker.run_due",
        lambda dry_run: {"ok": False, "errors": 0, "runs": [], "due": []},
    )
    assert cmd_agents_run_due(args) == 1
