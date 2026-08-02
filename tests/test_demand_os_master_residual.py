"""MASTER residual — db_utm · ga4 · widget leads · wave1 agents."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from agent.demand_os.agents.wave1 import WAVE1_ROLES, run_agent
from agent.demand_os.db_utm import sync_wizard_starts_from_ops_bus
from agent.demand_os.ga4_adapter import fetch_wizard_starts, pull_ga4_into_dtl
from agent.demand_os.utm_lock import build_wizard_utm
from agent.demand_os.widget_leads import list_hot_leads, sync_hot_leads_to_a2a


def test_sync_ops_bus_dry_run(tmp_path: Path):
    events = tmp_path / "GROWTH-EVENTS.jsonl"
    utm = build_wizard_utm("tiktok", "installateur", "ops_tt_01")
    fake_rows = [
        {
            "event_id": "e1",
            "id": 1,
            "payload": {
                "utm_link": utm,
                "asset_id": "ops_tt_01",
                "utm_source": "tiktok",
            },
        }
    ]
    import agent.db as dbmod

    with patch.object(dbmod, "db_ops_bus_list", return_value=fake_rows):
        result = sync_wizard_starts_from_ops_bus(
            dry_run=True, events_path=events, limit=10
        )
    assert result["ok"] is True
    assert result["synced"] == 1
    assert result["dry_run"] is True
    assert not events.exists()


def test_sync_ops_bus_ingest(tmp_path: Path):
    events = tmp_path / "e.jsonl"
    utm = build_wizard_utm("facebook", "installateur", "ops_fb_01")
    fake_rows = [
        {
            "event_id": "e2",
            "payload": {
                "utm_link": utm,
                "asset_id": "ops_fb_01",
                "utm_source": "facebook",
            },
        }
    ]
    import agent.db as dbmod

    with patch.object(dbmod, "db_ops_bus_list", return_value=fake_rows):
        result = sync_wizard_starts_from_ops_bus(
            dry_run=False, events_path=events, limit=5
        )
    assert result["ok"] is True
    assert result["synced"] == 1
    assert events.is_file()
    assert "wizard_start" in events.read_text(encoding="utf-8")


def test_ga4_fail_closed():
    out = fetch_wizard_starts(days=7)
    assert out["ok"] is False
    assert out["mode"] == "stub"
    dtl = pull_ga4_into_dtl()
    assert dtl["ok"] is False


def test_hot_leads_from_db_mock():
    leads = [
        {
            "id": 9,
            "email": "hot@zzp.nl",
            "game_score": 90,
            "disposition": "open",
            "is_test": False,
            "source": "game",
        },
        {
            "id": 10,
            "email": "cold@zzp.nl",
            "game_score": 10,
            "disposition": "open",
            "is_test": False,
            "source": "game",
        },
    ]
    import agent.db as dbmod

    with patch.object(dbmod, "db_list_leads", return_value=leads):
        out = list_hot_leads(limit=10)
    assert out["ok"] is True
    assert len(out["leads"]) == 1
    assert out["leads"][0]["lead_id"] == "9"


def test_sync_hot_leads_dry_run(tmp_path: Path):
    bus = tmp_path / "a2a.jsonl"
    leads = [
        {
            "id": 11,
            "email": "a@b.c",
            "game_score": 95,
            "disposition": "open",
            "is_test": False,
            "source": "widget",
        }
    ]
    import agent.db as dbmod

    with patch.object(dbmod, "db_list_leads", return_value=leads):
        out = sync_hot_leads_to_a2a(limit=5, dry_run=True, bus_path=bus)
    assert out["ok"] is True
    assert out["emitted"] == 1
    assert out["dry_run"] is True


def test_wave1_agents():
    assert len(WAVE1_ROLES) == 5
    gl = run_agent("growth_lead", action="money_check")
    assert gl["role"] == "growth_lead"
    assert "starts_utm" in gl["result"]
    tt = run_agent("tt")
    assert tt["marketing"] == "PARKED_LAST"
    assert tt["result"]["live_publish"] is False
    val = run_agent("validator")
    assert "sniper_compliance" in val["result"]
    sales = run_agent("sales", action="list_hot")
    assert sales["role"] == "sales"
