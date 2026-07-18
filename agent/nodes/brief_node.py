"""Weekly COI brief — orders, leads, analytics snapshot summary + HITL drafts."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

BRIEF_HITL_SOURCE = "brief_hitl"
BRIEF_SALES_CTA_SOURCE = "brief_sales_cta"
MAX_HITL_TICKETS = 3
MAX_SALES_CTA_TICKETS = 3
CTA_SCORE_THRESHOLD = 40  # align widget CTA gate (REV-DEMAND-02a)


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _list_cta_band_leads(limit: int = MAX_SALES_CTA_TICKETS) -> list[dict[str, Any]]:
    """Open CTA-band leads for sales HITL (score >= 40, not closed/snoozed/test)."""
    from agent.db import db_list_leads

    candidates: list[dict[str, Any]] = []
    for lead in db_list_leads(limit=50):
        if lead.get("is_test") is True:
            continue
        disposition = (lead.get("disposition") or "open").lower()
        if disposition in ("closed", "snoozed"):
            continue
        score = int(lead.get("game_score") or 0)
        if score < CTA_SCORE_THRESHOLD:
            continue
        candidates.append(lead)
    candidates.sort(key=lambda row: int(row.get("game_score") or 0), reverse=True)
    return candidates[:limit]


def collect_weekly_metrics() -> dict[str, Any]:
    """Read-only 7d metrics used by brief text and HITL recommendations."""
    from agent.db import db_get_latest_analytics_snapshot, get_connection

    since = (_utc_now() - timedelta(days=7)).replace(microsecond=0).isoformat()
    conn = get_connection()

    orders_row = conn.execute(
        """
        SELECT
            COALESCE(SUM(
                CASE WHEN classification.classification = 'real' THEN 1 ELSE 0 END
            ), 0) AS cnt,
            COALESCE(SUM(
                CASE WHEN classification.classification = 'real'
                     THEN orders.total_gross ELSE 0 END
            ), 0) AS revenue,
            COALESCE(SUM(
                CASE WHEN classification.classification = 'test' THEN 1 ELSE 0 END
            ), 0) AS test_count,
            COALESCE(SUM(
                CASE WHEN classification.classification IS NULL
                          OR classification.classification = 'unknown'
                     THEN 1 ELSE 0 END
            ), 0) AS unknown_count
        FROM orders
        LEFT JOIN revenue_classification_events AS classification
          ON classification.id = (
              SELECT MAX(latest.id)
              FROM revenue_classification_events AS latest
              WHERE latest.entity_type = 'order'
                AND latest.entity_key = orders.order_id
          )
        WHERE orders.created_at >= ?
        """,
        (since,),
    ).fetchone()
    leads_row = conn.execute(
        """
        SELECT COUNT(*) AS cnt
        FROM leads
        WHERE created_at >= ?
        """,
        (since,),
    ).fetchone()

    order_count = int(orders_row["cnt"]) if orders_row else 0
    revenue = float(orders_row["revenue"]) if orders_row else 0.0
    test_count = int(orders_row["test_count"]) if orders_row else 0
    unknown_count = int(orders_row["unknown_count"]) if orders_row else 0
    lead_count = int(leads_row["cnt"]) if leads_row else 0

    snapshot = db_get_latest_analytics_snapshot()
    ga4_line = "GA4: brak snapshotu w DB"
    has_snapshot = bool(snapshot)
    sync_status = (snapshot or {}).get("sync_status") if snapshot else None
    if snapshot:
        sources = json.loads(snapshot.get("sources_json") or "{}")
        zz = sources.get("zzpackage") or {}
        app = sources.get("app") or {}
        ga4_line = (
            f"GA4 ({snapshot['period']}): "
            f"wizard sessions={zz.get('sessions', 0)}, "
            f"conversions={zz.get('conversions', 0)}, "
            f"app sessions={app.get('sessions', 0)}"
        )

    cta_leads = _list_cta_band_leads(limit=MAX_SALES_CTA_TICKETS)
    return {
        "order_count": order_count,
        "revenue": revenue,
        "test_count": test_count,
        "unknown_count": unknown_count,
        "lead_count": lead_count,
        "ga4_line": ga4_line,
        "has_snapshot": has_snapshot,
        "sync_status": sync_status,
        "cta_leads": cta_leads,
    }


def build_weekly_brief(metrics: dict[str, Any] | None = None) -> str:
    """Compose a short operational brief for Dowódca (Telegram)."""
    m = metrics if metrics is not None else collect_weekly_metrics()
    return (
        "<b>Jadzia — weekly brief</b>\n"
        f"Orders KPI-eligible (7d): {m['order_count']} | EUR {m['revenue']:.2f}\n"
        f"Orders excluded: test={m['test_count']} unknown={m['unknown_count']}\n"
        f"Leads (7d): {m['lead_count']}\n"
        f"{m['ga4_line']}"
    )


def propose_brief_recommendations(metrics: dict[str, Any]) -> list[dict[str, str]]:
    """Derive 0–3 HITL draft recommendations from metrics (no side effects)."""
    recs: list[dict[str, str]] = []

    unknown = int(metrics.get("unknown_count") or 0)
    if unknown > 0:
        recs.append(
            {
                "code": "triage_unknown_orders",
                "title": "[Brief HITL] Triage unknown revenue classifications",
                "description": (
                    f"Weekly brief: {unknown} order(s) with unknown/null classification "
                    "in the last 7 days. Review reconcile dry-run; do NOT run "
                    "--apply-classifications without Dowódca review."
                ),
                "severity": "MEDIUM",
            }
        )

    if not metrics.get("has_snapshot"):
        recs.append(
            {
                "code": "analytics_snapshot_missing",
                "title": "[Brief HITL] Missing GA4 analytics snapshot",
                "description": (
                    "Weekly brief: no analytics snapshot in DB. "
                    "Run snapshot refresh on VPS when convenient."
                ),
                "severity": "LOW",
            }
        )
    elif metrics.get("sync_status") not in (None, "success"):
        status = metrics.get("sync_status") or "unknown"
        recs.append(
            {
                "code": "analytics_snapshot_health",
                "title": "[Brief HITL] Analytics snapshot health",
                "description": (
                    f"Weekly brief: GA4 snapshot issue (sync_status={status}). "
                    "Check INT-009 credentials/cache; no history replay."
                ),
                "severity": "MEDIUM",
            }
        )

    # Stable hygiene nudge when room remains (keeps strategy loop alive).
    if len(recs) < MAX_HITL_TICKETS:
        recs.append(
            {
                "code": "ops_fb_hygiene_nudge",
                "title": "[Brief HITL] FB smoke/test post hygiene",
                "description": (
                    "Weekly brief nudge: review OPS-FB-HYGIENE-01 checklist "
                    "(docs/handoffs/2026-07-18-ops-fb-hygiene-READY-for-human.md). "
                    "Human deletes smoke posts; agent does not act autonomously."
                ),
                "severity": "LOW",
            }
        )

    return recs[:MAX_HITL_TICKETS]


def propose_sales_cta_recommendations(
    metrics: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Derive 0–3 sales CTA HITL drafts from CTA-band leads (no side effects)."""
    from agent.customer_agent import (
        _DEFAULT_CTA_SKU,
        build_widget_wizard_deeplink,
    )

    m = metrics if metrics is not None else {}
    leads = list(m.get("cta_leads") or [])
    if not leads:
        leads = _list_cta_band_leads(limit=MAX_SALES_CTA_TICKETS)

    recs: list[dict[str, str]] = []
    for lead in leads[:MAX_SALES_CTA_TICKETS]:
        lead_id = int(lead.get("id") or 0)
        if lead_id <= 0:
            continue
        email = str(lead.get("email") or "").strip()
        score = int(lead.get("game_score") or 0)
        source = str(lead.get("source") or "unknown")
        cta_sku = _DEFAULT_CTA_SKU
        deeplink = build_widget_wizard_deeplink("caddy", cta_sku)
        email_hint = email if email else "(no email)"
        recs.append(
            {
                "code": "sales_cta_followup",
                "title": f"[Sales CTA] Follow up lead #{lead_id}",
                "description": (
                    f"Weekly brief sales CTA: follow up lead #{lead_id} "
                    f"({email_hint}), score={score}, source={source}.\n"
                    f"lead_id={lead_id}\n"
                    f"cta_sku={cta_sku}\n"
                    f"wizard_deeplink={deeplink}\n"
                    "HITL only — Ack/Snooze/Close in Commander; no auto pay."
                ),
                "severity": "HIGH" if score >= 80 else "MEDIUM",
                "lead_id": str(lead_id),
                "cta_sku": cta_sku,
                "wizard_deeplink": deeplink,
            }
        )
    return recs


def _open_brief_titles(source: str = BRIEF_HITL_SOURCE) -> set[str]:
    from agent.db import db_commander_list_tickets

    open_tickets = db_commander_list_tickets(status="open", limit=100)
    return {
        str(t.get("title") or "")
        for t in open_tickets
        if (t.get("source") or "") == source
    }


def _open_sales_cta_lead_ids() -> set[int]:
    """Lead ids already covered by open brief_sales_cta tickets."""
    from agent.db import db_commander_list_tickets

    open_tickets = db_commander_list_tickets(status="open", limit=100)
    found: set[int] = set()
    for ticket in open_tickets:
        if (ticket.get("source") or "") != BRIEF_SALES_CTA_SOURCE:
            continue
        parsed = parse_sales_cta_ticket_fields(str(ticket.get("description") or ""))
        lead_id = parsed.get("lead_id")
        if lead_id:
            found.add(int(lead_id))
    return found


def parse_sales_cta_ticket_fields(description: str) -> dict[str, str]:
    """Extract machine fields from sales CTA ticket description."""
    out: dict[str, str] = {}
    for line in (description or "").splitlines():
        line = line.strip()
        if line.startswith("lead_id="):
            out["lead_id"] = line.split("=", 1)[1].strip()
        elif line.startswith("cta_sku="):
            out["cta_sku"] = line.split("=", 1)[1].strip()
        elif line.startswith("wizard_deeplink="):
            out["wizard_deeplink"] = line.split("=", 1)[1].strip()
    return out


def spawn_brief_hitl_tickets(
    recommendations: list[dict[str, str]] | None = None,
    *,
    metrics: dict[str, Any] | None = None,
) -> list[int]:
    """
    Persist draft Commander tickets for Dowódca HITL approve.

    Does not execute SSH/publish/payments. Dedupes by open title+source.
    """
    from agent.db import db_commander_create_ticket

    recs = recommendations
    if recs is None:
        m = metrics if metrics is not None else collect_weekly_metrics()
        recs = propose_brief_recommendations(m)

    existing = _open_brief_titles()
    created: list[int] = []
    for rec in recs:
        title = rec["title"]
        if title in existing:
            logger.info("[BriefNode] skip duplicate HITL ticket title=%s", title)
            continue
        ticket_id = db_commander_create_ticket(
            title=title,
            description=rec["description"],
            source=BRIEF_HITL_SOURCE,
            severity=rec.get("severity", "MEDIUM"),
        )
        if ticket_id:
            created.append(int(ticket_id))
            existing.add(title)
            logger.info(
                "[BriefNode] HITL ticket created id=%s code=%s",
                ticket_id,
                rec.get("code"),
            )
    return created


def spawn_brief_sales_cta_tickets(
    recommendations: list[dict[str, str]] | None = None,
    *,
    metrics: dict[str, Any] | None = None,
) -> list[int]:
    """
    Persist sales CTA Commander tickets for Dowódca HITL.

    Does not execute SSH/publish/payments. Dedupes by open title+source and lead_id.
    """
    from agent.db import db_commander_create_ticket

    recs = recommendations
    if recs is None:
        m = metrics if metrics is not None else collect_weekly_metrics()
        recs = propose_sales_cta_recommendations(m)

    existing_titles = _open_brief_titles(BRIEF_SALES_CTA_SOURCE)
    existing_leads = _open_sales_cta_lead_ids()
    created: list[int] = []
    for rec in recs[:MAX_SALES_CTA_TICKETS]:
        title = rec["title"]
        lead_raw = rec.get("lead_id") or ""
        try:
            lead_id = int(lead_raw) if lead_raw else 0
        except (TypeError, ValueError):
            lead_id = 0
        if title in existing_titles or (lead_id and lead_id in existing_leads):
            logger.info(
                "[BriefNode] skip duplicate sales CTA title=%s lead_id=%s",
                title,
                lead_id or "-",
            )
            continue
        ticket_id = db_commander_create_ticket(
            title=title,
            description=rec["description"],
            source=BRIEF_SALES_CTA_SOURCE,
            severity=rec.get("severity", "MEDIUM"),
        )
        if ticket_id:
            created.append(int(ticket_id))
            existing_titles.add(title)
            if lead_id:
                existing_leads.add(lead_id)
            logger.info(
                "[BriefNode] sales CTA ticket created id=%s lead_id=%s code=%s",
                ticket_id,
                lead_id or "-",
                rec.get("code"),
            )
    return created


def send_weekly_brief() -> bool:
    """Send weekly brief to Telegram admin and spawn HITL draft tickets."""
    from agent.customer_agent import _send_telegram_alert_sync

    metrics = collect_weekly_metrics()
    message = build_weekly_brief(metrics)
    try:
        _send_telegram_alert_sync(message)
        ticket_ids = spawn_brief_hitl_tickets(metrics=metrics)
        sales_ids = spawn_brief_sales_cta_tickets(metrics=metrics)
        logger.info(
            "[BriefNode] Weekly brief sent; hitl_tickets=%s sales_cta_tickets=%s",
            ticket_ids,
            sales_ids,
        )
        return True
    except Exception as exc:
        logger.error("[BriefNode] Weekly brief failed: %s", exc)
        return False
