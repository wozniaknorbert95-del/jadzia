"""Analytics snapshot node — INT-009 GA4 aggregation."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Dict

from cachetools import TTLCache

from core import ga4_client
from core.ga4_client import Ga4NotConfiguredError
from core.models import (
    AnalyticsSnapshotResponse,
    AnalyticsSnapshotSources,
    AnalyticsSourceAppMetrics,
    AnalyticsSourceZzpackageMetrics,
)

logger = logging.getLogger(__name__)

_DEFAULT_TTL = 900
_cache: TTLCache[int, AnalyticsSnapshotResponse] = TTLCache(
    maxsize=8,
    ttl=int(os.getenv("GA4_CACHE_TTL_SECONDS", str(_DEFAULT_TTL))),
)

_PERIOD_LABELS: Dict[int, str] = {
    1: "last_1_day",
    7: "last_7_days",
    30: "last_30_days",
}


def _period_label(days: int) -> str:
    return _PERIOD_LABELS.get(days, f"last_{days}_days")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def fetch_analytics_snapshot(period_days: int = 7) -> AnalyticsSnapshotResponse:
    """
    Build GA4 snapshot for app + zzpackage properties.

    Agent card output: sync_status, sources, errors.
    """
    if period_days in _cache:
        logger.info("[AnalyticsNode] Cache hit period_days=%s", period_days)
        return _cache[period_days]

    if not ga4_client.is_ga4_configured():
        logger.warning("[AnalyticsNode] GA4 not configured")
        response = AnalyticsSnapshotResponse(
            sync_status="degraded",
            generated_at=_utc_now_iso(),
            period=_period_label(period_days),
            errors=["ga4_not_configured"],
        )
        return response

    errors: list[str] = []
    app_metrics: AnalyticsSourceAppMetrics | None = None
    zzpackage_metrics: AnalyticsSourceZzpackageMetrics | None = None

    app_property = ga4_client.get_property_id_app()
    if app_property:
        try:
            raw = ga4_client.fetch_app_metrics(app_property, period_days)
            app_metrics = AnalyticsSourceAppMetrics(
                active_users=raw["active_users"],
                sessions=raw["sessions"],
                avg_session_duration_sec=raw["avg_session_duration_sec"],
                game_starts=raw["game_starts"],
                lead_captured=raw["lead_captured"],
                dau_1d=raw.get("dau_1d"),
            )
            logger.info(
                "[AnalyticsNode] app snapshot sessions=%s game_starts=%s",
                app_metrics.sessions,
                app_metrics.game_starts,
            )
        except Ga4NotConfiguredError:
            errors.append("ga4_not_configured")
        except Exception as exc:
            logger.error("[AnalyticsNode] app fetch failed: %s", exc)
            errors.append(f"app_fetch_failed:{type(exc).__name__}")
    else:
        errors.append("ga4_property_id_app_missing")

    zz_property = ga4_client.get_property_id_zzpackage()
    if zz_property:
        try:
            raw = ga4_client.fetch_zzpackage_metrics(zz_property, period_days)
            zzpackage_metrics = AnalyticsSourceZzpackageMetrics(
                sessions=raw["sessions"],
                conversions=raw["conversions"],
                purchase_revenue=raw["purchase_revenue"],
                aov=raw["aov"],
            )
            logger.info(
                "[AnalyticsNode] zzpackage snapshot sessions=%s conversions=%s",
                zzpackage_metrics.sessions,
                zzpackage_metrics.conversions,
            )
        except Ga4NotConfiguredError:
            if "ga4_not_configured" not in errors:
                errors.append("ga4_not_configured")
        except Exception as exc:
            logger.error("[AnalyticsNode] zzpackage fetch failed: %s", exc)
            errors.append(f"zzpackage_fetch_failed:{type(exc).__name__}")
    else:
        errors.append("ga4_property_id_zzpackage_missing")

    has_data = app_metrics is not None or zzpackage_metrics is not None
    if not has_data:
        response = AnalyticsSnapshotResponse(
            sync_status="fail",
            generated_at=_utc_now_iso(),
            period=_period_label(period_days),
            errors=errors,
        )
        _cache[period_days] = response
        return response

    sync_status = "success" if not errors else "degraded"
    response = AnalyticsSnapshotResponse(
        sync_status=sync_status,
        generated_at=_utc_now_iso(),
        period=_period_label(period_days),
        sources=AnalyticsSnapshotSources(app=app_metrics, zzpackage=zzpackage_metrics),
        errors=errors,
    )
    _cache[period_days] = response
    _persist_snapshot(response)
    return response


def _persist_snapshot(response: AnalyticsSnapshotResponse) -> None:
    """Write snapshot to SQLite for COI sense layer history."""
    from agent.db import db_save_analytics_snapshot

    sources = {}
    if response.sources.app is not None:
        sources["app"] = response.sources.app.model_dump()
    if response.sources.zzpackage is not None:
        sources["zzpackage"] = response.sources.zzpackage.model_dump()

    row_id = db_save_analytics_snapshot(
        {
            "period": response.period,
            "generated_at": response.generated_at,
            "sync_status": response.sync_status,
            "sources": sources,
            "errors": response.errors,
        }
    )
    if row_id:
        logger.info("[AnalyticsNode] Snapshot persisted id=%s period=%s", row_id, response.period)
