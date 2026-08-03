"""Connector boundary — fail-closed honesty for tool 100%."""

from __future__ import annotations

import pytest

from agent.demand_os.ga4_adapter import fetch_wizard_starts
from agent.demand_os.gdrive_cf import list_cf_assets
from agent.demand_os.commander_status import build_demand_os_status


def test_ga4_default_stub_no_invented_rows(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("DEMAND_OS_GA4_LIVE", raising=False)
    out = fetch_wizard_starts(days=7)
    assert out["ok"] is False
    assert out["mode"] == "stub"
    assert out["starts"] == []


def test_gdrive_default_local_registry(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("DEMAND_OS_GDRIVE_LIVE", raising=False)
    out = list_cf_assets(limit=2)
    assert out["ok"] is True
    assert out["mode"] == "local_registry"
    assert isinstance(out.get("assets"), list)


def test_footer_lightweight_never_claims_doctor_pass():
    st = build_demand_os_status(with_full_doctor=False)
    assert st["footer"]["doctor_scope"] == "lightweight"
    assert st["footer"]["doctor_ok"] is False
    assert "doctor_files_ok" in st["footer"]


def test_footer_full_scope_matches_boolean():
    st = build_demand_os_status(with_full_doctor=True)
    assert st["footer"]["doctor_scope"] == "full"
    assert isinstance(st["footer"]["doctor_ok"], bool)
