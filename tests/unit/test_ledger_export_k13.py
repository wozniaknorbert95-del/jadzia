"""K13 ledger export tests."""

from __future__ import annotations

from pathlib import Path

from agent.demand_os.attribution import ingest_wizard_start_event
from agent.demand_os.ledger_export import export_ledger, render_ledger_csv


def test_export_dry_run_and_apply_idempotent(tmp_path: Path):
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
    dry = export_ledger(set_now=set_now, db_path=db, dry_run=True)
    assert dry["ok"] and dry["applied"] is False
    assert dry["manifest"]["row_count"] == 1
    applied = export_ledger(set_now=set_now, db_path=db, dry_run=False)
    assert applied["applied"] is True
    body1 = (set_now / "LEDGER.csv").read_text(encoding="utf-8")
    applied2 = export_ledger(set_now=set_now, db_path=db, dry_run=False)
    body2 = (set_now / "LEDGER.csv").read_text(encoding="utf-8")
    assert body1 == body2
    assert applied["manifest"]["checksum_sha256"] == applied2["manifest"]["checksum_sha256"]
    assert "wizard_starts" in render_ledger_csv([])
