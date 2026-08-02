"""Demand Desk UI — static contract guards (no browser)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "commander-ui" / "index.html").read_text(encoding="utf-8")
APP = (ROOT / "commander-ui" / "app.js").read_text(encoding="utf-8")
CSS = (ROOT / "commander-ui" / "styles.css").read_text(encoding="utf-8")
SW = (ROOT / "commander-ui" / "sw.js").read_text(encoding="utf-8")
GOLDEN = json.loads(
    (ROOT / "tests" / "fixtures" / "desk_status_v21.min.json").read_text(encoding="utf-8")
)

DESK_IDS = [
    "view-demand-desk",
    "desk-header",
    "desk-robota",
    "desk-icp",
    "desk-state",
    "desk-week",
    "desk-cash-warning",
    "desk-praca",
    "desk-puls",
    "desk-kpi-starts",
    "desk-kpi-wow",
    "desk-kpi-paid",
    "desk-kpi-hook",
    "desk-kpi-publish",
    "desk-fixture-banner",
    "desk-praca-hitl",
    "desk-hitl-list",
    "desk-praca-hunt",
    "desk-hunt-list",
    "desk-jakosc",
    "desk-val-fail",
    "desk-comments",
    "desk-gorace",
    "desk-stl",
    "desk-dual-cash",
    "desk-skad",
    "desk-top-assets",
    "desk-kalendarz",
    "desk-week-calendar",
    "desk-shells-line",
    "desk-footer",
    "desk-data-mode",
    "desk-last-real",
    "desk-doctor",
    "desk-gate",
    "desk-contract-version",
]

CONTRACT_KEYS = [
    "robota_dnia",
    "icp_role_week",
    "iso_week",
    "state",
    "cash_warning",
    "kpi",
    "screen",
    "stl",
    "dual_cash",
    "week_calendar",
    "shells_line",
    "data_mode",
    "last_real_event",
    "footer",
    "diagnostics",
    "contract_version",
    "gate",
]


def _desk_js_section() -> str:
    marker = "// --- Demand Desk (Etap 5) ---"
    assert marker in APP
    return APP[APP.index(marker) :]


def test_desk_html_ids_present():
    for el_id in DESK_IDS:
        assert f'id="{el_id}"' in HTML, el_id


def test_desk_load_and_render_functions():
    section = _desk_js_section()
    assert "function loadDemandDesk" in section
    assert "function renderDemandDesk" in section


def test_no_go_ready_hero_or_publish_in_desk_section():
    section = _desk_js_section()
    assert "desk-go-ready" not in section
    assert "Opublikować" not in section


def test_bottom_nav_still_five_views():
    start = HTML.index('id="bottom-nav"')
    end = HTML.index("</nav>", start)
    bottom = HTML[start:end]
    assert bottom.count('data-view="') == 5
    assert 'data-view="demand-desk"' not in bottom


def test_desk_nav_desktop_and_more_sheet():
    assert 'data-view="demand-desk"' in HTML
    assert "Biuro Popytu" in HTML
    assert 'id="more-to-demand-desk"' in HTML


def test_cache_bust_desk_dash02():
    assert HTML.count("desk-dash02") >= 2
    assert "desk-dash01" not in HTML
    assert "coi-commander-desk-dash02" in SW


def test_desk_design_link_in_html():
    assert "DEMAND-CONTROL-PANEL-DESIGN.md" in HTML
    assert "Design v2.1" in HTML


def test_desk_praca_before_puls_in_html():
    assert HTML.index('id="desk-praca"') < HTML.index('id="desk-puls"')


def test_render_top_assets_asset_or_asset_id():
    section = _desk_js_section()
    assert "a.asset || a.asset_id" in section


def test_refresh_only_loads_desk_when_active():
    start = APP.index("async function refresh()")
    end = APP.index("\nasync function ", start + 1)
    refresh_body = APP[start:end]
    assert 'active === "demand-desk"' in refresh_body
    assert "loadDemandDesk" in refresh_body
    assert refresh_body.index('active === "demand-desk"') < refresh_body.index("loadDemandDesk")


def test_dual_cash_columns_in_render():
    section = _desk_js_section()
    assert "dual.columns" in section
    assert "verdict, offerte_only" in section


def test_desk_css_states():
    assert ".demand-desk--fixture" in CSS
    assert ".demand-desk--parked-stop" in CSS
    assert "min-height: 44px" in CSS


def test_render_references_contract_keys():
    section = _desk_js_section()
    for key in CONTRACT_KEYS:
        assert key in section or key.replace("_", "") in section.replace("_", ""), key


def test_golden_fixture_keys():
    for key in CONTRACT_KEYS:
        assert key in GOLDEN or key == "contract_version"


def test_deep_link_view_param():
    assert 'get("view")' in APP
    assert "demand-desk" in APP


def test_more_sheet_demand_desk_wired():
    assert "bindNavButtons(\".more-sheet-btn[data-view]\")" in APP
    assert 'id="more-to-demand-desk"' in HTML


def test_desk_rbac_disables_all_act_buttons():
    section = _desk_js_section()
    assert 'querySelectorAll(".desk-act-btn")' in section
