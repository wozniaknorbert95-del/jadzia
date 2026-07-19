"""Weekly scorecard draft builder — DTL facts only, Ads null."""

from __future__ import annotations

import os
import tempfile
from unittest.mock import patch

import pytest

from agent.db import get_connection
from agent.marketing.weekly_scorecard import (
    build_weekly_scorecard_draft,
    format_weekly_scorecard_pl,
    run_weekly_scorecard_nudge_if_due,
)


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


def _fact(metric_key: str, value: float, as_of: str = "2026-07-19T12:00:00+00:00"):
    return {
        "metric_key": metric_key,
        "value": value,
        "as_of": as_of,
        "channel": "all",
    }


def test_draft_from_facts_ads_null(temp_db):
    facts = {
        "ops_leads_count": [_fact("ops_leads_count", 12)],
        "ops_leads_open": [_fact("ops_leads_open", 3)],
        "ops_orders_count": [_fact("ops_orders_count", 2)],
        "margin_net_sum": [_fact("margin_net_sum", 240.0)],
        "attribution_coverage_pct": [_fact("attribution_coverage_pct", 80.0)],
        "organic_er_baseline_30d": [_fact("organic_er_baseline_30d", 0.042)],
    }

    def _list(metric_key=None, limit=100):
        if metric_key:
            return list(facts.get(metric_key, []))[:limit]
        return []

    with patch(
        "agent.marketing.weekly_scorecard.db_list_marketing_facts",
        side_effect=_list,
    ):
        draft = build_weekly_scorecard_draft(iso_week="2026-W29")

    assert draft["ok"] is True
    assert draft["iso_week"] == "2026-W29"
    assert draft["kpis"]["leads"] == 12.0
    assert draft["kpis"]["purchases"] == 2.0
    assert draft["kpis"]["margin_net_sum"] == 240.0
    assert draft["kpis"]["spend_eur"] is None
    assert draft["kpis"]["cpl"] is None
    assert draft["decision"] is None
    assert "Ads Manager" in draft["text_pl"]
    assert "HOLD/KILL" in draft["text_pl"] or "HOLD/KILL" in (draft.get("decision_note") or "")


def test_format_pl_includes_null_spend():
    text = format_weekly_scorecard_pl(
        {
            "iso_week": "2026-W29",
            "campaign": "zzp_branding_check_v1",
            "kpis": {"leads": 1, "leads_open": 0, "purchases": None},
            "notes": ["x"],
        }
    )
    assert "Spend/CPL: —" in text
    assert "2026-W29" in text


def test_nudge_disabled():
    out = run_weekly_scorecard_nudge_if_due(interval_seconds=0)
    assert out["skipped"] is True
    assert out["reason"] == "disabled"
