"""DEMAND-OS-PROGRAM-SEAL — doctor + commander status payload."""

from __future__ import annotations

import csv
from pathlib import Path

from agent.demand_os.commander_status import build_demand_os_status
from agent.demand_os.doctor import run_doctor


def test_doctor_pass_on_repo():
    report = run_doctor()
    assert report.marketing == "PARKED_LAST"
    assert report.ok is True, report.errors
    names = {c["name"] for c in report.checks}
    assert "phase0" in names
    assert "money_check" in names
    assert "calendar_sot_json" in names


def test_doctor_fails_when_tip_missing_parked(tmp_path: Path, monkeypatch):
    # Minimal fake repo missing tip PARKED_LAST
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


def test_commander_status_payload_shape(tmp_path: Path):
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
