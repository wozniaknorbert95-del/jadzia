"""K1 REV_R1 attribution contract tests."""

from __future__ import annotations

from pathlib import Path

from agent.demand_os.attribution import (
    attribution_summary,
    ingest_wizard_start_event,
    resolve_attribution_status,
    sync_ops_bus_to_attribution,
)


def test_resolve_attribution_statuses():
    assert (
        resolve_attribution_status(
            asset_id="tt_w32",
            utm_parts={"source": "tiktok", "medium": "organic", "content": "tt_w32"},
            calendar_assets={"tt_w32"},
        )
        == "attributed"
    )
    assert (
        resolve_attribution_status(
            asset_id="",
            utm_parts={"source": "", "medium": ""},
        )
        == "unattributed"
    )
    assert (
        resolve_attribution_status(
            asset_id="x",
            utm_parts={"source": "tiktok", "medium": "organic", "content": "y"},
            calendar_assets={"y"},
        )
        == "ambiguous"
    )


def test_ingest_dedupe(tmp_path: Path):
    db = tmp_path / "a.db"
    utm = "https://zzpackage.flexgrafik.nl/wizard/?utm_source=tiktok&utm_medium=organic&utm_campaign=w32&utm_content=tt_w32"
    r1 = ingest_wizard_start_event(
        event_id="e1",
        ts_utc="2026-08-03T10:00:00+00:00",
        utm_link=utm,
        asset_id="tt_w32",
        provenance="test",
        source_event_id="src1",
        calendar_assets={"tt_w32"},
        db_path=db,
    )
    r2 = ingest_wizard_start_event(
        event_id="e1-retry",
        ts_utc="2026-08-03T10:00:00+00:00",
        utm_link=utm,
        asset_id="tt_w32",
        provenance="test",
        source_event_id="src1",
        calendar_assets={"tt_w32"},
        db_path=db,
    )
    assert r1["ok"] and not r1["duplicate"]
    assert r1["attribution_status"] == "attributed"
    assert r2["duplicate"] is True
    summary = attribution_summary(db_path=db, days=7)
    assert summary["total"] == 1
    assert summary["window_days"] == 7
    assert summary["by_status"]["attributed"] == 1
    assert summary["top_assets"][0]["asset_id"] == "tt_w32"


def test_attribution_summary_respects_window(tmp_path: Path):
    db = tmp_path / "w.db"
    utm = "https://zzpackage.flexgrafik.nl/wizard/?utm_source=tiktok&utm_medium=organic&utm_campaign=w&utm_content=a1"
    ingest_wizard_start_event(
        event_id="old",
        ts_utc="2020-01-01T00:00:00+00:00",
        utm_link=utm,
        asset_id="a1",
        provenance="test",
        source_event_id="old1",
        calendar_assets={"a1"},
        db_path=db,
    )
    ingest_wizard_start_event(
        event_id="new",
        ts_utc="2026-08-03T10:00:00+00:00",
        utm_link=utm + "&x=1",
        asset_id="a1",
        provenance="test",
        source_event_id="new1",
        calendar_assets={"a1"},
        db_path=db,
    )
    assert attribution_summary(db_path=db, days=7)["total"] == 1
    assert attribution_summary(db_path=db, days=90)["total"] >= 1


def test_sync_ops_bus_to_attribution_dry_run(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(
        "agent.db.db_ops_bus_list",
        lambda **kwargs: [
            {
                "event_id": "ops1",
                "source_event_id": "src-ops1",
                "created_at": "2026-08-03T12:00:00+00:00",
                "payload": {
                    "utm_link": "https://zzpackage.flexgrafik.nl/wizard/?utm_source=tiktok&utm_medium=organic&utm_campaign=w&utm_content=a1",
                    "asset_id": "a1",
                },
            }
        ],
    )
    out = sync_ops_bus_to_attribution(dry_run=True, db_path=tmp_path / "x.db")
    assert out["ok"] is True
    assert out["synced"] == 1
    assert out["dry_run"] is True
