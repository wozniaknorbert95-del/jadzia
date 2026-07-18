"""Weekly COI brief — orders, leads, analytics snapshot summary."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime, timedelta

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(UTC)


def build_weekly_brief() -> str:
    """Compose a short operational brief for Dowódca (Telegram)."""
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

    return (
        "<b>Jadzia — weekly brief</b>\n"
        f"Orders KPI-eligible (7d): {order_count} | EUR {revenue:.2f}\n"
        f"Orders excluded: test={test_count} unknown={unknown_count}\n"
        f"Leads (7d): {lead_count}\n"
        f"{ga4_line}"
    )


def send_weekly_brief() -> bool:
    """Send weekly brief to Telegram admin (or Discord fallback)."""
    from agent.customer_agent import _send_telegram_alert_sync

    message = build_weekly_brief()
    try:
        _send_telegram_alert_sync(message)
        logger.info("[BriefNode] Weekly brief sent")
        return True
    except Exception as exc:
        logger.error("[BriefNode] Weekly brief failed: %s", exc)
        return False
