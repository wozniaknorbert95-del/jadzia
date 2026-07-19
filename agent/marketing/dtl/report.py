"""Commander Data Health report — analytics only (no HITL approvals)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from agent.commander.sla import freshness_status
from agent.db import (
    db_get_latest_marketing_raw_ingest,
    db_list_active_quality_flags,
    db_list_marketing_facts,
    db_margin_coverage_stats,
)

DTL_SOURCES = ("ga4", "orders", "leads", "l0_pixel", "attribution", "margin")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_data_health_report() -> Dict[str, Any]:
    """Aggregate freshness, quality flags, margin coverage, recent facts."""
    freshness: Dict[str, Any] = {}
    for source in DTL_SOURCES:
        latest = db_get_latest_marketing_raw_ingest(source)
        last_at = latest.get("fetched_at") if latest else None
        entry = freshness_status(source, last_at)
        entry["ingest_status"] = latest.get("status") if latest else None
        entry["checksum"] = latest.get("checksum") if latest else None
        freshness[source] = entry

    flags = db_list_active_quality_flags(limit=50)
    margin = db_margin_coverage_stats()
    recent_facts = db_list_marketing_facts(limit=40)

    critical = sum(1 for f in flags if f.get("severity") in ("critical", "red"))
    amber = sum(1 for f in flags if f.get("severity") == "amber")

    if critical:
        overall = "red"
    elif amber:
        overall = "amber"
    elif any(freshness[s]["status"] == "red" for s in DTL_SOURCES):
        overall = "red"
    elif any(freshness[s]["status"] == "amber" for s in DTL_SOURCES):
        overall = "amber"
    else:
        overall = "ok"

    return {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "freshness": freshness,
        "quality_flags": flags,
        "quality_summary": {
            "active_total": len(flags),
            "critical_or_red": critical,
            "amber": amber,
        },
        "margin_coverage": margin,
        "recent_facts": recent_facts,
        "panel": "data_health",
        "note": "Analytics only — MB decisions / Telegram HITL are F1+",
    }
