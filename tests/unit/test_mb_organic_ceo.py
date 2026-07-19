"""DTL facebook organic ingest + brief→CEO Brain Bus."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from agent.db import (
    db_create_calendar_entry,
    db_list_marketing_facts,
    db_update_calendar_entry,
    get_connection,
)
from agent.marketing.dtl.facebook_organic import ingest_facebook_organic_posts
from agent.marketing.dtl.pipeline import run_dtl_ingest
from agent.nodes.brief_node import send_weekly_brief


@pytest.fixture
def temp_db(monkeypatch):
    import tempfile

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


def _published_post(title: str, fb_post_id: str) -> int:
    eid_str, status = db_create_calendar_entry(
        {
            "title": title,
            "body_nl": "Hallo",
            "platform": "facebook",
            "status": "draft",
            "scheduled_at": "2026-07-19T12:00:00+00:00",
        }
    )
    assert status == "success"
    eid = int(eid_str)
    assert db_update_calendar_entry(
        eid,
        {"status": "published", "fb_post_id": fb_post_id},
    )
    return eid


def test_organic_skipped_when_fb_not_configured(temp_db, monkeypatch):
    monkeypatch.delenv("FB_PAGE_ID", raising=False)
    monkeypatch.delenv("FB_ACCESS_TOKEN", raising=False)
    out = ingest_facebook_organic_posts()
    assert out["status"] == "skipped"


def test_organic_writes_lift_facts(temp_db, monkeypatch):
    monkeypatch.setenv("FB_PAGE_ID", "page1")
    monkeypatch.setenv("FB_ACCESS_TOKEN", "token1")
    _published_post("Test post", "111_222")
    _published_post("Test post 2", "111_333")

    def fake_fetch2(post_id: str):
        if post_id.endswith("222"):
            return {
                "ok": True,
                "post_id": post_id,
                "engagements": 80,
                "impressions": 100,
                "link_clicks": 20,
                "insights_ok": True,
            }
        return {
            "ok": True,
            "post_id": post_id,
            "engagements": 10,
            "impressions": 100,
            "link_clicks": 2,
            "insights_ok": True,
        }

    with patch(
        "agent.publishers.facebook.fetch_post_organic_metrics",
        side_effect=fake_fetch2,
    ):
        out = ingest_facebook_organic_posts(min_impressions=50)

    assert out["status"] == "ok"
    assert out["facts_written"] >= 1
    lifts = db_list_marketing_facts(metric_key="organic_er_lift_pct", limit=10)
    assert len(lifts) >= 1


def test_pipeline_includes_facebook_organic_step(temp_db, monkeypatch):
    monkeypatch.delenv("FB_PAGE_ID", raising=False)
    monkeypatch.delenv("FB_ACCESS_TOKEN", raising=False)
    with patch(
        "agent.marketing.dtl.ga4.ingest_ga4_snapshot",
        return_value={"source": "ga4", "status": "skipped"},
    ), patch(
        "agent.marketing.dtl.l0_probe.ingest_l0_pixel_probe",
        return_value={"source": "l0_pixel", "status": "ok"},
    ):
        summary = run_dtl_ingest(include_ga4=True, include_l0=True)
    sources = [s.get("source") for s in summary.get("steps") or []]
    assert "facebook_organic" in sources


def test_brief_publishes_ceo_priority(temp_db, monkeypatch):
    monkeypatch.setenv("BRIEF_CEO_PRIORITY_ENABLED", "1")
    called = {}

    def fake_stub(priority, *, week=None, process_now=True, send_telegram=True):
        called["priority"] = priority
        called["week"] = week
        return {"ok": True, "event_id": 1}

    with patch(
        "agent.customer_agent._send_telegram_alert_sync",
        MagicMock(),
    ), patch(
        "agent.nodes.brief_node.spawn_brief_hitl_tickets",
        return_value=[],
    ), patch(
        "agent.nodes.brief_node.spawn_brief_sales_cta_tickets",
        return_value=[],
    ), patch(
        "agent.marketing.brain_bus.publish_ceo_priority_stub",
        side_effect=fake_stub,
    ), patch(
        "agent.nodes.brief_node.propose_brief_recommendations",
        return_value=[{"title": "Fix FB hygiene", "code": "ops_fb"}],
    ):
        ok = send_weekly_brief()
    assert ok is True
    assert "Fix FB hygiene" in (called.get("priority") or "")


def test_brief_ceo_flag_off(temp_db, monkeypatch):
    monkeypatch.setenv("BRIEF_CEO_PRIORITY_ENABLED", "0")
    with patch("agent.customer_agent._send_telegram_alert_sync", MagicMock()), patch(
        "agent.nodes.brief_node.spawn_brief_hitl_tickets",
        return_value=[],
    ), patch(
        "agent.nodes.brief_node.spawn_brief_sales_cta_tickets",
        return_value=[],
    ), patch(
        "agent.marketing.brain_bus.publish_ceo_priority_stub"
    ) as stub:
        ok = send_weekly_brief()
    assert ok is True
    stub.assert_not_called()
