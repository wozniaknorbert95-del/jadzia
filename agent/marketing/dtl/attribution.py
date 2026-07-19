"""Attribution L1–L2: UTM → session stitch → order facts."""

from __future__ import annotations

import logging
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agent.db import (
    db_insert_marketing_raw_ingest,
    db_list_orders_full,
    db_upsert_marketing_fact,
)
from agent.marketing.dtl.checksum import payload_checksum

logger = logging.getLogger(__name__)

WINDOW = "all_time"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def channel_from_attribution(attr: Dict[str, Any]) -> str:
    """L1 last-touch channel label from order attribution_json."""
    if not attr:
        return "unknown"
    source = (
        attr.get("utm_source")
        or attr.get("last_touch_source")
        or attr.get("first_touch_source")
        or ""
    )
    medium = (
        attr.get("utm_medium")
        or attr.get("last_touch_medium")
        or attr.get("first_touch_medium")
        or ""
    )
    source = str(source).strip().lower()
    medium = str(medium).strip().lower()
    if not source:
        return "unknown"
    if medium:
        return f"{source}/{medium}"
    return source


def session_key_from_order(order: Dict[str, Any]) -> Optional[str]:
    """
    L2 session stitch key.
    Prefer ga_client_id (cross-order), then checkout_id (1:1 Wizard session).
    """
    attr = order.get("attribution") or {}
    ga_cid = (attr.get("ga_client_id") or "").strip()
    if ga_cid:
        return f"ga:{ga_cid}"
    checkout_id = (order.get("checkout_id") or "").strip()
    if checkout_id:
        return f"checkout:{checkout_id}"
    return None


def build_attribution_chains(orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Group orders by session key; emit L1 channel + L2 touch path."""
    by_session: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    orphans: List[Dict[str, Any]] = []

    for order in orders:
        sk = session_key_from_order(order)
        channel = channel_from_attribution(order.get("attribution") or {})
        touch = {
            "order_id": order.get("order_id"),
            "channel": channel,
            "created_at": order.get("created_at"),
            "utm_source": (order.get("attribution") or {}).get("utm_source"),
            "utm_medium": (order.get("attribution") or {}).get("utm_medium"),
            "utm_campaign": (order.get("attribution") or {}).get("utm_campaign"),
        }
        if sk:
            by_session[sk].append(touch)
        else:
            orphans.append(touch)

    chains: List[Dict[str, Any]] = []
    for session_id, touches in by_session.items():
        touches_sorted = sorted(touches, key=lambda t: t.get("created_at") or "")
        channels = [t["channel"] for t in touches_sorted if t.get("channel")]
        last_channel = channels[-1] if channels else "unknown"
        unique_channels = list(dict.fromkeys(channels))
        chains.append(
            {
                "session_id": session_id,
                "order_ids": [t["order_id"] for t in touches_sorted],
                "touch_path": touches_sorted,
                "last_touch_channel": last_channel,
                "assisted": len(unique_channels) >= 2,
                "level": "L2",
            }
        )
    for touch in orphans:
        chains.append(
            {
                "session_id": None,
                "order_ids": [touch.get("order_id")],
                "touch_path": [touch],
                "last_touch_channel": touch.get("channel") or "unknown",
                "assisted": False,
                "level": "L1",
            }
        )
    return chains


def ingest_attribution(limit: int = 500) -> Dict[str, Any]:
    """Persist attribution rollup facts from orders (L1 + L2)."""
    as_of = _utc_now()
    orders = db_list_orders_full(limit=limit)
    chains = build_attribution_chains(orders)

    channel_counts: Counter = Counter()
    l2_count = 0
    assisted_count = 0
    for chain in chains:
        channel_counts[chain["last_touch_channel"]] += len(chain.get("order_ids") or [])
        if chain.get("level") == "L2":
            l2_count += 1
        if chain.get("assisted"):
            assisted_count += 1

    payload = {
        "orders_scanned": len(orders),
        "chains": len(chains),
        "l2_sessions": l2_count,
        "assisted_conversions": assisted_count,
        "by_channel": dict(channel_counts),
        "sample_chains": chains[:20],
    }
    checksum = payload_checksum(payload)
    ingest_id = db_insert_marketing_raw_ingest(
        {
            "source": "attribution",
            "fetched_at": as_of,
            "checksum": checksum,
            "payload": payload,
            "window_label": WINDOW,
            "status": "ok",
        }
    )

    total_orders = len(orders) or 0
    known_orders = sum(v for k, v in channel_counts.items() if k != "unknown")
    coverage = (known_orders / total_orders) if total_orders else 0.0

    facts = [
        ("orders_total", "all", float(total_orders)),
        ("orders_attributed_l1", "all", float(known_orders)),
        ("attribution_coverage_pct", "all", round(coverage * 100.0, 2)),
        ("attribution_l2_sessions", "all", float(l2_count)),
        ("assisted_conversions", "all", float(assisted_count)),
    ]
    for channel, count in channel_counts.items():
        facts.append(("orders_by_last_touch", channel, float(count)))

    for metric_key, channel, value in facts:
        db_upsert_marketing_fact(
            {
                "metric_key": metric_key,
                "channel": channel,
                "window_label": WINDOW,
                "value": value,
                "confidence": 1.0 if total_orders else 0.0,
                "as_of": as_of,
                "source_ingest_id": ingest_id,
                "dims": {"layer": "L1-L2"},
            }
        )

    logger.info(
        "[dtl.attribution] orders=%s l2=%s coverage=%.1f%%",
        total_orders,
        l2_count,
        coverage * 100.0,
    )
    return {
        "source": "attribution",
        "status": "ok",
        "ingest_id": ingest_id,
        "orders_scanned": total_orders,
        "l2_sessions": l2_count,
        "coverage_pct": round(coverage * 100.0, 2),
        "as_of": as_of,
    }
