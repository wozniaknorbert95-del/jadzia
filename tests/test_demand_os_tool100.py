"""TOOL-100 — week ritual · STL · ledger · CF/FB · design · go-ready."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent.demand_os.agents.wave2 import run_wave2
from agent.demand_os.audit_log import append_audit, list_audit
from agent.demand_os.content_factory import build_brief, proof_check
from agent.demand_os.design_wizard import check_design_lead
from agent.demand_os.ledger import ensure_today_row, ledger_summary
from agent.demand_os.stl_monitor import stl_report
from agent.demand_os.utm_lock import build_wizard_utm
from agent.demand_os.week_ritual import go_day_ready, week_plan


def test_ledger_summary():
    s = ledger_summary()
    assert s["ok"] is True
    assert "rows" in s


def test_ensure_today_dry(tmp_path: Path):
    # copy empty-ish: write minimal ledger
    led = tmp_path / "L.csv"
    led.write_text(
        "date,channel,icp_role,asset_id,utm_link,publish_Y/N,comments_sent,"
        "hot_leads,wizard_starts,paid,notes\n",
        encoding="utf-8",
    )
    out = ensure_today_row(path=led, dry_run=True, asset_id="t_hy")
    assert out["ok"] is True
    assert out["dry_run"] is True


def test_stl_report_shape():
    r = stl_report()
    assert r["ok"] is True
    assert "open_hot" in r
    assert r["sla_min"] == 15


def test_week_and_go_ready(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("DEMAND_OS_MARKETING_HITL", raising=False)
    w = week_plan(day="pon")
    assert w["ok"] is True
    assert w["day"] == "pon"
    assert w["marketing"] == "PARKED_LAST"
    assert w["marketing_hitl_gate"] == "BLOCKED"
    g = go_day_ready()
    assert "score" in g
    assert g["marketing"] == "PARKED_LAST"
    assert g["marketing_hitl_gate"] == "BLOCKED"


def test_week_and_go_ready_go_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DEMAND_OS_MARKETING_HITL", "GO")
    w = week_plan(day="sr")
    assert w["marketing"] == "HITL_LIVE"
    assert w["marketing_hitl_gate"] == "READY"
    assert w["job"]["live"] == "READY after Validator PASS + HITL approval"
    g = go_day_ready()
    assert g["marketing"] == "HITL_LIVE"
    assert g["marketing_hitl_gate"] == "READY"


def test_cf_brief_and_proof():
    b = build_brief(channel="tiktok", asset_id="tt_t100_01")
    assert b["ok"] is True
    assert "utm_link" in b["brief"]
    assert proof_check("VHQ dashboard hero")["ok"] is False
    assert proof_check("bus before after")["ok"] is True


def test_wave2_shells(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("DEMAND_OS_MARKETING_HITL", raising=False)
    cf = run_wave2("cf", action="brief")
    assert cf["role"] == "cf"
    assert cf["marketing"] == "PARKED_LAST"
    fb = run_wave2("fb")
    assert fb["role"] == "fb"
    assert fb["result"]["live_comment"] is False
    monkeypatch.setenv("DEMAND_OS_MARKETING_HITL", "GO")
    cf_go = run_wave2("cf", action="brief")
    assert cf_go["marketing"] == "HITL_LIVE"
    assert run_wave2("fb")["result"]["live_comment"] is False


def test_design_wizard_rules():
    bad = check_design_lead(message="Hier is je offerte zonder link")
    assert bad["ok"] is False
    utm = build_wizard_utm("whatsapp", "installateur", "da_1")
    good = check_design_lead(
        message="Mockup klaar — start wizard",
        wizard_url=utm,
    )
    assert good["ok"] is True


def test_audit_log(tmp_path: Path):
    p = tmp_path / "a.jsonl"
    rec = append_audit("test_action", actor="pytest", path=p)
    assert rec["action"] == "test_action"
    listed = list_audit(path=p)
    assert listed["count"] == 1


def test_wave3_and_commander(monkeypatch: pytest.MonkeyPatch):
    from agent.demand_os.agents.wave3 import run_wave3
    from agent.demand_os.commander_status import build_demand_os_status

    monkeypatch.delenv("DEMAND_OS_MARKETING_HITL", raising=False)
    blog = run_wave3("blog")
    assert blog["role"] == "blog"
    assert blog["result"]["live_ship"] is False
    cre = run_wave3("cre")
    assert cre["role"] == "cre"
    st = build_demand_os_status()
    assert st["gate"] == "DEMAND-OS-DESK-CONTRACT-00"
    assert st["desk"] == "Demand Desk v2.1"
    assert "go_ready" not in st
    assert st["diagnostics"]["go_ready"]["score"] == 100.0
    assert st["diagnostics"]["marketing_hitl_gate"] == "BLOCKED"
    assert st["marketing"] == "PARKED_LAST"
    assert "median_min" in st["stl"]
    assert "robota_dnia" in st
    assert isinstance(st["footer"]["doctor_ok"], bool)


def test_da_deeplink_utm_lock():
    from agent.inspire.reco import build_wizard_deeplink
    from agent.demand_os.utm_lock import validate_utm_url

    url = build_wizard_deeplink("caddy", "MA-005")
    check = validate_utm_url(url)
    assert check["ok"] is True
    assert check["parts"]["channel"] == "design_agent"
    assert "voertuig=caddy" in url


def test_paid_sync_dry(tmp_path: Path):
    from unittest.mock import patch

    from agent.demand_os.db_utm import sync_paid_from_ops_bus
    from agent.demand_os.utm_lock import build_wizard_utm

    utm = build_wizard_utm("tiktok", "installateur", "ord_1")
    rows = [{"event_id": "o1", "payload": {"utm_link": utm, "asset_id": "ord_1"}}]
    import agent.db as dbmod

    with patch.object(dbmod, "db_ops_bus_list", return_value=rows):
        out = sync_paid_from_ops_bus(dry_run=True, events_path=tmp_path / "e.jsonl")
    assert out["ok"] is True
    assert out["synced"] == 1
