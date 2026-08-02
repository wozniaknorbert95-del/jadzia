"""Speed-to-lead monitor — OS B.6 / A2A SLA (measure only, no auto-DM)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.demand_os.a2a_bus import list_handoffs

HOT_SLA_MIN = 15
OVERNIGHT_MIN = 60 * 12


def _parse_ts(raw: str) -> Optional[datetime]:
    if not raw:
        return None
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _median(vals: List[float]) -> Optional[float]:
    if not vals:
        return None
    s = sorted(vals)
    n = len(s)
    mid = n // 2
    if n % 2:
        return round(s[mid], 2)
    return round((s[mid - 1] + s[mid]) / 2.0, 2)


def stl_report(*, bus_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Open hot ages + median SLA on acked engage_event/lead_hot (emit→ack).
    """
    items = list_handoffs(path=bus_path) if bus_path else list_handoffs()
    now = datetime.now(timezone.utc)
    hot_types = {"engage_event", "lead_hot"}
    scored: List[Dict[str, Any]] = []
    closed_ages: List[float] = []
    breaches = 0
    overnight = 0
    for h in items:
        ht = h.get("handoff_type") or h.get("type")
        if ht not in hot_types:
            continue
        status = (h.get("status") or "emitted").lower()
        ts = _parse_ts(h.get("ts") or h.get("created_at") or "")
        ack = _parse_ts(h.get("acked_at") or "")
        if status in ("acked", "done", "closed") and ts and ack:
            closed_ages.append((ack - ts).total_seconds() / 60.0)
            continue
        if status in ("acked", "done", "closed"):
            # prefer elapsed_minutes if present
            if h.get("elapsed_minutes") is not None:
                try:
                    closed_ages.append(float(h["elapsed_minutes"]))
                except (TypeError, ValueError):
                    pass
            continue
        age_min = None
        bucket = "unknown"
        if ts:
            age_min = round((now - ts).total_seconds() / 60.0, 1)
            if age_min <= 5:
                bucket = "lt5"
            elif age_min <= HOT_SLA_MIN:
                bucket = "lt15"
            elif age_min <= OVERNIGHT_MIN:
                bucket = "late"
                breaches += 1
            else:
                bucket = "overnight"
                breaches += 1
                overnight += 1
        scored.append(
            {
                "id": h.get("id"),
                "handoff_type": ht,
                "age_min": age_min,
                "bucket": bucket,
                "asset_id": h.get("asset_id"),
            }
        )
    median = _median(closed_ages)
    return {
        "ok": True,
        "open_hot": len(scored),
        "sla_min": HOT_SLA_MIN,
        "breaches": breaches,
        "overnight": overnight,
        "closed_hot": len(closed_ages),
        "median_min": median,
        "items": scored[:50],
        "kpi": "hot→Wizard median · zero overnight",
        "marketing": "PARKED_LAST",
    }
