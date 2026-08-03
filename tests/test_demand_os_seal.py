"""DEMAND-OS-PROGRAM-SEAL — doctor + commander status payload."""

from __future__ import annotations

import csv
from pathlib import Path

from agent.demand_os.commander_status import build_demand_os_status
from agent.demand_os.doctor import _state_marketing_pair, _tip_ok, run_doctor


def test_doctor_pass_on_repo():
    report = run_doctor()
    assert report.ok is True, report.errors
    assert report.marketing in {"HITL_LIVE", "PARKED_LAST"}
    tip = next(c for c in report.checks if c["name"].endswith("STATE.md"))
    assert tip["ok"] is True
    assert tip["detail"] in {"TOOL_FIRST/PARKED", "HITL_LIVE/READY", "PARKED_LAST/BLOCKED"}
    names = {c["name"] for c in report.checks}
    assert "phase0" in names
    assert "money_check" in names
    assert "calendar_sot_json" in names


def test_doctor_fails_when_tip_missing_parked(tmp_path: Path, monkeypatch):
    # Minimal fake repo missing semantic marketing tip
    (tmp_path / "tools").mkdir()
    (tmp_path / "agent" / "demand_os" / "connectors").mkdir(parents=True)
    (tmp_path / "docs" / "ops" / "demand-os").mkdir(parents=True)
    (tmp_path / "docs" / "ops" / "marketing").mkdir(parents=True)
    # phase0 missing → fail
    (tmp_path / "agent/demand_os/connectors/transport.py").write_text(
        "class LiveTikTokTransport:\n    pass\n", encoding="utf-8"
    )
    report = run_doctor(root=tmp_path)
    assert report.ok is False
    assert report.errors


def test_doctor_tip_semantics_pre_go():
    text = """
    | marketing_hitl | **PARKED_LAST** · gate **BLOCKED** |
    TOOL-INTEGRITY-SEAL
    """
    assert _state_marketing_pair(text) == ("PARKED_LAST", "BLOCKED")
    assert _tip_ok(rel="docs/ops/demand-os/STATE.md", text=text) == (
        True,
        "PARKED_LAST/BLOCKED",
    )


def test_doctor_tip_semantics_post_go():
    text = """
    | marketing_hitl | **HITL_LIVE** · gate **READY** |
    TOOL-INTEGRITY-SEAL
    """
    assert _state_marketing_pair(text) == ("HITL_LIVE", "READY")
    assert _tip_ok(rel="docs/ops/demand-os/STATE.md", text=text) == (
        True,
        "HITL_LIVE/READY",
    )


def test_doctor_tip_semantics_tool_first():
    text = """
    status: "[ETAP 4 · TOOL 100% FIRST · live P0 PARKED]"
    | active_item | **TOOL 100%** · live `4-P0-*` PARKED |
    | marketing_hitl | env GO possible · **live publish cadence PARKED** |
    """
    assert _tip_ok(rel="docs/ops/demand-os/STATE.md", text=text) == (
        True,
        "TOOL_FIRST/PARKED",
    )
    assert _state_marketing_pair(text) == ("HITL_LIVE", "PARKED")


def test_doctor_tip_semantics_reject_mismatch():
    text = """
    | marketing_hitl | **HITL_LIVE** · gate **BLOCKED** |
    TOOL-INTEGRITY-SEAL
    """
    assert _state_marketing_pair(text) is None
    assert _tip_ok(rel="docs/ops/demand-os/STATE.md", text=text) == (
        False,
        "state tip mismatch",
    )


def test_commander_status_payload_shape(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("DEMAND_OS_MARKETING_HITL", raising=False)
    (tmp_path / "LEDGER.csv").write_text(
        "date,channel,icp_role,asset_id,utm_link,publish_Y/N,comments_sent,"
        "hot_leads,wizard_starts,paid,notes\n",
        encoding="utf-8",
    )
    with (tmp_path / "VALIDATOR-LOG.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["asset_id", "decision"])
        w.writeheader()
        w.writerow({"asset_id": "a", "decision": "PASS"})
    payload = build_demand_os_status(set_now=tmp_path)
    assert payload["ok"] is True
    assert payload["marketing"] == "PARKED_LAST"
    assert "wizard_starts_utm" in payload["kpi"]
    assert "screen" in payload
    assert "money_check" in payload
    assert payload["footer"]["doctor_scope"] == "lightweight"
    assert payload["footer"]["doctor_ok"] is False
