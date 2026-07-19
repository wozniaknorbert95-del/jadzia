"""Data quality evaluation after ingest — freshness + margin coverage."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agent.commander.sla import freshness_status
from agent.db import (
    db_get_latest_marketing_raw_ingest,
    db_insert_quality_flag,
    db_deactivate_quality_flags,
    db_margin_coverage_stats,
)

logger = logging.getLogger(__name__)

# Sources evaluated for stale flags (aligned with FRESHNESS_SLA keys where possible)
STALE_SOURCES = ("ga4", "orders", "leads", "l0_pixel", "attribution", "margin")

MARGIN_COVERAGE_FLOOR_PCT = 90.0


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def evaluate_freshness_flags() -> List[Dict[str, Any]]:
    """Raise/clear stale flags based on latest raw ingest timestamps."""
    as_of = _utc_now()
    raised: List[Dict[str, Any]] = []
    for source in STALE_SOURCES:
        latest = db_get_latest_marketing_raw_ingest(source)
        last_at = latest.get("fetched_at") if latest else None
        fresh = freshness_status(source, last_at)
        if fresh["status"] == "red":
            flag = {
                "flag_type": "stale",
                "source": source,
                "severity": "red",
                "message": f"DTL source {source} stale or missing",
                "as_of": as_of,
                "details": fresh,
            }
            db_insert_quality_flag(flag)
            raised.append(flag)
        elif fresh["status"] == "amber":
            flag = {
                "flag_type": "stale",
                "source": source,
                "severity": "amber",
                "message": f"DTL source {source} aging",
                "as_of": as_of,
                "details": fresh,
            }
            db_insert_quality_flag(flag)
            raised.append(flag)
        else:
            db_deactivate_quality_flags(source, "stale")
    return raised


def evaluate_margin_coverage_flag() -> Optional[Dict[str, Any]]:
    """Flag when margin fact coverage < floor (empty orders → no flag)."""
    as_of = _utc_now()
    stats = db_margin_coverage_stats()
    total = stats["orders_total"]
    if total == 0:
        db_deactivate_quality_flags("margin", "low_coverage")
        return None
    if stats["coverage_pct"] < MARGIN_COVERAGE_FLOOR_PCT:
        flag = {
            "flag_type": "low_coverage",
            "source": "margin",
            "severity": "amber",
            "message": (
                f"Margin coverage {stats['coverage_pct']}% "
                f"< {MARGIN_COVERAGE_FLOOR_PCT}% floor"
            ),
            "as_of": as_of,
            "details": stats,
        }
        db_insert_quality_flag(flag)
        return flag
    db_deactivate_quality_flags("margin", "low_coverage")
    return None


def run_quality_pass() -> Dict[str, Any]:
    stale = evaluate_freshness_flags()
    margin = evaluate_margin_coverage_flag()
    logger.info(
        "[dtl.quality] stale_flags=%s margin_flag=%s",
        len(stale),
        bool(margin),
    )
    return {
        "stale_flags": len(stale),
        "margin_flag": margin is not None,
        "margin_stats": db_margin_coverage_stats(),
    }
