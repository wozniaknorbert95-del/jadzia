"""GA4 snapshot → DTL raw + facts (reuses analytics_node / ga4_client)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from agent.db import (
    db_insert_marketing_raw_ingest,
    db_insert_quality_flag,
    db_deactivate_quality_flags,
    db_upsert_marketing_fact,
)
from agent.marketing.dtl.checksum import payload_checksum

logger = logging.getLogger(__name__)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _period_label(days: int) -> str:
    if days <= 1:
        return "last_1_day"
    return f"last_{days}_days"


def ingest_ga4_snapshot(period_days: int = 7) -> Dict[str, Any]:
    """
    Fetch GA4 via analytics_node, append raw ingest, write normalized facts.
    Does not invent metrics when GA4 is unconfigured — flags missing/api_error.
    """
    from agent.nodes.analytics_node import fetch_analytics_snapshot

    as_of = _utc_now()
    window = _period_label(period_days)
    source = "ga4"

    try:
        snapshot = fetch_analytics_snapshot(period_days=period_days)
    except Exception as exc:
        logger.error("[dtl.ga4] fetch failed: %s", exc)
        ingest_id = db_insert_marketing_raw_ingest(
            {
                "source": source,
                "fetched_at": as_of,
                "checksum": payload_checksum({"error": str(exc)}),
                "payload": {"error": str(exc)},
                "window_label": window,
                "status": "error",
                "error_message": str(exc),
            }
        )
        db_insert_quality_flag(
            {
                "flag_type": "api_error",
                "source": source,
                "severity": "red",
                "message": f"GA4 fetch exception: {exc}",
                "as_of": as_of,
                "details": {"ingest_id": ingest_id},
            }
        )
        return {"source": source, "status": "error", "as_of": as_of, "error": str(exc)}

    clean_errors = [str(e) for e in (snapshot.errors or [])]
    payload = {
        "sync_status": snapshot.sync_status,
        "generated_at": snapshot.generated_at,
        "period": snapshot.period,
        "sources": snapshot.sources.model_dump() if snapshot.sources else {},
        "errors": clean_errors,
    }

    status = "ok" if snapshot.sync_status == "success" else snapshot.sync_status
    if status == "fail":
        status = "error"

    checksum = payload_checksum(payload)
    ingest_id = db_insert_marketing_raw_ingest(
        {
            "source": source,
            "fetched_at": as_of,
            "checksum": checksum,
            "payload": payload,
            "window_label": window,
            "status": status,
            "error_message": None if status == "ok" else snapshot.sync_status,
        }
    )

    sources = payload.get("sources") or {}
    zz = sources.get("zzpackage") or {}
    app = sources.get("app") or {}

    fact_rows = [
        ("ga4_zz_sessions", "wizard", zz.get("sessions")),
        ("ga4_zz_conversions", "wizard", zz.get("conversions")),
        ("ga4_zz_purchase_revenue", "wizard", zz.get("purchase_revenue")),
        ("ga4_zz_aov", "wizard", zz.get("aov")),
        ("ga4_app_sessions", "app", app.get("sessions")),
        ("ga4_app_active_users", "app", app.get("active_users")),
        ("ga4_app_lead_captured", "app", app.get("lead_captured")),
    ]

    confidence = 1.0
    if snapshot.sync_status == "degraded":
        confidence = 0.6
    elif snapshot.sync_status == "fail":
        confidence = 0.0

    written = 0
    for metric_key, channel, raw_val in fact_rows:
        if raw_val is None:
            continue
        db_upsert_marketing_fact(
            {
                "metric_key": metric_key,
                "channel": channel,
                "window_label": window,
                "value": float(raw_val),
                "confidence": confidence,
                "as_of": as_of,
                "source_ingest_id": ingest_id,
                "dims": {"period": snapshot.period},
            }
        )
        written += 1

    if snapshot.sync_status == "fail":
        db_insert_quality_flag(
            {
                "flag_type": "api_error",
                "source": source,
                "severity": "red",
                "message": "GA4 sync_status=fail — no usable sources",
                "as_of": as_of,
                "details": {"errors": clean_errors, "ingest_id": ingest_id},
            }
        )
    elif snapshot.sync_status == "degraded":
        db_insert_quality_flag(
            {
                "flag_type": "missing",
                "source": source,
                "severity": "amber",
                "message": "GA4 degraded — partial sources",
                "as_of": as_of,
                "details": {"errors": clean_errors, "ingest_id": ingest_id},
            }
        )
    else:
        db_deactivate_quality_flags(source, "api_error")
        db_deactivate_quality_flags(source, "missing")

    logger.info(
        "[dtl.ga4] status=%s facts=%s ingest_id=%s",
        snapshot.sync_status,
        written,
        ingest_id,
    )
    return {
        "source": source,
        "status": status,
        "ingest_id": ingest_id,
        "facts_written": written,
        "sync_status": snapshot.sync_status,
        "as_of": as_of,
    }
