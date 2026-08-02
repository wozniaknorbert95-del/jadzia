"""Demand OS Hub — observability · A2A · memory (OS TARGET §E/F/G/M)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from agent.demand_os.a2a_bus import ack_handoff, emit_handoff, list_handoffs
from agent.demand_os.memory import load_memory, set_semantic_icp, sync_episodic_from_ledger
from agent.demand_os.observability import build_screen, money_check


def _write_ledger(path: Path) -> None:
    cols = [
        "date",
        "channel",
        "icp_role",
        "asset_id",
        "utm_link",
        "publish_Y/N",
        "comments_sent",
        "hot_leads",
        "wizard_starts",
        "paid",
        "notes",
    ]
    rows = [
        {
            "date": "2026-08-01",
            "channel": "tiktok",
            "icp_role": "installateur",
            "asset_id": "tt_w32_install_01",
            "utm_link": (
                "https://zzpackage.flexgrafik.nl/wizard/"
                "?utm_source=tiktok&utm_medium=organic"
                "&utm_campaign=icp_installateur&utm_content=tt_w32_install_01"
            ),
            "publish_Y/N": "Y",
            "comments_sent": "2",
            "hot_leads": "0",
            "wizard_starts": "3",
            "paid": "1",
            "notes": "hook witte bus",
        },
        {
            "date": "2026-08-01",
            "channel": "facebook",
            "icp_role": "installateur",
            "asset_id": "fb_hunt_w32_d2",
            "utm_link": (
                "https://zzpackage.flexgrafik.nl/wizard/"
                "?utm_source=facebook&utm_medium=organic"
                "&utm_campaign=icp_installateur&utm_content=fb_hunt_w32_d2"
            ),
            "publish_Y/N": "N",
            "comments_sent": "1",
            "hot_leads": "0",
            "wizard_starts": "1",
            "paid": "0",
            "notes": "",
        },
    ]
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def _write_validator(path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["asset_id", "decision"])
        w.writeheader()
        w.writerow({"asset_id": "a", "decision": "PASS"})
        w.writerow({"asset_id": "b", "decision": "FAIL"})


def test_observability_screen(tmp_path: Path):
    _write_ledger(tmp_path / "LEDGER.csv")
    _write_validator(tmp_path / "VALIDATOR-LOG.csv")
    (tmp_path / "CONTENT-CALENDAR.json").write_text(
        json.dumps(
            {
                "week": "2026-W32",
                "slots": [
                    {
                        "asset_id": "tt_w32_install_01",
                        "channel": "tiktok",
                        "status": "validated",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    screen = build_screen(set_now=tmp_path)
    assert screen.publish_count == 1
    assert screen.comments_sent == 3
    assert screen.validator_fail == 1
    assert screen.validator_pass == 1
    assert screen.paid_total == 1
    assert sum(screen.wizard_starts_by_utm.values()) == 4
    assert screen.top_hook == "tt_w32_install_01"
    assert screen.hitl_queue[0]["action"] == "HITL_PUBLISH"


def test_money_check(tmp_path: Path):
    _write_ledger(tmp_path / "LEDGER.csv")
    _write_validator(tmp_path / "VALIDATOR-LOG.csv")
    mc = money_check(set_now=tmp_path)
    assert mc["starts_utm"] == 4
    assert mc["paid"] == 1
    assert mc["top_hook"] == "tt_w32_install_01"
    assert mc["kill_vanity"] is True
    assert mc["sniper_compliance"] == 0.5


def test_a2a_emit_ack(tmp_path: Path):
    bus = tmp_path / "A2A.jsonl"
    rec = emit_handoff(
        "lead_hot",
        asset_id="wa_test",
        payload={"wizard": True},
        path=bus,
    )
    assert rec["to_agent"] == "CRE_Wizard"
    assert rec["sla_minutes"] == 15
    acked = ack_handoff(rec["id"], path=bus)
    assert acked["status"] == "acked"
    assert acked["sla_ok"] is True
    listed = list_handoffs(path=bus, handoff_type="lead_hot")
    assert len(listed) == 1


def test_a2a_rejects_unknown():
    import pytest

    with pytest.raises(ValueError):
        emit_handoff("vanity_dashboard")


def test_memory_layers(tmp_path: Path):
    _write_ledger(tmp_path / "LEDGER.csv")
    mem = tmp_path / "MEMORY.json"
    store = set_semantic_icp(
        "installateur",
        "witte bus",
        memory_path=mem,
    )
    assert store["semantic"]["icp_role_week"] == "installateur"
    synced = sync_episodic_from_ledger(
        set_now=tmp_path,
        memory_path=mem,
        weekly_improvement="new angle 50m",
    )
    assert synced["episodic"]["top_hook_asset_id"] == "tt_w32_install_01"
    assert synced["episodic"]["weekly_improvement"] == "new angle 50m"
    loaded = load_memory(path=mem)
    assert loaded["procedural"]["validator_rules"] == "C.5 R1-R8"
    assert "playbook" in loaded["procedural"]
