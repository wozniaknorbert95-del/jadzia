"""DI-S6: honest money/risk narrative — no vanity €."""

from __future__ import annotations


def test_insufficient_data_when_no_leads_no_nba():
    from agent.commander.money_narrative import build_money_risk_narrative

    out = build_money_risk_narrative(
        leads=[],
        analytics_snap=None,
        brief={"nba": None},
        demand_os_mc={"starts_utm": 0, "paid": 0, "top_hook": "", "validator_fail": 0},
    )
    assert out["status"] == "insufficient_data"
    assert out["cta"]["action"] == "open_wizard"
    assert "€" not in out["q1"]
    assert out["pipeline"]["order_desk"]["evidence"] == "EV-W2-010"
    assert "EV-W2-010" in out["event_ids"]
    assert "revenue" not in out
    assert "revenue_eur" not in out
    assert out["pipeline"]["wizard_sessions"] is None
    assert out["demand_os"]["marketing"] == "PARKED_LAST"


def test_demand_os_hub_partial_with_starts():
    from agent.commander.money_narrative import build_money_risk_narrative

    out = build_money_risk_narrative(
        leads=[],
        analytics_snap=None,
        brief={"nba": None},
        demand_os_mc={
            "starts_utm": 3,
            "paid": 1,
            "top_hook": "tt_w32_install_01",
            "validator_fail": 0,
        },
    )
    assert out["status"] == "partial"
    assert out["demand_os"]["starts_utm"] == 3
    assert out["demand_os"]["marketing"] == "PARKED_LAST"
    assert out["pipeline"]["wizard_sessions"] == 3
    assert out["cta"]["action"] == "demand_os_status"
    assert "€" not in str(out)


def test_partial_with_hot_lead_counts_and_top_risk():
    from agent.commander.money_narrative import build_money_risk_narrative

    leads = [
        {
            "id": 1,
            "game_score": 90,
            "disposition": "open",
            "is_test": False,
            "email": "a@b.c",
        },
        {
            "id": 2,
            "game_score": 50,
            "disposition": "open",
            "is_test": False,
            "email": "c@d.e",
        },
        {
            "id": 3,
            "game_score": 95,
            "disposition": "closed",
            "is_test": False,
            "email": "x@y.z",
        },
    ]
    brief = {
        "nba": {
            "title": "Hot lead: a@b.c",
            "owner": "Sales / Dowódca",
            "queue_type": "hot_lead",
            "severity": "CRITICAL",
            "evidence_ts": "2026-07-31T10:00:00+00:00",
            "approval_class": "L1",
            "why_now": "Pending hot_lead",
        }
    }
    out = build_money_risk_narrative(
        leads=leads,
        analytics_snap=None,
        brief=brief,
        demand_os_mc={"starts_utm": 0, "paid": 0, "top_hook": "", "validator_fail": 0},
    )
    assert out["status"] == "partial"
    assert out["pipeline"]["open_leads"] == 2
    assert out["pipeline"]["hot_leads"] == 1
    assert out["pipeline"]["cta_band_leads"] == 2
    assert out["top_risk"]["owner"] == "Sales / Dowódca"
    assert out["top_risk"]["queue_type"] == "hot_lead"
    assert out["cta"]["action"] == "focus_queue"
    assert "€" not in str(out)
    assert out["pipeline"]["order_desk"]["status"] == "PARKED"


def test_never_surfaces_purchase_revenue_from_snapshot():
    from agent.commander.money_narrative import build_money_risk_narrative

    snap = {
        "generated_at": "2026-07-31T10:00:00+00:00",
        "sync_status": "ok",
        "sources_json": '{"zzpackage":{"purchase_revenue":99999,"sessions":12}}',
    }
    out = build_money_risk_narrative(
        leads=[],
        analytics_snap=snap,
        brief={"nba": None},
        demand_os_mc={"starts_utm": 0, "paid": 0, "top_hook": "", "validator_fail": 0},
    )
    blob = str(out)
    assert "99999" not in blob
    assert "purchase_revenue" not in blob or out["ga4"]["usable_for_money"] is False
    assert "revenue_eur" not in out
