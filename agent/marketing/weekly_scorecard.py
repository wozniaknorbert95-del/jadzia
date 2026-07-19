"""Weekly scorecard draft from DTL facts — draft only, no HOLD/KILL decisions."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agent.db import db_list_marketing_facts

logger = logging.getLogger(__name__)

CAMPAIGN_DEFAULT = "zzp_branding_check_v1"
ADS_MANAGER_NOTE = "wklej z Ads Manager (brak Ads API spend)"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _iso_week(dt: Optional[datetime] = None) -> str:
    d = dt or _utc_now()
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def _latest_fact(metric_key: str) -> Optional[Dict[str, Any]]:
    rows = db_list_marketing_facts(metric_key=metric_key, limit=1)
    return rows[0] if rows else None


def _fact_value(metric_key: str) -> Optional[float]:
    row = _latest_fact(metric_key)
    if not row:
        return None
    try:
        return float(row.get("value"))
    except (TypeError, ValueError):
        return None


def _fact_as_of(metric_key: str) -> Optional[str]:
    row = _latest_fact(metric_key)
    return str(row.get("as_of")) if row and row.get("as_of") else None


def build_weekly_scorecard_draft(
    *,
    campaign: str = CAMPAIGN_DEFAULT,
    iso_week: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build JSON draft + PL text from DTL facts.
    Meta spend/CPL stay null — never invent Ads Manager numbers.
    Does not propose HOLD/KILL/SCALE.
    """
    week = iso_week or _iso_week()
    leads = _fact_value("ops_leads_count")
    leads_open = _fact_value("ops_leads_open")
    orders = _fact_value("ops_orders_count")
    gross = _fact_value("ops_orders_gross_sum")
    margin_net = _fact_value("margin_net_sum")
    attr_cov = _fact_value("attribution_coverage_pct")
    organic_er = _fact_value("organic_er_baseline_30d")

    # Paid KPIs — Ads API not in scope
    spend_eur = None
    cpl = None
    wizard_starts = None
    lead_to_wizard_pct = None
    lead_to_purchase_pct = None
    cpa_wizard = None
    sla_lead_median_min = None
    leads_over_2h = None

    notes: List[str] = [
        f"Spend / CPL / creatives: {ADS_MANAGER_NOTE}",
        "Draft tylko — decyzja HOLD/KILL/SCALE zostaje u Dowódcy (HITL).",
    ]
    if leads is None:
        notes.append("ops_leads_count brak w DTL — odpal DTL ingest.")
    if orders is None:
        notes.append("ops_orders_count brak w DTL.")

    kpis = {
        "leads": leads,
        "leads_open": leads_open,
        "cpl": cpl,
        "spend_eur": spend_eur,
        "wizard_starts": wizard_starts,
        "lead_to_wizard_pct": lead_to_wizard_pct,
        "purchases": orders,
        "lead_to_purchase_pct": lead_to_purchase_pct,
        "cpa_wizard": cpa_wizard,
        "sla_lead_median_min": sla_lead_median_min,
        "leads_over_2h": leads_over_2h,
        "orders_gross_sum": gross,
        "margin_net_sum": margin_net,
        "attribution_coverage_pct": attr_cov,
        "organic_er_baseline_30d": organic_er,
    }

    sources = {
        "ops_leads_count": _fact_as_of("ops_leads_count"),
        "ops_orders_count": _fact_as_of("ops_orders_count"),
        "margin_net_sum": _fact_as_of("margin_net_sum"),
        "attribution_coverage_pct": _fact_as_of("attribution_coverage_pct"),
        "organic_er_baseline_30d": _fact_as_of("organic_er_baseline_30d"),
    }

    text_pl = format_weekly_scorecard_pl(
        {
            "iso_week": week,
            "campaign": campaign,
            "kpis": kpis,
            "notes": notes,
        }
    )

    return {
        "ok": True,
        "iso_week": week,
        "campaign": campaign,
        "as_of": _utc_now().isoformat(),
        "kpis": kpis,
        "sources": sources,
        "notes": notes,
        "decision": None,
        "decision_note": "HITL only — draft nie proponuje HOLD/KILL/SCALE",
        "text_pl": text_pl,
    }


def format_weekly_scorecard_pl(draft: Dict[str, Any]) -> str:
    k = draft.get("kpis") or {}
    notes = draft.get("notes") or []

    def _fmt(v: Any) -> str:
        if v is None:
            return "—"
        if isinstance(v, float):
            if abs(v - round(v)) < 1e-9:
                return str(int(round(v)))
            return f"{v:.2f}"
        return str(v)

    lines = [
        f"📊 Weekly scorecard DRAFT · {draft.get('iso_week')}",
        f"Kampania: {draft.get('campaign')}",
        f"Leads: {_fmt(k.get('leads'))} (open {_fmt(k.get('leads_open'))})",
        f"Spend/CPL: — ({ADS_MANAGER_NOTE})",
        f"Purchases≈orders: {_fmt(k.get('purchases'))}",
        f"Margin net: {_fmt(k.get('margin_net_sum'))}",
        f"Attr coverage %: {_fmt(k.get('attribution_coverage_pct'))}",
        f"Organic ER baseline: {_fmt(k.get('organic_er_baseline_30d'))}",
        "Decyzja OS: (pusta — Ty wybierasz HOLD/KILL/SCALE)",
    ]
    for n in notes[:3]:
        lines.append(f"• {n}")
    return "\n".join(lines)


def send_weekly_scorecard_telegram(draft: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Plain admin-chat draft — no decision buttons."""
    import os

    import httpx

    from agent.marketing.telegram_proposals import _telegram_admin_chat

    payload = draft or build_weekly_scorecard_draft()
    bot_token, admin_id = _telegram_admin_chat()
    if not bot_token or not admin_id:
        return {
            "ok": False,
            "error": "missing TELEGRAM_BOT_TOKEN or admin chat",
            "sent": 0,
        }

    text = payload.get("text_pl") or format_weekly_scorecard_pl(payload)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        with httpx.Client(timeout=15.0) as client:
            r = client.post(url, json={"chat_id": admin_id, "text": text})
        if not r.is_success:
            logger.error(
                "[mb.weekly] telegram failed status=%s",
                r.status_code,
            )
            return {"ok": False, "error": f"http_{r.status_code}", "sent": 0}
    except Exception as exc:
        logger.error("[mb.weekly] telegram send failed: %s", exc)
        return {"ok": False, "error": str(exc), "sent": 0}

    return {"ok": True, "sent": 1, "iso_week": payload.get("iso_week")}


def run_weekly_scorecard_nudge_if_due(*, interval_seconds: int) -> Dict[str, Any]:
    """Durable weekly TG draft nudge (agent_state mb_weekly_scorecard)."""
    import os
    from datetime import timedelta

    from agent.db import db_commander_get_agent_state, db_commander_upsert_agent_state

    if interval_seconds <= 0:
        return {"ok": True, "skipped": True, "reason": "disabled"}

    now = _utc_now()
    state = db_commander_get_agent_state("mb_weekly_scorecard") or {}
    last_raw = state.get("last_run_at")
    if last_raw:
        try:
            last = datetime.fromisoformat(str(last_raw).replace("Z", "+00:00"))
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            if now - last < timedelta(seconds=interval_seconds):
                return {
                    "ok": True,
                    "skipped": True,
                    "reason": "not_due",
                    "last_run_at": last_raw,
                    "interval_seconds": interval_seconds,
                }
        except Exception:
            pass

    draft = build_weekly_scorecard_draft()
    push = send_weekly_scorecard_telegram(draft)
    now_iso = now.isoformat()
    db_commander_upsert_agent_state(
        "mb_weekly_scorecard",
        {
            "status": "LIVE" if push.get("ok") else "DEGRADED",
            "last_run_at": now_iso,
            "last_error": None if push.get("ok") else (push.get("error") or "push_failed"),
            "expected_interval_seconds": interval_seconds,
            "iso_week": draft.get("iso_week"),
        },
    )
    logger.info(
        "[mb.weekly] nudge sent=%s week=%s",
        push.get("sent"),
        draft.get("iso_week"),
    )
    return {
        "ok": bool(push.get("ok")),
        "skipped": False,
        "push": push,
        "draft": draft,
        "last_run_at": now_iso,
        "interval_seconds": interval_seconds,
        "env_hint": os.getenv("MARKETING_WEEKLY_SCORECARD_INTERVAL_SECONDS"),
    }
