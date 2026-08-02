"""Demand Desk E2E-style flows via API + static contracts (no Playwright in CI)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "commander-ui" / "index.html").read_text(encoding="utf-8")
APP = (ROOT / "commander-ui" / "app.js").read_text(encoding="utf-8")


def test_default_boot_opens_demand_desk_without_view_param():
    boot = APP[APP.index("async function vhqBoot"): APP.index("if (document.readyState", APP.index("async function vhqBoot"))]
    assert "await openDemandDeskView()" in boot
    assert 'viewParam === "hq"' in boot


def test_deep_link_demand_desk_in_boot():
    assert 'viewParam === "demand-desk"' in APP or 'viewParam === "demand-desk"' in APP
    assert "openDemandDeskView" in APP


def test_more_sheet_demand_desk_entry():
    assert 'id="more-to-demand-desk"' in HTML
    assert 'data-view="demand-desk"' in HTML


def test_refresh_scope_preserves_desk_loader():
    start = APP.index("async function refresh()")
    end = APP.index("\nasync function ", start + 1)
    body = APP[start:end]
    assert 'active === "demand-desk"' in body
    assert "loadDemandDesk" in body
