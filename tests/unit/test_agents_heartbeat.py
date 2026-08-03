"""Agent heartbeat — last_run honesty per registry role (6-03)."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from agent.demand_os.agents.heartbeat import (
    heartbeat_view,
    load_heartbeats,
    record_heartbeat,
)
from agent.demand_os.agents.registry import list_agents

ROOT = Path(__file__).resolve().parents[2]


def test_record_and_view_heartbeat(tmp_path: Path):
    p = tmp_path / "hb.json"
    rec = record_heartbeat("validator", action="compliance", path=p)
    assert rec["role"] == "validator"
    assert rec["last_action"] == "compliance"
    assert rec["run_count"] == 1
    view = heartbeat_view("validator", path=p)
    assert view["run_count"] == 1
    assert view["stale"] is False
    assert view["age_days"] is not None and view["age_days"] < 1


def test_heartbeat_increments_and_isolates(tmp_path: Path):
    p = tmp_path / "hb.json"
    record_heartbeat("sales", path=p)
    record_heartbeat("sales", path=p)
    record_heartbeat("cre", path=p)
    data = load_heartbeats(path=p)
    assert data["sales"]["run_count"] == 2
    assert data["cre"]["run_count"] == 1
    assert "validator" not in data


def test_heartbeat_unknown_role_rejected(tmp_path: Path):
    with pytest.raises(ValueError):
        record_heartbeat("bogus", path=tmp_path / "hb.json")


def test_heartbeat_missing_file_is_stale(tmp_path: Path):
    view = heartbeat_view("blog", path=tmp_path / "nope.json")
    assert view["last_run_at"] is None
    assert view["stale"] is True
    assert view["run_count"] == 0


def test_heartbeat_old_record_is_stale(tmp_path: Path):
    p = tmp_path / "hb.json"
    old = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    p.write_text(json.dumps({"tt": {"role": "tt", "last_run_at": old, "run_count": 3}}))
    view = heartbeat_view("tt", path=p)
    assert view["stale"] is True
    assert view["run_count"] == 3
    assert view["age_days"] >= 10


def test_dispatch_records_auto_heartbeat(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """D1 regression: manual-only heartbeat would be a dead mechanism."""
    p = tmp_path / "hb.json"
    monkeypatch.setenv("DEMAND_OS_AGENTS_HEARTBEAT", str(p))
    from agent.demand_os.agents.registry import dispatch

    out = dispatch("validator", action="compliance")
    assert out["ok"] is True
    hb = load_heartbeats(path=p)
    assert hb["validator"]["last_action"] == "compliance"
    assert hb["validator"]["run_count"] == 1
    # failed dispatch must NOT record (honest: run did not succeed)
    out2 = dispatch("validator", action="bogus")
    assert out2["ok"] is False
    assert load_heartbeats(path=p)["validator"]["run_count"] == 1
    # unknown role must NOT record
    dispatch("bogus", action="status")
    assert "bogus" not in load_heartbeats(path=p)


def test_default_path_env_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    from agent.demand_os.agents.heartbeat import default_heartbeat_path

    monkeypatch.setenv("DEMAND_OS_AGENTS_HEARTBEAT", str(tmp_path / "custom.json"))
    assert default_heartbeat_path() == tmp_path / "custom.json"
    monkeypatch.delenv("DEMAND_OS_AGENTS_HEARTBEAT")
    # repo set-now is writable locally → default lands there (prod falls back to data/)
    p = default_heartbeat_path()
    assert p.name == "AGENTS-HEARTBEAT.json"


def test_list_agents_includes_heartbeat(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    p = tmp_path / "hb.json"
    monkeypatch.setenv("DEMAND_OS_AGENTS_HEARTBEAT", str(p))
    record_heartbeat("growth_lead", action="money_check", path=p)
    rows = {r["role"]: r for r in list_agents()}
    hb = rows["growth_lead"]["heartbeat"]
    assert hb["run_count"] == 1
    assert hb["last_action"] == "money_check"
    assert hb["stale"] is False
    assert rows["cf"]["heartbeat"]["stale"] is True  # never ran


def test_hub_heartbeat_cli(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("DEMAND_OS_AGENTS_HEARTBEAT", str(tmp_path / "hb.json"))
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "demand_os_hub.py"),
            "agents",
            "heartbeat",
            "--role",
            "blog",
            "--action",
            "pipeline",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        env={**__import__("os").environ, "DEMAND_OS_AGENTS_HEARTBEAT": str(tmp_path / "hb.json")},
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["heartbeat"]["role"] == "blog"
    assert payload["heartbeat"]["last_action"] == "pipeline"
