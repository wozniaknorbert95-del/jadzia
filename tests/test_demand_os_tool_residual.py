"""Demand OS TOOL residual — starts ingest · gate · calendar SoT · MCP · TT · A2A auto."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent.demand_os.content_calendar import (
    DEFAULT_CALENDAR_PATH,
    CalendarSlot,
    ContentCalendar,
    save_calendar,
)
from agent.demand_os.connectors.transport import (
    LiveTikTokTransport,
    MockTransport,
    get_transport,
)
from agent.demand_os.ga4_adapter import fetch_wizard_starts_stub
from agent.demand_os.gdrive_cf import list_cf_assets_stub
from agent.demand_os.observability import money_check
from agent.demand_os.publish_gate_bridge import (
    check_publish_allowed,
    gated_publish_calendar_content,
)
from agent.demand_os.publish_request import PublishRequest
from agent.demand_os.starts_ingest import (
    ingest_fixture_csv,
    ingest_row,
    write_sample_fixture,
)
from agent.demand_os.utm_lock import build_wizard_utm
from agent.demand_os.validator import evaluate_publish_request
from agent.demand_os.weekly_tune import weekly_success_report
from agent.demand_os.widget_leads import emit_hot_lead, list_hot_leads_stub


UTM_TT = build_wizard_utm("tiktok", "installateur", "tt_w32_install_01")


def test_ingest_fixture_and_money_check(tmp_path: Path, monkeypatch):
    events = tmp_path / "GROWTH-EVENTS.jsonl"
    fixture = tmp_path / "starts.csv"
    write_sample_fixture(fixture)
    monkeypatch.setenv("DEMAND_OS_GROWTH_EVENTS", str(events))
    result = ingest_fixture_csv(fixture, events_path=events)
    assert result["ok"] is True
    assert result["rows_ok"] == 3
    # empty ledger dir for set_now
    (tmp_path / "LEDGER.csv").write_text(
        "date,channel,icp_role,asset_id,utm_link,publish_Y/N,comments_sent,"
        "hot_leads,wizard_starts,paid,notes\n",
        encoding="utf-8",
    )
    (tmp_path / "VALIDATOR-LOG.csv").write_text(
        "asset_id,decision\na,PASS\n", encoding="utf-8"
    )
    mc = money_check(set_now=tmp_path, events_path=events)
    assert mc["starts_utm"] >= 3
    assert mc["paid"] >= 1
    assert "tt_w32_install_01" in (mc.get("top_hook") or "")


def test_ingest_rejects_bad_utm():
    with pytest.raises(ValueError):
        ingest_row(utm_link="https://zzpackage.flexgrafik.nl/wizard/")


def test_ingest_paid_optional(tmp_path: Path, monkeypatch):
    events = tmp_path / "e.jsonl"
    monkeypatch.setenv("DEMAND_OS_GROWTH_EVENTS", str(events))
    rec = ingest_row(utm_link=UTM_TT, event_type="paid", events_path=events)
    assert rec["ok"] is True


def test_publish_gate_deny_allow(tmp_path: Path):
    cal_path = tmp_path / "CONTENT-CALENDAR.json"
    cal = ContentCalendar(week="2026-W32", slots=[])
    save_calendar(cal, cal_path)
    deny = check_publish_allowed("missing_asset", calendar_path=cal_path)
    assert deny.allowed is False
    cal = ContentCalendar(
        week="2026-W32",
        slots=[
            CalendarSlot(
                date="2026-08-01",
                channel="tiktok",
                asset_id="tt_gate_01",
                status="validated",
                pass_token="val_testtoken1234567890",
            )
        ],
    )
    save_calendar(cal, cal_path)
    allow = check_publish_allowed("tt_gate_01", calendar_path=cal_path)
    assert allow.allowed is True
    dry = gated_publish_calendar_content(
        {"asset_id": "tt_gate_01", "platform": "tiktok", "content_type": "video"},
        calendar_path=cal_path,
        dry_run=True,
    )
    assert dry["status"] == "ok"
    assert dry["dry_run"] is True


def test_calendar_sot_is_json_not_sqlite():
    assert DEFAULT_CALENDAR_PATH.name == "CONTENT-CALENDAR.json"
    assert "sqlite" not in str(DEFAULT_CALENDAR_PATH).lower()
    assert Path("docs/ops/demand-os/CALENDAR-SOT.md").is_file()


def test_mcp_adapters_fail_closed():
    ga4 = fetch_wizard_starts_stub()
    assert ga4["ok"] is False
    assert ga4["mode"] == "stub"
    gd = list_cf_assets_stub()
    # Default = local ASSET-REGISTRY (honest CF), not hollow live_empty
    assert gd["mode"] in ("local_registry", "missing_registry", "stub", "not_wired")
    if gd["mode"] == "local_registry":
        assert gd["ok"] is True
    leads = list_hot_leads_stub()
    # DB present → jadzia.db; unavailable → stub. Never invent hot leads.
    assert leads["mode"] in ("stub", "jadzia.db")
    assert "leads" in leads
    if leads["mode"] == "jadzia.db":
        assert leads["ok"] is True


def test_widget_emit_lead(tmp_path: Path):
    bus = tmp_path / "a2a.jsonl"
    rec = emit_hot_lead(lead_id="L1", wizard_url=UTM_TT, bus_path=bus)
    assert rec["handoff_type"] == "lead_hot"
    assert bus.is_file()


def test_tt_transport_stub():
    assert isinstance(get_transport("mock"), MockTransport)
    live_tt = get_transport("live", platform="tiktok")
    assert isinstance(live_tt, LiveTikTokTransport)
    r = live_tt.read(target_id="tt_own", platform="tiktok", external_id="x")
    assert r.ok is False
    c = live_tt.comment(
        target_id="tt_own",
        platform="tiktok",
        external_id="x",
        text="hi",
        dry_run=True,
    )
    assert c.ok is True
    assert c.dry_run is True


def test_a2a_auto_on_val_pass(tmp_path: Path, monkeypatch):
    bus = tmp_path / "A2A.jsonl"
    monkeypatch.setenv("DEMAND_OS_A2A_BUS", str(bus))
    # also patch default path via env used by a2a_bus
    req = PublishRequest(
        asset_id="tt_w32_install_01",
        channel="tiktok",
        icp_role="installateur",
        caption="installateur witte bus Wizard\n" + UTM_TT + "\n#installateur",
        utm_link=UTM_TT,
    )
    decision = evaluate_publish_request(req, log=False, emit_events=True)
    assert decision.ok is True
    lines = [json.loads(l) for l in bus.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert any(x.get("handoff_type") == "publish_request" for x in lines)
    assert any(x.get("status") == "acked" for x in lines)


def test_weekly_no_live_publish_cta(tmp_path: Path):
    (tmp_path / "LEDGER.csv").write_text(
        "date,channel,icp_role,asset_id,utm_link,publish_Y/N,comments_sent,"
        "hot_leads,wizard_starts,paid,notes\n",
        encoding="utf-8",
    )
    (tmp_path / "VALIDATOR-LOG.csv").write_text(
        "asset_id,decision\n", encoding="utf-8"
    )
    mem = tmp_path / "MEMORY.json"
    report = weekly_success_report(set_now=tmp_path, memory_path=mem)
    assert report["live_publish_cta"] is False
    assert report["marketing"] == "PARKED_LAST"
    assert report["improvement"]
