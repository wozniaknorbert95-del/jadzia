"""Analytics API routes — INT-009 GA4 snapshot."""

from __future__ import annotations

import json
import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import verify_jwt
from core.models import AnalyticsSnapshotResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analytics"])

_PERIOD_DAYS: dict[str, int] = {
    "1d": 1,
    "7d": 7,
    "30d": 30,
}


@router.get("/api/v1/analytics/snapshot", response_model=AnalyticsSnapshotResponse)
async def get_analytics_snapshot(
    period: Literal["1d", "7d", "30d"] = Query(default="7d"),
    _auth=Depends(verify_jwt),
) -> AnalyticsSnapshotResponse:
    """Return aggregated GA4 metrics for app + zzpackage (INT-009)."""
    from agent.nodes.analytics_node import fetch_analytics_snapshot

    period_days = _PERIOD_DAYS[period]
    result = fetch_analytics_snapshot(period_days=period_days)

    if result.sync_status == "fail":
        logger.error(
            "[AnalyticsAPI] Snapshot failed period=%s errors=%s",
            period,
            result.errors,
        )
        raise HTTPException(status_code=503, detail={"sync_status": "fail", "errors": result.errors})

    return result


@router.get("/api/v1/analytics/snapshots")
async def list_analytics_snapshots(
    limit: int = Query(default=30, ge=1, le=200),
    _auth=Depends(verify_jwt),
) -> dict:
    """Return persisted GA4 snapshot history (newest first)."""
    from agent.db import db_list_analytics_snapshots

    rows = db_list_analytics_snapshots(limit=limit)
    items = []
    for row in rows:
        items.append(
            {
                "id": row["id"],
                "period": row["period"],
                "generated_at": row["generated_at"],
                "sync_status": row["sync_status"],
                "sources": json.loads(row.get("sources_json") or "{}"),
                "errors": json.loads(row.get("errors_json") or "[]"),
                "created_at": row["created_at"],
            }
        )
    return {"snapshots": items, "total": len(items)}
