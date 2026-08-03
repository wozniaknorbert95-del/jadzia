"""K5 dual SoT reconcile tests."""

from __future__ import annotations

from pathlib import Path

from agent.demand_os.attribution import ingest_wizard_start_event
from agent.demand_os.sot_reconcile import reconcile_dual_sot


def test_reconcile_detects_missing_projection(tmp_path: Path):
    db = tmp_path / "j.db"
    set_now = tmp_path / "set-now"
    set_now.mkdir()
    utm = "https://zzpackage.flexgrafik.nl/wizard/?utm_source=tiktok&utm_medium=organic&utm_campaign=w&utm_content=a1"
    ingest_wizard_start_event(
        event_id="e1",
        ts_utc="2026-08-03T10:00:00+00:00",
        utm_link=utm,
        asset_id="a1",
        provenance="test",
        source_event_id="s1",
        db_path=db,
    )
    report = reconcile_dual_sot(set_now=set_now, db_path=db, dry_run=True)
    assert report["sqlite_total"] == 1
    assert report["dry_run"] is True
    assert any(d["kind"] == "missing_projection" for d in report["drift"])
