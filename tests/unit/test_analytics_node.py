"""Tests for analytics_node (INT-009)."""

from unittest.mock import patch

import pytest

from agent.nodes import analytics_node
from agent.nodes.analytics_node import fetch_analytics_snapshot


@pytest.fixture(autouse=True)
def clear_cache():
    analytics_node._cache.clear()
    yield
    analytics_node._cache.clear()


def test_snapshot_degraded_when_ga4_not_configured():
    with patch("core.ga4_client.is_ga4_configured", return_value=False):
        result = fetch_analytics_snapshot(period_days=7)

    assert result.sync_status == "degraded"
    assert result.period == "last_7_days"
    assert result.errors == ["ga4_not_configured"]
    assert result.sources.app is None
    assert result.sources.zzpackage is None


def test_snapshot_success_both_sources(monkeypatch):
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/fake/creds.json")
    monkeypatch.setenv("GA4_PROPERTY_ID_APP", "111")
    monkeypatch.setenv("GA4_PROPERTY_ID_ZZPACKAGE", "222")

    with patch("core.ga4_client.is_ga4_configured", return_value=True), patch(
        "core.ga4_client.fetch_app_metrics",
        return_value={
            "active_users": 42,
            "sessions": 120,
            "avg_session_duration_sec": 95.3,
            "game_starts": 80,
            "lead_captured": 12,
            "dau_1d": 10,
        },
    ), patch(
        "core.ga4_client.fetch_zzpackage_metrics",
        return_value={
            "sessions": 200,
            "conversions": 5,
            "purchase_revenue": 995.0,
            "aov": 199.0,
        },
    ):
        result = fetch_analytics_snapshot(period_days=7)

    assert result.sync_status == "success"
    assert result.sources.app is not None
    assert result.sources.app.active_users == 42
    assert result.sources.app.game_starts == 80
    assert result.sources.app.dau_1d == 10
    assert result.sources.zzpackage is not None
    assert result.sources.zzpackage.aov == 199.0
    assert result.errors == []


def test_snapshot_degraded_partial_failure(monkeypatch):
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/fake/creds.json")
    monkeypatch.setenv("GA4_PROPERTY_ID_APP", "111")
    monkeypatch.setenv("GA4_PROPERTY_ID_ZZPACKAGE", "222")

    with patch("core.ga4_client.is_ga4_configured", return_value=True), patch(
        "core.ga4_client.fetch_app_metrics",
        return_value={
            "active_users": 1,
            "sessions": 2,
            "avg_session_duration_sec": 3.0,
            "game_starts": 1,
            "lead_captured": 0,
            "dau_1d": None,
        },
    ), patch(
        "core.ga4_client.fetch_zzpackage_metrics",
        side_effect=RuntimeError("quota"),
    ):
        result = fetch_analytics_snapshot(period_days=7)

    assert result.sync_status == "degraded"
    assert result.sources.app is not None
    assert result.sources.zzpackage is None
    assert any("zzpackage_fetch_failed" in err for err in result.errors)


def test_snapshot_fail_when_all_sources_fail(monkeypatch):
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/fake/creds.json")
    monkeypatch.setenv("GA4_PROPERTY_ID_APP", "111")
    monkeypatch.setenv("GA4_PROPERTY_ID_ZZPACKAGE", "222")

    with patch("core.ga4_client.is_ga4_configured", return_value=True), patch(
        "core.ga4_client.fetch_app_metrics",
        side_effect=RuntimeError("api down"),
    ), patch(
        "core.ga4_client.fetch_zzpackage_metrics",
        side_effect=RuntimeError("api down"),
    ):
        result = fetch_analytics_snapshot(period_days=1)

    assert result.sync_status == "fail"
    assert result.period == "last_1_day"
    assert len(result.errors) == 2


def test_snapshot_uses_cache(monkeypatch):
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/fake/creds.json")
    monkeypatch.setenv("GA4_PROPERTY_ID_APP", "111")

    fetch_mock = patch(
        "core.ga4_client.fetch_app_metrics",
        return_value={
            "active_users": 1,
            "sessions": 1,
            "avg_session_duration_sec": 1.0,
            "game_starts": 1,
            "lead_captured": 0,
            "dau_1d": None,
        },
    )
    with patch("core.ga4_client.is_ga4_configured", return_value=True), fetch_mock as mock_fetch, patch(
        "core.ga4_client.get_property_id_zzpackage",
        return_value="",
    ):
        first = fetch_analytics_snapshot(period_days=30)
        second = fetch_analytics_snapshot(period_days=30)

    assert first.sync_status == "degraded"
    assert second.generated_at == first.generated_at
    assert mock_fetch.call_count == 1
