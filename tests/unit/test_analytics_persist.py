"""Tests for analytics snapshot persistence (S3-01)."""

import json
import os
from unittest.mock import patch

import pytest

from agent.db import db_get_latest_analytics_snapshot, db_list_analytics_snapshots, db_save_analytics_snapshot
from agent.nodes.analytics_node import fetch_analytics_snapshot
from core.models import AnalyticsSnapshotResponse, AnalyticsSnapshotSources, AnalyticsSourceZzpackageMetrics


@pytest.fixture
def temp_db(monkeypatch):
    import tempfile

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr("agent.db.DB_PATH", path)
    import agent.db as db_mod

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


def test_db_save_and_list_snapshot(temp_db):
    row_id = db_save_analytics_snapshot(
        {
            "period": "last_7_days",
            "generated_at": "2026-07-03T10:00:00+00:00",
            "sync_status": "success",
            "sources": {"zzpackage": {"sessions": 23, "conversions": 2}},
            "errors": [],
        }
    )
    assert row_id is not None

    latest = db_get_latest_analytics_snapshot()
    assert latest is not None
    assert latest["sync_status"] == "success"
    sources = json.loads(latest["sources_json"])
    assert sources["zzpackage"]["sessions"] == 23

    listed = db_list_analytics_snapshots(limit=5)
    assert len(listed) == 1


def test_fetch_analytics_snapshot_persists_on_success(temp_db):
    fake_response = AnalyticsSnapshotResponse(
        sync_status="success",
        generated_at="2026-07-03T10:00:00+00:00",
        period="last_7_days",
        sources=AnalyticsSnapshotSources(
            zzpackage=AnalyticsSourceZzpackageMetrics(sessions=10, conversions=1)
        ),
        errors=[],
    )

    with patch("agent.nodes.analytics_node.ga4_client.is_ga4_configured", return_value=True), patch(
        "agent.nodes.analytics_node.ga4_client.get_property_id_app",
        return_value=None,
    ), patch(
        "agent.nodes.analytics_node.ga4_client.get_property_id_zzpackage",
        return_value="123",
    ), patch(
        "agent.nodes.analytics_node.ga4_client.fetch_zzpackage_metrics",
        return_value={
            "sessions": 10,
            "conversions": 1,
            "purchase_revenue": 100.0,
            "aov": 100.0,
        },
    ), patch(
        "agent.nodes.analytics_node._cache",
        {},
    ):
        result = fetch_analytics_snapshot(period_days=7)

    assert result.sync_status in ("success", "degraded")
    rows = db_list_analytics_snapshots()
    assert len(rows) == 1
