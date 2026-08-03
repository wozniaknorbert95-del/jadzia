"""Desk status GA4 honesty — split metrics, unavailable stub."""

from __future__ import annotations

from agent.demand_os.commander_status import build_demand_os_status


def test_status_ga4_stub_unavailable_split(monkeypatch):
    monkeypatch.delenv("DEMAND_OS_GA4_LIVE", raising=False)
    payload = build_demand_os_status(with_full_doctor=False)
    assert "ga4" in payload
    ga4 = payload["ga4"]
    assert ga4["ok"] is False
    assert ga4["status"] == "unavailable"
    assert ga4["mode"] == "stub"
    assert ga4["ga4_sessions_7d"] is None
    assert ga4["ga4_wizard_starts_7d"] is None
    assert "utm_attributed_starts" in ga4
    kpi = payload["kpi"]
    assert "utm_attributed_starts" in kpi
    assert "ga4_sessions_7d" in kpi
    # North Star remains ledger/events, not GA4 invent
    assert kpi["wizard_starts_utm"] == kpi["utm_attributed_starts"]
