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


def test_probe_dispatch_never_records_heartbeat(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """D9-01 regression: observability probes must not touch heartbeat —
    otherwise staleness measures its own measurement and can never go red."""
    p = tmp_path / "hb.json"
    monkeypatch.setenv("DEMAND_OS_AGENTS_HEARTBEAT", str(p))
    from agent.demand_os.agents.registry import dispatch

    out = dispatch("validator", action="compliance", probe=True)
    assert out["ok"] is True
    assert load_heartbeats(path=p) == {}, "probe must not record heartbeat"
    # sanity: non-probe still records
    dispatch("validator", action="compliance")
    assert load_heartbeats(path=p)["validator"]["run_count"] == 1


def test_wave_check_does_not_refresh_heartbeats(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """D9-01 regression: wave_readiness must leave heartbeat file untouched."""
    from datetime import datetime, timedelta, timezone

    p = tmp_path / "hb.json"
    monkeypatch.setenv("DEMAND_OS_AGENTS_HEARTBEAT", str(p))
    old = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    p.write_text(
        json.dumps({"sales": {"role": "sales", "last_run_at": old, "last_action": "list_hot", "run_count": 7}}),
        encoding="utf-8",
    )
    before = p.read_text(encoding="utf-8")
    from agent.demand_os.agents.wave_check import wave_readiness

    out = wave_readiness()
    assert p.read_text(encoding="utf-8") == before, "wave-check must not write heartbeats"
    # and with 30d-old heartbeat the staleness check must be RED (sales limit 12h)
    wave1 = next(w for w in out["waves"] if w["wave"] == 1)
    stale = next(c for c in wave1["tool_checks"] if c["check"] == "heartbeat_staleness")
    assert stale["ok"] is False
    assert "sales" in stale["detail"]


def test_default_path_env_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    from agent.demand_os.agents.heartbeat import default_heartbeat_path

    monkeypatch.setenv("DEMAND_OS_AGENTS_HEARTBEAT", str(tmp_path / "custom.json"))
    assert default_heartbeat_path() == tmp_path / "custom.json"
    monkeypatch.delenv("DEMAND_OS_AGENTS_HEARTBEAT")
    # repo set-now is writable locally → default lands there (prod falls back to data/)
    p = default_heartbeat_path()
    assert p.name == "AGENTS-HEARTBEAT.json"


def test_desk_chip_uses_per_role_limits(tmp_path: Path):
    """S10/9-02: desk chip must honor per-role limits, not global STALE_DAYS=7.

    sales (12h limit) at 24h is stale even though 24h < 7d; growth_lead (48h)
    at 24h is still fresh. Non-cadence roles keep the 7d default.
    """
    p = tmp_path / "hb.json"
    day_ago = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    p.write_text(
        json.dumps(
            {
                "sales": {"role": "sales", "last_run_at": day_ago, "run_count": 5},
                "growth_lead": {"role": "growth_lead", "last_run_at": day_ago, "run_count": 5},
            }
        ),
        encoding="utf-8",
    )
    sales = heartbeat_view("sales", path=p)
    assert sales["stale"] is True, "24h > 12h limit for sales"
    assert sales["stale_limit_h"] == 12.0
    growth = heartbeat_view("growth_lead", path=p)
    assert growth["stale"] is False, "24h < 48h limit for growth_lead"
    assert growth["stale_limit_h"] == 48.0
    # non-cadence role keeps the 7d default
    assert heartbeat_view("blog", path=p)["stale_limit_h"] == 168.0


def test_desk_chip_matches_wave_staleness(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """S10/9-02 contract: chip `stale` on desk == wave-check verdict, same file."""
    p = tmp_path / "hb.json"
    monkeypatch.setenv("DEMAND_OS_AGENTS_HEARTBEAT", str(p))
    now = datetime.now(timezone.utc)
    beats = {
        role: {"role": role, "last_run_at": (now - timedelta(hours=age)).isoformat(), "run_count": 1}
        for role, age in {
            "growth_lead": 5,   # fresh (<48h)
            "sales": 24,        # stale (>12h)
            "validator": 5,     # fresh (<48h)
            "icp_brain": 5,     # fresh (<48h)
            "cre": 5,           # fresh (<48h)
        }.items()
    }
    p.write_text(json.dumps(beats), encoding="utf-8")
    from agent.demand_os.agents.wave_check import wave_readiness

    out = wave_readiness()
    wave1 = next(w for w in out["waves"] if w["wave"] == 1)
    check = next(c for c in wave1["tool_checks"] if c["check"] == "heartbeat_staleness")
    assert check["ok"] is False and "sales" in check["detail"]
    for role, expect_stale in {"sales": True, "growth_lead": False, "validator": False}.items():
        assert heartbeat_view(role)["stale"] is expect_stale, role
    # wave says only sales stale → chip must agree for every cadence role
    for role in ("growth_lead", "validator", "icp_brain", "cre"):
        assert heartbeat_view(role)["stale"] is False, role


def test_stale_limit_env_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """DEMAND_OS_HB_STALE_<ROLE> overrides both desk chip and wave-check."""
    p = tmp_path / "hb.json"
    two_hours = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    p.write_text(
        json.dumps({"sales": {"role": "sales", "last_run_at": two_hours, "run_count": 1}}),
        encoding="utf-8",
    )
    assert heartbeat_view("sales", path=p)["stale"] is False  # 2h < 12h default
    monkeypatch.setenv("DEMAND_OS_HB_STALE_SALES", "1")
    assert heartbeat_view("sales", path=p)["stale"] is True  # 2h > 1h override


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
