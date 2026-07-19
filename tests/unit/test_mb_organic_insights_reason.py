"""Organic ingest reason codes + Data Health insights park."""

from __future__ import annotations

import os
import tempfile
from unittest.mock import patch

import pytest

from agent.db import get_connection
from agent.marketing.dtl.facebook_organic import ingest_facebook_organic_posts
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


def test_organic_no_published_posts(temp_db, monkeypatch):
    monkeypatch.setenv("FB_PAGE_ID", "123")
    monkeypatch.setenv("FB_ACCESS_TOKEN", "tok")
    with patch(
        "agent.publishers.facebook.check_token_health",
        return_value={"has_read_insights": False, "ok": True},
    ), patch(
        "agent.marketing.dtl.facebook_organic.db_list_calendar_entries",
        return_value=[],
    ):
        out = ingest_facebook_organic_posts()
    assert out["reason"] == "no_published_posts"
    assert out["status"] == "degraded"


def test_organic_insights_scope_missing(temp_db, monkeypatch):
    monkeypatch.setenv("FB_PAGE_ID", "123")
    monkeypatch.setenv("FB_ACCESS_TOKEN", "tok")
    with patch(
        "agent.publishers.facebook.check_token_health",
        return_value={"has_read_insights": False, "ok": True},
    ), patch(
        "agent.marketing.dtl.facebook_organic.db_list_calendar_entries",
        return_value=[{"fb_post_id": "p1"}],
    ), patch(
        "agent.publishers.facebook.fetch_post_organic_metrics",
        return_value={
            "ok": True,
            "post_id": "p1",
            "engagements": 10,
            "impressions": None,
            "insights_ok": False,
            "insights_reason": "insights_scope_missing",
            "link_clicks": None,
        },
    ):
        out = ingest_facebook_organic_posts()
    assert out["reason"] == "insights_scope_missing"
    assert out["status"] == "degraded"


def test_report_conscious_park_read_insights(temp_db, monkeypatch):
    monkeypatch.setenv("FB_PAGE_ID", "123")
    monkeypatch.setenv("FB_ACCESS_TOKEN", "tok")
    with patch(
        "agent.marketing.dtl.report.db_get_latest_marketing_raw_ingest",
        side_effect=lambda src: {
            "fetched_at": "2026-07-19T12:00:00+00:00",
            "status": "degraded",
            "checksum": "x",
            "payload": {
                "reason": "insights_scope_missing",
                "has_read_insights": False,
            },
        }
        if src == "facebook_organic"
        else {
            "fetched_at": "2026-07-19T12:00:00+00:00",
            "status": "ok",
            "checksum": "x",
            "payload": {},
        },
    ), patch(
        "agent.marketing.dtl.report.freshness_status",
        return_value={"status": "ok", "age_hours": 0.1},
    ), patch(
        "agent.publishers.facebook.is_facebook_configured",
        return_value=True,
    ), patch(
        "agent.publishers.facebook.check_token_health",
        return_value={"has_read_insights": False, "ok": True},
    ):
        report = build_data_health_report()
    assert report["overall_status"] == "ok"
    assert any(p["id"] == "fb_read_insights" for p in report["conscious_parks"])
    assert report["facebook_organic"]["reason"] == "insights_scope_missing"
