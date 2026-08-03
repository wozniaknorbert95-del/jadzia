"""Marketing mode env switch — default PARKED, GO via DEMAND_OS_MARKETING_HITL."""

from __future__ import annotations

import os

import pytest

from agent.demand_os.commander_status import build_demand_os_status
from agent.demand_os.marketing_mode import (
    LIVE,
    PARKED,
    marketing_hitl_gate,
    resolve_marketing_mode,
)


def test_marketing_mode_default_parked(monkeypatch):
    monkeypatch.delenv("DEMAND_OS_MARKETING_HITL", raising=False)
    assert resolve_marketing_mode() == PARKED
    assert marketing_hitl_gate() == "BLOCKED"


def test_marketing_mode_go_env(monkeypatch):
    monkeypatch.setenv("DEMAND_OS_MARKETING_HITL", "GO")
    assert resolve_marketing_mode() == LIVE
    assert marketing_hitl_gate() == "READY"


def test_status_reflects_go_env(monkeypatch):
    monkeypatch.setenv("DEMAND_OS_MARKETING_HITL", "GO")
    st = build_demand_os_status()
    assert st["marketing"] == LIVE
    assert st["diagnostics"]["marketing_hitl_gate"] == "READY"
    assert st["cash_warning"] is None
    assert st["robota_dnia"]["code"] != "PARKED_STOP"
