"""GA4 adapter honesty — stub ≠ zero success; sessions ≠ starts."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

from agent.demand_os.ga4_adapter import fetch_wizard_starts, fetch_wizard_starts_by_utm


def test_stub_is_unavailable_not_ok_zero(monkeypatch):
    monkeypatch.delenv("DEMAND_OS_GA4_LIVE", raising=False)
    out = fetch_wizard_starts(days=7)
    assert out["ok"] is False
    assert out["status"] == "unavailable"
    assert out["mode"] == "stub"
    assert out["ga4_sessions_7d"] is None
    assert out["ga4_wizard_starts_7d"] is None
    assert "disabled" in out["reason"].lower() or "disabled" in out["error"].lower()


def test_live_without_creds_unavailable(monkeypatch):
    monkeypatch.setenv("DEMAND_OS_GA4_LIVE", "1")
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    monkeypatch.delenv("GA4_CREDENTIALS_JSON", raising=False)
    monkeypatch.delenv("GA4_PROPERTY_ID_ZZPACKAGE", raising=False)
    monkeypatch.delenv("GA4_PROPERTY_ID_APP", raising=False)
    monkeypatch.delenv("GA4_PROPERTY_ID", raising=False)
    out = fetch_wizard_starts(days=7)
    assert out["ok"] is False
    assert out["status"] == "unavailable"
    assert out["mode"] == "missing_config"


def test_live_aggregate_ok_splits_sessions(monkeypatch):
    monkeypatch.setenv("DEMAND_OS_GA4_LIVE", "1")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/tmp/fake.json")
    monkeypatch.setenv("GA4_PROPERTY_ID_ZZPACKAGE", "123456")

    snap = MagicMock()
    snap.sources.model_dump.return_value = {"zzpackage": {"sessions": 42}}
    snap.sync_status = "fresh"
    snap.fetched_at = "2026-08-03T12:00:00Z"
    snap.created_at = None

    with patch(
        "agent.nodes.analytics_node.fetch_analytics_snapshot",
        return_value=snap,
    ):
        out = fetch_wizard_starts(days=7)

    assert out["ok"] is True
    assert out["status"] == "ok"
    assert out["ga4_sessions_7d"] == 42
    assert out["ga4_wizard_starts_7d"] is None  # not invented
    assert out["starts"] == []


def test_live_error_unavailable(monkeypatch):
    monkeypatch.setenv("DEMAND_OS_GA4_LIVE", "1")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/tmp/fake.json")
    monkeypatch.setenv("GA4_PROPERTY_ID_ZZPACKAGE", "123456")

    with patch(
        "agent.nodes.analytics_node.fetch_analytics_snapshot",
        side_effect=RuntimeError("boom"),
    ):
        out = fetch_wizard_starts(days=7)

    assert out["ok"] is False
    assert out["status"] == "unavailable"
    assert out["mode"] == "live_error"
    assert "boom" in out["reason"]


def test_utm_csv_missing_unavailable(monkeypatch, tmp_path):
    monkeypatch.delenv("DEMAND_OS_GA4_UTM_CSV", raising=False)
    out = fetch_wizard_starts_by_utm(days=7)
    assert out["ok"] is False
    assert out["status"] == "unavailable"
    assert out["starts_by_utm"] == {}


def test_utm_csv_import(monkeypatch, tmp_path):
    csv_path = tmp_path / "utm.csv"
    csv_path.write_text("utm_link,starts\nhttps://x?utm_content=a,3\n", encoding="utf-8")
    monkeypatch.setenv("DEMAND_OS_GA4_UTM_CSV", str(csv_path))
    out = fetch_wizard_starts_by_utm(days=7)
    assert out["ok"] is True
    assert out["status"] == "ok"
    assert out["starts_by_utm"]["https://x?utm_content=a"] == 3
