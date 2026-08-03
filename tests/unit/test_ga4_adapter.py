"""GA4 adapter honesty — stub ≠ zero success; sessions ≠ starts."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

from agent.demand_os.ga4_adapter import (
    fetch_wizard_starts,
    fetch_wizard_starts_by_utm,
    fetch_wizard_starts_stub,
    ga4_available,
    pull_ga4_into_dtl,
)


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


def test_live_aggregate_ok_splits_sessions(monkeypatch, tmp_path):
    creds = tmp_path / "ga4.json"
    creds.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("DEMAND_OS_GA4_LIVE", "1")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(creds))
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


def test_live_path_without_file_unavailable(monkeypatch):
    monkeypatch.setenv("DEMAND_OS_GA4_LIVE", "1")
    monkeypatch.setenv(
        "GOOGLE_APPLICATION_CREDENTIALS", "/opt/jadzia/secrets/missing-ga4.json"
    )
    monkeypatch.setenv("GA4_PROPERTY_ID_ZZPACKAGE", "123456")
    monkeypatch.delenv("GA4_CREDENTIALS_JSON", raising=False)
    out = fetch_wizard_starts(days=7)
    assert out["ok"] is False
    assert out["status"] == "unavailable"
    assert out["mode"] == "missing_config"


def test_live_sync_fail_null_sessions_unavailable(monkeypatch, tmp_path):
    creds = tmp_path / "ga4.json"
    creds.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("DEMAND_OS_GA4_LIVE", "1")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(creds))
    monkeypatch.setenv("GA4_PROPERTY_ID_ZZPACKAGE", "123456")
    snap = MagicMock()
    snap.sources.model_dump.return_value = {"zzpackage": {}}
    snap.sync_status = "fail"
    snap.fetched_at = None
    snap.created_at = None
    with patch(
        "agent.nodes.analytics_node.fetch_analytics_snapshot",
        return_value=snap,
    ):
        out = fetch_wizard_starts(days=7)
    assert out["ok"] is False
    assert out["status"] == "unavailable"
    assert out["mode"] == "live_error"


def test_live_error_unavailable(monkeypatch, tmp_path):
    creds = tmp_path / "ga4.json"
    creds.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("DEMAND_OS_GA4_LIVE", "1")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(creds))
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


def test_ga4_available_and_stub_alias(monkeypatch):
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    monkeypatch.delenv("GA4_CREDENTIALS_JSON", raising=False)
    assert ga4_available() is False
    monkeypatch.setenv("GA4_CREDENTIALS_JSON", '{"type":"service_account"}')
    monkeypatch.setenv("GA4_PROPERTY_ID", "999")
    assert ga4_available() is True
    monkeypatch.delenv("DEMAND_OS_GA4_LIVE", raising=False)
    stub = fetch_wizard_starts_stub(days=7)
    assert stub["mode"] == "stub"


def test_ga4_inline_credentials_must_be_json(monkeypatch):
    # Inline contract: GA4_CREDENTIALS_JSON only counts when it is inline JSON
    # (starts with "{") — a path or garbage here must not flip live mode on.
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    monkeypatch.setenv("GA4_CREDENTIALS_JSON", "/opt/jadzia/secrets/ga4.json")
    monkeypatch.setenv("GA4_PROPERTY_ID", "999")
    assert ga4_available() is False
    monkeypatch.setenv("GA4_CREDENTIALS_JSON", "not-json")
    assert ga4_available() is False
    monkeypatch.setenv("GA4_CREDENTIALS_JSON", ' {"type":"service_account"}')
    assert ga4_available() is True


def test_live_wizard_event_and_freshness(monkeypatch, tmp_path):
    creds = tmp_path / "ga4.json"
    creds.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("DEMAND_OS_GA4_LIVE", "1")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(creds))
    monkeypatch.setenv("GA4_PROPERTY_ID_ZZPACKAGE", "123456")
    monkeypatch.setenv("DEMAND_OS_GA4_WIZARD_START_EVENT", "wizard_start")
    snap = MagicMock()
    snap.sources.model_dump.return_value = {
        "zzpackage": {"sessions": 10, "events": {"wizard_start": "5"}}
    }
    snap.sync_status = None
    snap.fetched_at = None
    snap.created_at = "2026-08-03T12:00:00Z"
    with patch(
        "agent.nodes.analytics_node.fetch_analytics_snapshot",
        return_value=snap,
    ):
        out = fetch_wizard_starts(days=7)
    assert out["ok"] is True
    assert out["ga4_wizard_starts_7d"] == 5
    assert out["freshness"]


def test_pull_ga4_into_dtl_paths(monkeypatch):
    monkeypatch.delenv("DEMAND_OS_GA4_LIVE", raising=False)
    skipped = pull_ga4_into_dtl()
    assert skipped["status"] == "unavailable"
    monkeypatch.setenv("DEMAND_OS_GA4_LIVE", "1")
    with patch(
        "agent.marketing.dtl.ga4.ingest_ga4_snapshot",
        return_value={"status": "ok"},
    ):
        ok = pull_ga4_into_dtl()
    assert ok["ok"] is True
    with patch(
        "agent.marketing.dtl.ga4.ingest_ga4_snapshot",
        side_effect=RuntimeError("nope"),
    ):
        err = pull_ga4_into_dtl()
    assert err["mode"] == "dtl_error"


def test_utm_csv_missing_file_and_bad_starts(monkeypatch, tmp_path):
    monkeypatch.setenv("DEMAND_OS_GA4_UTM_CSV", str(tmp_path / "missing.csv"))
    out = fetch_wizard_starts_by_utm(days=7)
    assert out["mode"] == "missing_file"
    csv_path = tmp_path / "utm.csv"
    csv_path.write_text(
        "utm_link,starts\nhttps://x?utm_content=a,bad\nhttps://y?utm_content=b,2\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("DEMAND_OS_GA4_UTM_CSV", str(csv_path))
    out2 = fetch_wizard_starts_by_utm(days=7)
    assert out2["ok"] is True
    assert out2["starts_by_utm"] == {"https://y?utm_content=b": 2}
