"""TARGET v5 §E hub-spoke flow + §J wave readiness — honest tool/human split."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from agent.demand_os.agents.flow import run_hub_spoke_flow
from agent.demand_os.agents.wave_check import WAVE_PASS_LIVE, wave_readiness

ROOT = Path(__file__).resolve().parents[2]


def test_flow_chain_dry_run_ok(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("DEMAND_OS_MARKETING_HITL", raising=False)
    out = run_hub_spoke_flow(icp_role="installateur", channel="tiktok")
    assert out["ok"] is True
    assert out["steps"]["icp_brief"]["ok"] is True
    assert out["steps"]["cf_brief"]["ok"] is True
    assert out["steps"]["validator"]["ok"] is True
    assert out["steps"]["publish_request"]["status"] == "dry_run"
    assert out["steps"]["publish_request"]["publish_allowed"] is False
    assert "PARKED" in out["steps"]["publish_request"]["blocked_reason"]
    assert out["live_publish"] is False
    assert out["dry_run"] is True
    assert out["request"]["icp_role"] == "installateur"
    assert "utm_source=tiktok" in out["request"]["utm_link"]


def test_flow_validator_fail_blocks_chain():
    # hero HQ + multi-CTA caption must fail C.5 rules and stop before handoff
    out = run_hub_spoke_flow(
        icp_role="installateur",
        caption="VHQ dashboard hero — like, comment, share, follow, buy!",
    )
    assert out["ok"] is False
    assert out["error"] == "validator_fail"
    assert "publish_request" not in out["steps"]
    assert out["live_publish"] is False


def test_flow_apply_emits_a2a_handoff(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("DEMAND_OS_A2A_BUS", str(tmp_path / "bus.jsonl"))
    out = run_hub_spoke_flow(dry_run=False)
    assert out["ok"] is True
    handoff = out["steps"]["publish_request"]
    assert handoff["status"] == "emitted"
    assert handoff["a2a_id"]
    assert handoff["sla_minutes"] == 5
    assert handoff["publish_allowed"] is False  # PARKED — emitted ≠ live
    bus = (tmp_path / "bus.jsonl").read_text(encoding="utf-8")
    assert "publish_request" in bus
    assert "Sniper_Validator" in bus


def test_flow_live_mode_marks_publish_allowed(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DEMAND_OS_MARKETING_HITL", "GO")
    out = run_hub_spoke_flow()
    assert out["steps"]["publish_request"]["publish_allowed"] is True
    assert out["steps"]["publish_request"]["blocked_reason"] == ""
    assert out["live_publish"] is False  # flow never publishes regardless


def test_wave_readiness_shape_and_split(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("DEMAND_OS_MARKETING_HITL", raising=False)
    out = wave_readiness()
    assert out["marketing"] == "PARKED_LAST"
    assert [w["wave"] for w in out["waves"]] == [1, 2, 3, 4]
    for wave in out["waves"]:
        assert wave["tool_checks"], f"wave {wave['wave']} must have tool checks"
        assert wave["overall"] in ("tool_ready", "waiting")
        assert wave["live_pass"] is False
        assert wave["live_pass_criteria"] == WAVE_PASS_LIVE[wave["wave"]]
        assert "PARKED" in wave["live_blocked_reason"]
    # tool side must be green after registry closeout
    assert out["ok"] is True
    assert all(w["overall"] == "tool_ready" for w in out["waves"])


def test_wave_readiness_go_clears_block_reason(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DEMAND_OS_MARKETING_HITL", "GO")
    out = wave_readiness()
    for wave in out["waves"]:
        assert wave["live_blocked_reason"] == ""
        assert wave["live_pass"] is False  # still human cadence — never auto-PASS


def _run_hub(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / "tools" / "demand_os_hub.py"), *argv],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_hub_agents_flow_cli_dry():
    proc = _run_hub("agents", "flow", "--icp-role", "hovenier", "--channel", "facebook")
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["request"]["icp_role"] == "hovenier"
    assert payload["steps"]["publish_request"]["status"] == "dry_run"


def test_hub_agents_wave_check_cli():
    proc = _run_hub("agents", "wave-check")
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert len(payload["waves"]) == 4
