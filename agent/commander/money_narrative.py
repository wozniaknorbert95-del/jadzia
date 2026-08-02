"""Honest money/risk narrative for Mission Control (DI-S6).

Counts + blockers only. Never emit vanity € / green revenue totals on L1.
Order Desk remains PARKED (EV-W2-010) until S7 SoT.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agent.commander.sla import freshness_status

CTA_SCORE_THRESHOLD = 40
HOT_LEAD_SCORE = 80
ORDER_DESK = {"status": "PARKED", "evidence": "EV-W2-010"}


def _utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _lead_counts(leads: List[Dict[str, Any]]) -> Dict[str, int]:
    open_n = hot_n = cta_n = 0
    for lead in leads:
        if lead.get("is_test") is True:
            continue
        disposition = (lead.get("disposition") or "open").lower()
        if disposition in ("closed", "snoozed"):
            continue
        open_n += 1
        score = int(lead.get("game_score") or 0)
        if score >= HOT_LEAD_SCORE:
            hot_n += 1
        if score >= CTA_SCORE_THRESHOLD:
            cta_n += 1
    return {"open_leads": open_n, "hot_leads": hot_n, "cta_band_leads": cta_n}


def _ga4_honesty(snap: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    generated_at = (snap or {}).get("generated_at")
    fresh = freshness_status("ga4", generated_at)
    # Wizard funnel fields: expose only as null placeholders — never invent sessions.
    # purchase_revenue intentionally omitted from L1 narrative.
    return {
        "freshness": fresh.get("status"),
        "generated_at": generated_at,
        "sync_status": (snap or {}).get("sync_status"),
        "wizard_sessions": None,
        "wizard_conversions": None,
        "usable_for_money": False,
        "note": "GA4 money/funnel not claimed on L1 — freshness chip only; no vanity euro",
    }


def _top_risk_from_brief(brief: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    nba = brief.get("nba")
    if not nba:
        return None
    return {
        "title": nba.get("title"),
        "owner": nba.get("owner") or "Dowódca",
        "queue_type": nba.get("queue_type"),
        "severity": nba.get("severity"),
        "evidence_ts": nba.get("evidence_ts") or nba.get("created_at"),
        "approval_class": nba.get("approval_class"),
        "why_now": nba.get("why_now"),
    }


def build_money_risk_narrative(
    *,
    leads: Optional[List[Dict[str, Any]]] = None,
    analytics_snap: Optional[Dict[str, Any]] = None,
    brief: Optional[Dict[str, Any]] = None,
    demand_os_mc: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build read-only money/risk narrative. Inject deps for unit tests."""
    from agent.db import db_list_analytics_snapshots, db_list_leads

    if leads is None:
        leads = db_list_leads(limit=50)
    if analytics_snap is None:
        rows = db_list_analytics_snapshots(limit=1)
        analytics_snap = rows[0] if rows else None
    if brief is None:
        from agent.commander.queue import build_director_brief_from_queue

        brief = build_director_brief_from_queue(max_secondary=0)

    counts = _lead_counts(leads)
    ga4 = _ga4_honesty(analytics_snap)
    top_risk = _top_risk_from_brief(brief or {})

    # Demand OS Hub §M — starts by UTM (never vanity views / euro)
    demand_os: Dict[str, Any] = {
        "starts_utm": 0,
        "paid": 0,
        "top_hook": "",
        "validator_fail": 0,
        "marketing": "PARKED_LAST",
        "source": "demand_os.money_check",
        "kill_vanity": True,
    }
    try:
        if demand_os_mc is not None:
            mc = demand_os_mc
        else:
            from agent.demand_os.observability import money_check

            mc = money_check()
        demand_os = {
            "starts_utm": int(mc.get("starts_utm") or 0),
            "paid": int(mc.get("paid") or 0),
            "top_hook": mc.get("top_hook") or "",
            "validator_fail": int(mc.get("validator_fail") or 0),
            "sniper_compliance": mc.get("sniper_compliance"),
            "marketing": "PARKED_LAST",
            "source": "demand_os.money_check",
            "kill_vanity": True,
        }
    except Exception as exc:
        demand_os["error"] = str(exc)[:160]

    has_lead_signal = (
        counts["open_leads"] > 0
        or counts["hot_leads"] > 0
        or counts["cta_band_leads"] > 0
    )
    has_demand_signal = int(demand_os.get("starts_utm") or 0) > 0
    if has_lead_signal or top_risk:
        status = "partial"
        q1 = (
            f"Pipeline signal: {counts['open_leads']} open lead(s), "
            f"{counts['hot_leads']} hot, {counts['cta_band_leads']} CTA-band. "
            "No live euro claimed — Order Desk PARKED."
        )
        cta = {
            "label": "Focus queue",
            "action": "focus_queue",
            "target": "queue",
        }
    elif has_demand_signal:
        status = "partial"
        q1 = (
            f"Demand OS: {demand_os['starts_utm']} Wizard start(s) UTM · "
            f"top_hook={demand_os.get('top_hook') or 'none'} · "
            "marketing HITL PARKED_LAST — no live euro claimed."
        )
        cta = {
            "label": "Demand OS status",
            "action": "demand_os_status",
            "target": "/api/v1/commander/demand-os/status",
        }
    else:
        status = "insufficient_data"
        q1 = (
            "Insufficient money/risk signal — no open leads, no ranked NBA, "
            "Demand OS starts_utm=0. Verify ingest/fixture; do not invent revenue. "
            "Marketing PARKED_LAST."
        )
        cta = {
            "label": "Open Wizard",
            "action": "open_wizard",
            "target": "https://zzpackage.flexgrafik.nl/wizard/",
        }

    event_ids = [ORDER_DESK["evidence"], "demand_os:hub"]
    if top_risk and top_risk.get("queue_type"):
        event_ids.append(f"nba:{top_risk['queue_type']}")

    # Prefer Hub starts over null GA4 wizard_sessions when available
    wizard_sessions = demand_os["starts_utm"] if has_demand_signal else ga4["wizard_sessions"]

    return {
        "status": status,
        "as_of": _utcnow(),
        "q1": q1,
        "pipeline": {
            **counts,
            "wizard_sessions": wizard_sessions,
            "wizard_conversions": ga4["wizard_conversions"],
            "order_desk": dict(ORDER_DESK),
        },
        "demand_os": demand_os,
        "top_risk": top_risk,
        "freshness": {
            "ga4": ga4["freshness"],
            "ga4_generated_at": ga4["generated_at"],
        },
        "ga4": ga4,
        "honesty": [
            "No vanity euro totals on Mission Control L1",
            "Order Desk PARKED · EV-W2-010",
            "GA4 purchase revenue not shown as money KPI",
            "Demand OS marketing HITL PARKED_LAST until GO MARKETING HITL",
        ],
        "cta": cta,
        "event_ids": event_ids,
        "policy_ref": "DI-S6",
    }
