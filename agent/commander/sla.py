"""SLA and freshness calculations."""

from __future__ import annotations

import json
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


def dtl_ingest_fetched_at(source: str) -> Optional[str]:
    """Clock for pipeline freshness = last DTL raw ingest fetch (not business event time)."""
    from agent.db import db_get_latest_marketing_raw_ingest

    latest = db_get_latest_marketing_raw_ingest(source)
    if not latest:
        return None
    return latest.get("fetched_at")


def worker_heartbeat_at() -> Optional[str]:
    """
    Worker freshness clock = last successful commander health probe.

    Must NOT use dowodca_last_active_at (HITL session / escalation N6).
    Fallback: newest DTL ingest among ga4/orders/leads.
    """
    from agent.db import db_commander_get_setting

    row = db_commander_get_setting("health:last_ok")
    if row:
        try:
            value = json.loads(row["value_json"])
            if value:
                return str(value)
        except (json.JSONDecodeError, TypeError, KeyError):
            pass

    times: list[str] = []
    for source in ("ga4", "orders", "leads"):
        fetched = dtl_ingest_fetched_at(source)
        if fetched:
            times.append(fetched)
    if not times:
        return None
    return max(times, key=lambda t: _parse_ts(t) or datetime.min.replace(tzinfo=timezone.utc))
