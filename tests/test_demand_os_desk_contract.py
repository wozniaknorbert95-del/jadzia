"""Desk v2.1.1 contract — status payload fields for Biuro Popytu."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from agent.demand_os.commander_status import build_demand_os_status
from agent.demand_os.desk_contract import (
    CONTRACT_TOP_KEYS,
    CONTRACT_VERSION,
    ROBOTA,
    detect_data_mode,
    resolve_robota_dnia,
    starts_wow_delta,
    validator_fail_display,
)


def test_robota_parked_stop_on_live_days():
    r = resolve_robota_dnia(marketing="PARKED_LAST", day="sr")
    assert r["code"] == "PARKED_STOP"
    assert r["code"] in ROBOTA
    r2 = resolve_robota_dnia(marketing="PARKED_LAST", day="pon")
    assert r2["code"] == "MONEY_CHECK"


def test_validator_na_when_zero_publish():
    assert validator_fail_display(publish_count=0, validator_fail=3) == "n/a"
    assert validator_fail_display(publish_count=2, validator_fail=1) == 1


def test_wow_delta_frozen_today():
    today = date(2026, 7, 31)  # Friday
    rows = [
        {"date": "2026-07-20", "wizard_starts": "5"},  # prev week
        {"date": "2026-07-28", "wizard_starts": "2"},  # this week
    ]
    assert starts_wow_delta(rows, today=today) == 2 - 5


def test_data_mode_fixture_no_fake_real(tmp_path: Path):
    led = tmp_path / "LEDGER.csv"
    led.write_text(
        "date,channel,icp_role,asset_id,utm_link,publish_Y/N,comments_sent,"
        "hot_leads,wizard_starts,paid,notes\n"
        "2026-07-30,tiktok,installateur,a1,https://x?utm_content=a1,Y,0,0,2,0,fixture sample\n",
        encoding="utf-8",
    )
    (tmp_path / "GROWTH-EVENTS.jsonl").write_text("", encoding="utf-8")
    dm = detect_data_mode(set_now=tmp_path)
    assert dm["data_mode"] == "FIXTURE"
    assert dm["last_real_event"]["ts"] == ""
    assert dm["real_hits"] == 0


def test_dual_cash_baseline_pass_not_fail():
    from agent.demand_os.desk_contract import dual_cash_report

    # uses repo set-now DA-AUDIT-LOG — baseline PASS with "0 FAIL" in notes
    r = dual_cash_report()
    assert r["open_fail"] == 0
    assert r["red"] is False


def test_commander_desk_v21_shape(tmp_path: Path):
    led = tmp_path / "LEDGER.csv"
    led.write_text(
        "date,channel,icp_role,asset_id,utm_link,publish_Y/N,comments_sent,"
        "hot_leads,wizard_starts,paid,notes\n",
        encoding="utf-8",
    )
    (tmp_path / "VALIDATOR-LOG.csv").write_text(
        "asset_id,decision,fail_rules\n", encoding="utf-8"
    )
    (tmp_path / "CONTENT-CALENDAR.json").write_text(
        '{"week":"2026-W31","slots":[{"date":"2026-07-30","channel":"tiktok",'
        '"asset_id":"tt_x","status":"validated"}]}',
        encoding="utf-8",
    )
    (tmp_path / "ALLOWLIST.json").write_text(
        '{"max_groups":5,"targets":[{"id":"g1","platform":"facebook",'
        '"kind":"group_nl","name":"ZZP NL","external_id":"1","status":"active"}]}',
        encoding="utf-8",
    )
    (tmp_path / "DA-AUDIT-LOG.csv").write_text(
        "date,lead_id,source,t_lead_iso,t_wizard_push_iso,delta_h,wizard_pushed,"
        "offerte_only,verdict,notes\n"
        "2026-08-01,baseline,design_agent,,,,,N,N,PASS,0 FAIL\n",
        encoding="utf-8",
    )
    (tmp_path / "GROWTH-EVENTS.jsonl").write_text("", encoding="utf-8")
    (tmp_path / "ENGAGE-LOG.jsonl").write_text(
        json.dumps(
            {
                "target_id": "g1",
                "action": "comment",
                "ok": False,
                "notes": "anti_spam",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    st = build_demand_os_status(set_now=tmp_path)
    assert st["desk"] == "Demand Desk v2.1"
    assert st["contract_version"] == CONTRACT_VERSION
    assert st["gate"] == "DEMAND-OS-DESK-CONTRACT-00"
    assert CONTRACT_TOP_KEYS.issubset(set(st.keys()))
    assert "go_ready" not in st
    assert st["diagnostics"]["marketing_hitl_gate"] == "BLOCKED"
    assert st["robota_dnia"]["code"] in ROBOTA
    assert st["icp_role_week"]
    assert st["state"] == "PARKED"
    assert len(st["week_calendar"]) == 5
    assert isinstance(st["shells_line"], str)
    assert isinstance(st["screen"]["hunt_queue"], list)
    assert st["screen"]["hunt_queue"][0]["desk_status"] == "BLOCK"
    assert st["screen"]["hitl_queue"][0]["desk_action"] == "GOTOWY"
    assert st["kpi"]["validator_fail"] == "n/a"
    assert isinstance(st["footer"]["doctor_ok"], bool)
    assert st["footer"]["stale_warn"] is True or st["data_mode"] == "EMPTY"


def test_golden_fixture_keys():
    fixture = (
        Path(__file__).resolve().parent / "fixtures" / "desk_status_v21.min.json"
    )
    golden = json.loads(fixture.read_text(encoding="utf-8"))
    st = build_demand_os_status()
    for k in CONTRACT_TOP_KEYS:
        assert k in golden, k
        assert k in st, k
    assert "go_ready" not in golden


def test_hub_status_parity_keys():
    """CLI builder == API builder (same function)."""
    st = build_demand_os_status()
    assert st["desk"] == "Demand Desk v2.1"
    assert "robota_dnia" in st
    assert "week_calendar" in st


def test_hitl_decision_dry(tmp_path: Path):
    from agent.demand_os.hitl_decision import record_hitl_decision

    cal = tmp_path / "CONTENT-CALENDAR.json"
    cal.write_text(
        json.dumps(
            {
                "week": "2026-W31",
                "slots": [
                    {
                        "date": "2026-07-30",
                        "channel": "tiktok",
                        "asset_id": "tt_hitl",
                        "status": "planned",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    out = record_hitl_decision("tt_hitl", "GOTOWY", calendar_path=cal)
    assert out["ok"] is True
    assert out["publish"] is False
    assert out["calendar_status"] == "validated"
    out2 = record_hitl_decision("tt_hitl", "BLOKADA", calendar_path=cal)
    assert out2["calendar_status"] == "blocked"
