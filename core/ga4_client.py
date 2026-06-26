"""GA4 Data API client — INT-009 read-only metrics."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_APP_EVENTS = ("game_start", "lead_captured", "score_submitted")


class Ga4NotConfiguredError(Exception):
    """Raised when GA4 credentials or property IDs are missing."""


def get_property_id_app() -> str:
    return os.getenv("GA4_PROPERTY_ID_APP", "").strip()


def get_property_id_zzpackage() -> str:
    return os.getenv("GA4_PROPERTY_ID_ZZPACKAGE", "").strip()


def is_ga4_configured() -> bool:
    """True when credentials path and at least one property ID are set."""
    creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if not creds:
        return False
    return bool(get_property_id_app() or get_property_id_zzpackage())


def _get_client() -> Any:
    if not is_ga4_configured():
        raise Ga4NotConfiguredError("GA4 not configured")
    from google.analytics.data_v1beta import BetaAnalyticsDataClient

    return BetaAnalyticsDataClient()


def _date_range(days: int) -> tuple[str, str]:
    if days <= 1:
        return "yesterday", "today"
    return f"{days}daysAgo", "today"


def _metric_value(rows: List[Any], index: int = 0) -> float:
    if not rows:
        return 0.0
    values = rows[0].metric_values
    if index >= len(values):
        return 0.0
    raw = values[index].value
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 0.0


def _run_standard_report(
    property_id: str,
    metrics: List[str],
    days: int,
) -> Dict[str, float]:
    from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest

    client = _get_client()
    request = RunReportRequest(
        property=f"properties/{property_id}",
        metrics=[Metric(name=name) for name in metrics],
        date_ranges=[DateRange(start_date=_date_range(days)[0], end_date=_date_range(days)[1])],
    )
    response = client.run_report(request)
    rows = list(response.rows)
    return {name: _metric_value(rows, idx) for idx, name in enumerate(metrics)}


def _run_event_counts(
    property_id: str,
    event_names: tuple[str, ...],
    days: int,
) -> Dict[str, int]:
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Filter,
        FilterExpression,
        Metric,
        RunReportRequest,
    )

    if not event_names:
        return {}

    client = _get_client()
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount")],
        date_ranges=[DateRange(start_date=_date_range(days)[0], end_date=_date_range(days)[1])],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                in_list_filter=Filter.InListFilter(values=list(event_names)),
            )
        ),
    )
    response = client.run_report(request)
    counts: Dict[str, int] = {name: 0 for name in event_names}
    for row in response.rows:
        event_name = row.dimension_values[0].value
        if event_name in counts:
            try:
                counts[event_name] = int(float(row.metric_values[0].value))
            except (TypeError, ValueError):
                counts[event_name] = 0
    return counts


def fetch_app_metrics(property_id: str, date_range_days: int) -> Dict[str, Any]:
    """Fetch app property metrics for the given lookback window."""
    standard = _run_standard_report(
        property_id,
        ["activeUsers", "sessions", "averageSessionDuration"],
        date_range_days,
    )
    events = _run_event_counts(property_id, _APP_EVENTS, date_range_days)

    dau_1d: Optional[int] = None
    if date_range_days > 1:
        try:
            dau_row = _run_standard_report(property_id, ["activeUsers"], 1)
            dau_1d = int(dau_row.get("activeUsers", 0))
        except Exception as exc:
            logger.warning("[GA4] app dau_1d fetch failed: %s", exc)

    return {
        "active_users": int(standard.get("activeUsers", 0)),
        "sessions": int(standard.get("sessions", 0)),
        "avg_session_duration_sec": round(standard.get("averageSessionDuration", 0.0), 2),
        "game_starts": events.get("game_start", 0),
        "lead_captured": events.get("lead_captured", 0),
        "score_submitted": events.get("score_submitted", 0),
        "dau_1d": dau_1d,
    }


def fetch_zzpackage_metrics(property_id: str, date_range_days: int) -> Dict[str, Any]:
    """Fetch zzpackage Wizard property metrics for the given lookback window."""
    standard = _run_standard_report(
        property_id,
        ["sessions", "conversions", "purchaseRevenue", "transactions"],
        date_range_days,
    )
    sessions = int(standard.get("sessions", 0))
    conversions = int(standard.get("conversions", 0))
    purchase_revenue = round(standard.get("purchaseRevenue", 0.0), 2)
    transactions = int(standard.get("transactions", 0))
    aov = round(purchase_revenue / transactions, 2) if transactions > 0 else 0.0

    return {
        "sessions": sessions,
        "conversions": conversions,
        "purchase_revenue": purchase_revenue,
        "aov": aov,
    }
