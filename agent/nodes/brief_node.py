"""Weekly COI brief — orders, leads, analytics snapshot summary + HITL drafts."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

BRIEF_HITL_SOURCE = "brief_hitl"
MAX_HITL_TICKETS = 3


def _utc_now() -> datetime:
    return datetime.now(UTC)


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

    return {
        "order_count": order_count,
        "revenue": revenue,
        "test_count": test_count,
        "unknown_count": unknown_count,
        "lead_count": lead_count,
        "ga4_line": ga4_line,
        "has_snapshot": has_snapshot,
        "sync_status": sync_status,
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


def _open_brief_titles() -> set[str]:
    from agent.db import db_commander_list_tickets

    open_tickets = db_commander_list_tickets(status="open", limit=100)
    return {
        str(t.get("title") or "")
        for t in open_tickets
        if (t.get("source") or "") == BRIEF_HITL_SOURCE
    }


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


def send_weekly_brief() -> bool:
    """Send weekly brief to Telegram admin and spawn HITL draft tickets."""
    from agent.customer_agent import _send_telegram_alert_sync

    metrics = collect_weekly_metrics()
    message = build_weekly_brief(metrics)
    try:
        _send_telegram_alert_sync(message)
        ticket_ids = spawn_brief_hitl_tickets(metrics=metrics)
        logger.info(
            "[BriefNode] Weekly brief sent; hitl_tickets=%s",
            ticket_ids,
        )
        return True
    except Exception as exc:
        logger.error("[BriefNode] Weekly brief failed: %s", exc)
        return False
