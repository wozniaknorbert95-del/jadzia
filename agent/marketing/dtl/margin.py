"""Order margin facts v1 — playbook 60% gross margin → COGS 40%."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from agent.db import (
    db_insert_marketing_raw_ingest,
    db_list_orders_full,
    db_upsert_marketing_fact,
    db_upsert_order_margin_fact,
)
from agent.marketing.dtl.attribution import channel_from_attribution
from agent.marketing.dtl.checksum import payload_checksum

logger = logging.getLogger(__name__)

GROSS_MARGIN_PCT = 0.60
COGS_METHOD = "playbook_60pct"
WINDOW = "all_time"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def calc_margin_v1(
    gross: float,
    shipping: float = 0.0,
    refunds_alloc: float = 0.0,
) -> Dict[str, float]:
    """
    Playbook: minimum 60% gross margin → COGS = 40% of gross.
    net_margin = gross - cogs - shipping - refunds_alloc
    """
    gross = float(gross or 0)
    shipping = float(shipping or 0)
    refunds_alloc = float(refunds_alloc or 0)
    cogs = round(gross * (1.0 - GROSS_MARGIN_PCT), 4)
    net_margin = round(gross - cogs - shipping - refunds_alloc, 4)
    net_margin_pct = round((net_margin / gross), 6) if gross > 0 else 0.0
    return {
        "gross": gross,
        "cogs": cogs,
        "shipping": shipping,
        "refunds_alloc": refunds_alloc,
        "net_margin": net_margin,
        "net_margin_pct": net_margin_pct,
    }


def ingest_order_margins(limit: int = 500) -> Dict[str, Any]:
    """Build/upsert margin facts for orders currently in SQLite."""
    as_of = _utc_now()
    orders = db_list_orders_full(limit=limit)
    written = 0
    skipped = 0
    net_sum = 0.0
    for order in orders:
        order_id = order.get("order_id")
        if not order_id:
            skipped += 1
            continue
        calc = calc_margin_v1(float(order.get("total_gross") or 0))
        channel = channel_from_attribution(order.get("attribution") or {})
        ok = db_upsert_order_margin_fact(
            {
                "order_id": order_id,
                **calc,
                "cogs_method": COGS_METHOD,
                "attribution_channel": channel,
                "as_of": as_of,
            }
        )
        if ok:
            written += 1
            net_sum += calc["net_margin"]
        else:
            skipped += 1

    payload = {
        "orders_scanned": len(orders),
        "written": written,
        "skipped": skipped,
        "net_margin_sum": net_sum,
        "cogs_method": COGS_METHOD,
    }
    ingest_id = db_insert_marketing_raw_ingest(
        {
            "source": "margin",
            "fetched_at": as_of,
            "checksum": payload_checksum(payload),
            "payload": payload,
            "window_label": WINDOW,
            "status": "ok",
        }
    )
    db_upsert_marketing_fact(
        {
            "metric_key": "margin_net_sum",
            "channel": "all",
            "window_label": WINDOW,
            "value": float(net_sum),
            "confidence": 1.0,
            "as_of": as_of,
            "source_ingest_id": ingest_id,
            "dims": {"cogs_method": COGS_METHOD},
        }
    )
    db_upsert_marketing_fact(
        {
            "metric_key": "margin_facts_count",
            "channel": "all",
            "window_label": WINDOW,
            "value": float(written),
            "confidence": 1.0,
            "as_of": as_of,
            "source_ingest_id": ingest_id,
        }
    )
    logger.info(
        "[dtl.margin] wrote=%s skipped=%s orders_scanned=%s",
        written,
        skipped,
        len(orders),
    )
    return {
        "source": "margin",
        "status": "ok",
        "ingest_id": ingest_id,
        "written": written,
        "skipped": skipped,
        "as_of": as_of,
    }
