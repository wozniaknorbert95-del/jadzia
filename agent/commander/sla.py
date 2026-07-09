"""SLA and freshness calculations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Optional

from agent.commander.constants import FRESHNESS_SLA_SECONDS, QUEUE_SLA_HOURS


def _parse_ts(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def sla_status_for_age_hours(age_hours: float, queue_type: str) -> str:
    """Return ok | amber | red."""
    sla = QUEUE_SLA_HOURS.get(queue_type, 24)
    amber_at = sla / 2
    if age_hours >= sla:
        return "red"
    if age_hours >= amber_at:
        return "amber"
    return "ok"


def freshness_status(source: str, last_sync_at: Optional[str]) -> Dict:
    amber_s, red_s = FRESHNESS_SLA_SECONDS.get(source, (1800, 7200))
    dt = _parse_ts(last_sync_at)
    now = datetime.now(timezone.utc)
    if not dt:
        return {
            "source": source,
            "staleness_seconds": None,
            "status": "red",
            "last_sync_at": None,
        }
    staleness = int((now - dt).total_seconds())
    if staleness >= red_s:
        status = "red"
    elif staleness >= amber_s:
        status = "amber"
    else:
        status = "ok"
    return {
        "source": source,
        "staleness_seconds": staleness,
        "status": status,
        "last_sync_at": last_sync_at,
    }
