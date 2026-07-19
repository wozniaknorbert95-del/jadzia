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


def _drivers(
    *,
    freshness: Dict[str, Any],
    flags: List[Dict[str, Any]],
    overall: str,
) -> List[Dict[str, Any]]:
    """Human-readable list of what drives overall_status (no secrets)."""
    out: List[Dict[str, Any]] = []
    for source, entry in freshness.items():
        st = entry.get("status")
        if st in ("red", "amber"):
            out.append(
                {
                    "kind": "freshness",
                    "source": source,
                    "severity": st,
                    "message": f"ingest freshness={st}",
                }
            )
    for f in flags:
        sev = (f.get("severity") or "").lower()
        if sev in ("critical", "red", "amber"):
            out.append(
                {
                    "kind": "quality_flag",
                    "source": f.get("source"),
                    "flag_type": f.get("flag_type"),
                    "severity": sev,
                    "message": f.get("message"),
                }
            )
    if not out and overall == "ok":
        out.append(
            {
                "kind": "ok",
                "source": "all",
                "severity": "ok",
                "message": "No red/amber drivers (info/park acks ignored)",
            }
        )
    return out


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
    info = sum(1 for f in flags if f.get("severity") == "info")

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

    drivers = _drivers(freshness=freshness, flags=flags, overall=overall)

    return {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "freshness": freshness,
        "quality_flags": flags,
        "quality_summary": {
            "active_total": len(flags),
            "critical_or_red": critical,
            "amber": amber,
            "info": info,
        },
        "drivers": drivers,
        "conscious_parks": [
            {
                "id": "l0_purchase",
                "status": "PARK",
                "reason": "Mollie GO required — not a Data Health failure",
            },
            {
                "id": "ads_api_create",
                "status": "PARK",
                "reason": "MB ticket_only / paste-ready only",
            },
        ],
        "margin_coverage": margin,
        "recent_facts": recent_facts,
        "panel": "data_health",
        "note": (
            "Analytics only — info/park flags do not set overall amber/red. "
            "Set L0_IC_VERIFIED=1 after Events Manager InitiateCheckout PASS."
        ),
    }
