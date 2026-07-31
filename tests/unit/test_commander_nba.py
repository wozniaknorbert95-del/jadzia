"""DI-S5: deterministic NBA ranking."""

from __future__ import annotations

import os

import pytest


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
    yield path


def _item(**kwargs):
    base = {
        "id": "x",
        "queue_type": "fb_post_pending",
        "title": "t",
        "severity": "ACTION",
        "age_hours": 2.0,
        "sla_status": "OK",
        "created_at": "2026-07-31T08:00:00+00:00",
        "payload": {},
        "escalation_reason": "Pending",
        "source": "calendar",
        "confidence": 0.9,
    }
    base.update(kwargs)
    return base


def test_score_is_deterministic_and_higher_for_sales_vs_fb():
    from agent.commander.nba import score_queue_item

    sales = score_queue_item(
        _item(queue_type="sales_cta", id="s", severity="ACTION", confidence=0.85)
    )
    fb = score_queue_item(
        _item(queue_type="fb_post_pending", id="f", severity="ACTION", confidence=0.9)
    )
    assert sales["score"] > fb["score"]
    assert score_queue_item(
        _item(queue_type="sales_cta", id="s", severity="ACTION", confidence=0.85)
    )["score"] == sales["score"]


def test_critical_outranks_action_same_type_proxy():
    from agent.commander.nba import rank_candidates

    action = _item(id="a", queue_type="wp_ticket", severity="ACTION", sla_status="OK")
    critical = _item(
        id="c", queue_type="wp_ticket", severity="CRITICAL", sla_status="RED", age_hours=8
    )
    ranked = rank_candidates([action, critical])
    assert ranked[0]["id"] == "c"


def test_info_and_stubs_never_nba():
    from agent.commander.nba import select_nba

    junk = [
        _item(
            id="stub",
            queue_type="ceo_stub",
            severity="INFO",
            source="brain_bus_ceo",
        ),
        _item(
            id="stale",
            queue_type="analytics_stale",
            severity="INFO",
            source="analytics",
        ),
    ]
    assert select_nba(junk) is None


def test_enrich_nba_required_fields():
    from agent.commander.nba import enrich_nba

    card = enrich_nba(
        _item(
            id="lead-1",
            queue_type="sales_cta",
            payload={"lead_id": 10},
            escalation_reason="Sales CTA follow-up",
        )
    )
    assert card["nba_primary"] is True
    assert card["why_now"]
    assert card["evidence_ts"]
    assert card["owner"]
    assert card["cta"]["label"]
    assert card["cta"]["action"] == "lead_ack"
    assert card["cost_of_inaction"]
    assert card["approval_class"] == "L1"
    assert "score" in card["nba_score_parts"]


def test_build_director_brief_one_primary_two_secondary():
    from agent.commander.nba import build_director_brief

    items = [
        _item(id="fb", queue_type="fb_post_pending", severity="ACTION"),
        _item(
            id="sale",
            queue_type="sales_cta",
            severity="ACTION",
            payload={"lead_id": 10},
            confidence=0.85,
        ),
        _item(id="cs", queue_type="cs_followup", severity="ACTION", payload={"ticket_id": 1}),
    ]
    brief = build_director_brief(items, max_secondary=2)
    assert brief["nba"] is not None
    assert brief["nba"]["nba_primary"] is True
    assert brief["nba"]["queue_type"] == "sales_cta"
    assert len(brief["secondary"]) == 2
    assert all(not s.get("nba_primary") for s in brief["secondary"])


def test_build_priorities_today_excludes_stale_uses_rank(temp_db):
    from datetime import datetime, timedelta, timezone

    from agent.commander.queue import build_director_brief_from_queue, build_priorities_today
    from agent.db import db_commander_create_ticket, db_save_analytics_snapshot

    stale_at = (datetime.now(timezone.utc) - timedelta(hours=6)).replace(
        microsecond=0
    ).isoformat()
    db_save_analytics_snapshot({
        "period": "7d",
        "generated_at": stale_at,
        "sync_status": "ok",
        "sources": {"ga4": True},
        "errors": [],
    })
    db_commander_create_ticket(
        "[Sales CTA] Follow up lead #99",
        "lead_id=99\ncta_sku=x\nwizard_deeplink=https://zzpackage.flexgrafik.nl/wizard/",
        "brief_sales_cta",
        severity="MEDIUM",
    )
    brief = build_director_brief_from_queue()
    assert brief["nba"] is None or brief["nba"].get("queue_type") != "analytics_stale"
    prio = build_priorities_today()
    assert not any(p.get("queue_type") == "analytics_stale" for p in prio)
