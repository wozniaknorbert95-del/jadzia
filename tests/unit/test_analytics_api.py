"""Tests for GET /api/v1/analytics/snapshot (INT-009)."""

import os
from unittest.mock import patch

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from core.models import (
    AnalyticsSnapshotResponse,
    AnalyticsSnapshotSources,
    AnalyticsSourceAppMetrics,
)

JWT_SECRET_VALUE = "test-secret-analytics"


@pytest.fixture
def client():
    return TestClient(create_app())


def _auth_headers() -> dict[str, str]:
    token = pyjwt.encode({"sub": "test"}, JWT_SECRET_VALUE, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


def test_analytics_snapshot_degraded_without_ga4(client):
    with patch.dict(os.environ, {"JWT_SECRET": JWT_SECRET_VALUE}, clear=False), patch(
        "api.dependencies.JWT_SECRET",
        JWT_SECRET_VALUE,
    ), patch(
        "agent.nodes.analytics_node.fetch_analytics_snapshot",
        return_value=AnalyticsSnapshotResponse(
            sync_status="degraded",
            generated_at="2026-06-26T12:00:00+00:00",
            period="last_7_days",
            errors=["ga4_not_configured"],
        ),
    ):
        r = client.get("/api/v1/analytics/snapshot", headers=_auth_headers())

    assert r.status_code == 200
    assert r.json()["sync_status"] == "degraded"


def test_analytics_snapshot_requires_jwt_when_secret_set(client):
    with patch.dict(os.environ, {"JWT_SECRET": JWT_SECRET_VALUE}, clear=False), patch(
        "api.dependencies.JWT_SECRET",
        JWT_SECRET_VALUE,
    ):
        r = client.get("/api/v1/analytics/snapshot")

    assert r.status_code == 401


def test_analytics_snapshot_success(client):
    payload = AnalyticsSnapshotResponse(
        sync_status="success",
        generated_at="2026-06-26T12:00:00+00:00",
        period="last_7_days",
        sources=AnalyticsSnapshotSources(
            app=AnalyticsSourceAppMetrics(
                active_users=10,
                sessions=20,
                avg_session_duration_sec=30.0,
                game_starts=5,
                lead_captured=2,
            )
        ),
    )
    with patch.dict(os.environ, {"JWT_SECRET": JWT_SECRET_VALUE}, clear=False), patch(
        "api.dependencies.JWT_SECRET",
        JWT_SECRET_VALUE,
    ), patch(
        "agent.nodes.analytics_node.fetch_analytics_snapshot",
        return_value=payload,
    ):
        r = client.get("/api/v1/analytics/snapshot?period=7d", headers=_auth_headers())

    assert r.status_code == 200
    data = r.json()
    assert data["sync_status"] == "success"
    assert data["sources"]["app"]["active_users"] == 10


def test_analytics_snapshot_fail_returns_503(client):
    with patch.dict(os.environ, {"JWT_SECRET": JWT_SECRET_VALUE}, clear=False), patch(
        "api.dependencies.JWT_SECRET",
        JWT_SECRET_VALUE,
    ), patch(
        "agent.nodes.analytics_node.fetch_analytics_snapshot",
        return_value=AnalyticsSnapshotResponse(
            sync_status="fail",
            generated_at="2026-06-26T12:00:00+00:00",
            period="last_7_days",
            errors=["app_fetch_failed:RuntimeError"],
        ),
    ):
        r = client.get("/api/v1/analytics/snapshot", headers=_auth_headers())

    assert r.status_code == 503
