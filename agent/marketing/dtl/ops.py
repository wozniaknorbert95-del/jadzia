"""Orders + leads ops ingest → DTL raw + facts."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from agent.db import (
    db_insert_marketing_raw_ingest,
    db_list_leads,
    db_list_orders,
    db_upsert_marketing_fact,
)
from agent.marketing.dtl.checksum import payload_checksum

logger = logging.getLogger(__name__)

WINDOW = "snapshot"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ingest_orders_snapshot(limit: int = 200) -> Dict[str, Any]:
    as_of = _utc_now()
    orders = db_list_orders(limit=limit)
    total_gross = sum(float(o.get("total_gross") or 0) for o in orders)
    by_status: Dict[str, int] = {}
    for o in orders:
        st = o.get("status") or "unknown"
        by_status[st] = by_status.get(st, 0) + 1

    payload = {
        "count": len(orders),
        "total_gross": total_gross,
        "by_status": by_status,
        "latest_updated_at": orders[0].get("updated_at") if orders else None,
    }
    ingest_id = db_insert_marketing_raw_ingest(
        {
            "source": "orders",
            "fetched_at": as_of,
            "checksum": payload_checksum(payload),
            "payload": payload,
            "window_label": WINDOW,
            "status": "ok",
        }
    )
    for metric_key, value in (
        ("ops_orders_count", float(len(orders))),
        ("ops_orders_gross_sum", float(total_gross)),
    ):
        db_upsert_marketing_fact(
            {
                "metric_key": metric_key,
                "channel": "all",
                "window_label": WINDOW,
                "value": value,
                "confidence": 1.0,
                "as_of": as_of,
                "source_ingest_id": ingest_id,
            }
        )
    logger.info("[dtl.ops] orders count=%s ingest_id=%s", len(orders), ingest_id)
    return {
        "source": "orders",
        "status": "ok",
        "ingest_id": ingest_id,
        "count": len(orders),
        "as_of": as_of,
    }


def ingest_leads_snapshot(limit: int = 200) -> Dict[str, Any]:
    as_of = _utc_now()
    leads = db_list_leads(limit=limit)
    by_source: Dict[str, int] = {}
    open_count = 0
    for lead in leads:
        src = lead.get("source") or "unknown"
        by_source[src] = by_source.get(src, 0) + 1
        if (lead.get("disposition") or "open") == "open":
            open_count += 1

    payload = {
        "count": len(leads),
        "open_count": open_count,
        "by_source": by_source,
        "latest_updated_at": leads[0].get("updated_at") if leads else None,
    }
    ingest_id = db_insert_marketing_raw_ingest(
        {
            "source": "leads",
            "fetched_at": as_of,
            "checksum": payload_checksum(payload),
            "payload": payload,
            "window_label": WINDOW,
            "status": "ok",
        }
    )
    for metric_key, value in (
        ("ops_leads_count", float(len(leads))),
        ("ops_leads_open", float(open_count)),
    ):
        db_upsert_marketing_fact(
            {
                "metric_key": metric_key,
                "channel": "all",
                "window_label": WINDOW,
                "value": value,
                "confidence": 1.0,
                "as_of": as_of,
                "source_ingest_id": ingest_id,
            }
        )
    for src, count in by_source.items():
        db_upsert_marketing_fact(
            {
                "metric_key": "ops_leads_by_source",
                "channel": src,
                "window_label": WINDOW,
                "value": float(count),
                "confidence": 1.0,
                "as_of": as_of,
                "source_ingest_id": ingest_id,
            }
        )
    logger.info("[dtl.ops] leads count=%s ingest_id=%s", len(leads), ingest_id)
    return {
        "source": "leads",
        "status": "ok",
        "ingest_id": ingest_id,
        "count": len(leads),
        "as_of": as_of,
    }
