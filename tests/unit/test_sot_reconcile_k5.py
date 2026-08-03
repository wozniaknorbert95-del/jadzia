"""K5 dual SoT reconcile tests."""

from __future__ import annotations

import json
from pathlib import Path

from agent.demand_os.attribution import ingest_wizard_start_event
from agent.demand_os.observability import build_screen, money_check
from agent.demand_os.sot_reconcile import reconcile_dual_sot

UTM = (
    "https://zzpackage.flexgrafik.nl/wizard/"
    "?utm_source=tiktok&utm_medium=organic&utm_campaign=w&utm_content=a1"
)


def test_reconcile_detects_missing_projection(tmp_path: Path):
    db = tmp_path / "j.db"
    set_now = tmp_path / "set-now"
    set_now.mkdir()
    ingest_wizard_start_event(
        event_id="e1",
        ts_utc="2026-08-03T10:00:00+00:00",
        utm_link=UTM,
        asset_id="a1",
        provenance="test",
        source_event_id="s1",
        db_path=db,
    )
    report = reconcile_dual_sot(set_now=set_now, db_path=db, dry_run=True)
    assert report["sqlite_total"] == 1
    assert report["dry_run"] is True
    assert any(d["kind"] == "missing_projection" for d in report["drift"])


def test_build_screen_does_not_double_count_ledger_and_events(tmp_path: Path):
    """Same start in LEDGER + GROWTH-EVENTS must count once (events authority)."""
    ledger = tmp_path / "LEDGER.csv"
    ledger.write_text(
        "date,channel,icp_role,asset_id,utm_link,publish_Y/N,comments_sent,"
        "hot_leads,wizard_starts,paid,notes\n"
        f"2026-08-03,tiktok,r,a1,{UTM},N,0,0,1,0,\n",
        encoding="utf-8",
    )
    events = tmp_path / "GROWTH-EVENTS.jsonl"
    events.write_text(
        json.dumps(
            {
                "id": "g1",
                "ts": "2026-08-03T10:00:00+00:00",
                "event_type": "wizard_start",
                "utm_link": UTM,
                "asset_id": "a1",
                "channel": "tiktok",
                "count": 1,
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "VALIDATOR-LOG.csv").write_text("asset_id,decision\n", encoding="utf-8")
    screen = build_screen(set_now=tmp_path, events_path=events)
    assert sum(screen.wizard_starts_by_utm.values()) == 1
    assert "growth_events" in (screen.notes or "")
    mc = money_check(set_now=tmp_path, events_path=events)
    assert mc["starts_utm"] == 1


def test_reconcile_count_mismatch_and_ledger_lag(tmp_path: Path):
    db = tmp_path / "j.db"
    set_now = tmp_path / "set-now"
    set_now.mkdir()
    ingest_wizard_start_event(
        event_id="e2",
        ts_utc="2026-08-03T11:00:00+00:00",
        utm_link=UTM,
        asset_id="a1",
        provenance="test",
        source_event_id="s2",
        db_path=db,
    )
    events = set_now / "GROWTH-EVENTS.jsonl"
    events.write_text(
        json.dumps(
            {
                "id": "g2",
                "ts": "2026-08-03T11:00:00+00:00",
                "event_type": "wizard_start",
                "utm_link": UTM,
                "asset_id": "a1",
                "count": 1,
            }
        )
        + "\n"
        + json.dumps(
            {
                "id": "g3",
                "ts": "2026-08-03T12:00:00+00:00",
                "event_type": "wizard_start",
                "utm_link": UTM,
                "asset_id": "a1",
                "count": 1,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (set_now / "LEDGER.csv").write_text(
        "date,channel,icp_role,asset_id,utm_link,publish_Y/N,comments_sent,"
        "hot_leads,wizard_starts,paid,notes\n"
        "2026-08-03,tiktok,r,a1,,N,0,0,0,0,\n",
        encoding="utf-8",
    )
    report = reconcile_dual_sot(set_now=set_now, db_path=db, dry_run=True)
    kinds = {d["kind"] for d in report["drift"]}
    assert "count_mismatch" in kinds
    assert "ledger_lag" in kinds
