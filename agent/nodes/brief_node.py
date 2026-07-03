"""Weekly COI brief — orders, leads, analytics snapshot summary."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def build_weekly_brief() -> str:
    """Compose a short operational brief for Dowódca (Telegram)."""
    from agent.db import db_get_latest_analytics_snapshot, get_connection

    since = (_utc_now() - timedelta(days=7)).replace(microsecond=0).isoformat()
    conn = get_connection()

    orders_row = conn.execute(
        """
        SELECT COUNT(*) AS cnt, COALESCE(SUM(total_gross), 0) AS revenue
        FROM orders
        WHERE created_at >= ?
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
        f"Orders (7d): {order_count} | EUR {revenue:.2f}\n"
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
