"""Circuit breakers — hard stops before Governance execute."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from agent.db import (
    db_list_active_quality_flags,
    db_rolling_net_margin_pct,
)
from agent.marketing.decision_engine import get_mb_mode
from agent.marketing.heuristics import MARGIN_FLOOR_PCT

logger = logging.getLogger(__name__)


@dataclass
class BreakerTrip:
    breaker_id: str
    message: str
    severity: str = "CRITICAL"


def evaluate_breakers(context: Optional[Dict[str, Any]] = None) -> List[BreakerTrip]:
    """Return list of tripped breakers (empty = clear)."""
    context = context or {}
    trips: List[BreakerTrip] = []
    mode = get_mb_mode()

    if mode == "shadow":
        trips.append(
            BreakerTrip(
                breaker_id="CB_SHADOW",
                message="MB_MODE=shadow — block all external side-effects",
                severity="ACTION",
            )
        )

    flags = db_list_active_quality_flags(limit=50)
    for f in flags:
        if f.get("source") == "ga4" and f.get("flag_type") == "stale" and f.get("severity") == "red":
            trips.append(
                BreakerTrip(
                    breaker_id="CB_DATA_STALE",
                    message="DTL GA4 stale — MB HOLD",
                )
            )
            break
        if f.get("source") == "l0_pixel" and f.get("severity") == "red":
            trips.append(
                BreakerTrip(
                    breaker_id="CB_PIXEL",
                    message="L0 pixel health red — block scale",
                )
            )
        if (
            f.get("source") == "vcms"
            and f.get("flag_type") == "ecosystem_red"
            and f.get("severity") in ("red", "critical")
        ):
            trips.append(
                BreakerTrip(
                    breaker_id="CB_ECOSYSTEM",
                    message="VCMS/KODA ecosystem red — MB HOLD (Brain Bus)",
                )
            )

    margin = db_rolling_net_margin_pct(limit=50)
    if margin is not None and margin < MARGIN_FLOOR_PCT:
        trips.append(
            BreakerTrip(
                breaker_id="CB_MARGIN_FLOOR",
                message=f"net_margin_pct {margin:.1%} < floor {MARGIN_FLOOR_PCT:.0%}",
            )
        )

    # Optional spend/CPA from context (paid Ads API PARK — only if facts present)
    spend = context.get("spend_daily_eur")
    spend_cap = context.get("spend_daily_cap_eur")
    if spend is not None and spend_cap is not None and float(spend) > float(spend_cap):
        trips.append(
            BreakerTrip(
                breaker_id="CB_SPEND_DAILY",
                message=f"daily spend {spend} > cap {spend_cap}",
            )
        )

    cpa_spike = context.get("cpa_spike_pct")
    if cpa_spike is not None and float(cpa_spike) >= 50.0:
        trips.append(
            BreakerTrip(
                breaker_id="CB_CPA_SPIKE",
                message=f"CPA spike +{cpa_spike}% in window",
            )
        )

    logger.info("[mb.breakers] trips=%s", [t.breaker_id for t in trips])
    return trips


def is_execute_allowed(context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    trips = evaluate_breakers(context)
    # CB_SHADOW always blocks execute; other CRITICAL/ACTION also block
    blocked = [t.breaker_id for t in trips]
    return {
        "allowed": len(trips) == 0,
        "trips": [
            {"breaker_id": t.breaker_id, "message": t.message, "severity": t.severity}
            for t in trips
        ],
        "blocked_by": blocked,
    }
