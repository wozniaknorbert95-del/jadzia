"""Data Health drivers + L0 IC verified / Purchase park split."""

from __future__ import annotations

import os
import tempfile
from unittest.mock import patch

import pytest

from agent.db import (
    db_deactivate_quality_flags,
    db_insert_quality_flag,
    db_list_active_quality_flags,
    get_connection,
)
from agent.marketing.dtl.report import build_data_health_report


@pytest.fixture
def temp_db(monkeypatch):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr("agent.db.DB_PATH", path)
    import agent.db as db_mod

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
    get_connection()
    yield path
    try:
        if hasattr(db_mod._local, "conn") and db_mod._local.conn:
            db_mod._local.conn.close()
            db_mod._local.conn = None
        os.unlink(path)
    except OSError:
        pass


def test_info_flags_do_not_make_overall_amber(temp_db):
    db_insert_quality_flag(
        {
            "flag_type": "park",
            "source": "l0_pixel_events_purchase",
            "severity": "info",
            "message": "Purchase PARK",
            "as_of": "2026-07-19T00:00:00+00:00",
        }
    )
    with patch(
        "agent.marketing.dtl.report.db_get_latest_marketing_raw_ingest",
        return_value={"fetched_at": "2026-07-19T12:00:00+00:00", "status": "ok", "checksum": "x"},
    ):
        with patch(
            "agent.marketing.dtl.report.freshness_status",
            return_value={"status": "ok", "age_hours": 0.1},
        ):
            report = build_data_health_report()
    assert report["overall_status"] == "ok"
    assert report["quality_summary"]["info"] >= 1
    assert report["quality_summary"]["amber"] == 0
    assert any(d.get("kind") == "ok" for d in report["drivers"])
    assert any(p["id"] == "l0_purchase" for p in report["conscious_parks"])


def test_amber_flag_still_drives_overall(temp_db):
    db_insert_quality_flag(
        {
            "flag_type": "missing",
            "source": "l0_pixel_events_ic",
            "severity": "amber",
            "message": "IC unverified",
            "as_of": "2026-07-19T00:00:00+00:00",
        }
    )
    with patch(
        "agent.marketing.dtl.report.db_get_latest_marketing_raw_ingest",
        return_value={"fetched_at": "2026-07-19T12:00:00+00:00", "status": "ok", "checksum": "x"},
    ):
        with patch(
            "agent.marketing.dtl.report.freshness_status",
            return_value={"status": "ok", "age_hours": 0.1},
        ):
            report = build_data_health_report()
    assert report["overall_status"] == "amber"
    assert any(d.get("severity") == "amber" for d in report["drivers"])


def test_l0_ic_verified_env_writes_info(temp_db, monkeypatch):
    monkeypatch.setenv("L0_IC_VERIFIED", "1")
    from agent.marketing.dtl.l0_probe import ingest_l0_pixel_probe

    with patch(
        "agent.marketing.dtl.l0_probe.probe_wizard_html",
        return_value={
            "url": "https://example.test/",
            "http_status": 200,
            "fbq": True,
            "fbevents": True,
            "gtm": False,
            "body_bytes": 100,
        },
    ):
        out = ingest_l0_pixel_probe("https://example.test/")
    assert out.get("status") == "ok"
    flags = db_list_active_quality_flags(limit=20)
    ic = [f for f in flags if f.get("source") == "l0_pixel_events_ic"]
    purch = [f for f in flags if f.get("source") == "l0_pixel_events_purchase"]
    assert ic and ic[0]["severity"] == "info"
    assert purch and purch[0]["severity"] == "info"
    # legacy amber source cleared
    legacy = [f for f in flags if f.get("source") == "l0_pixel_events"]
    assert not legacy
