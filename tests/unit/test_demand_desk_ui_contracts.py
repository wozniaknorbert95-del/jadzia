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
    "desk-ab-row",
    "desk-praca",
    "desk-puls",
    "desk-kpi-starts",
    "desk-kpi-wow",
    "desk-kpi-paid",
    "desk-kpi-hook",
    "desk-kpi-publish",
    "desk-kpi-ga4",
    "desk-kpi-attr",
    "desk-fixture-banner",
    "desk-praca-hitl",
    "desk-hitl-list",
    "desk-praca-hunt",
    "desk-hunt-list",
    "desk-cd-row",
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
    "desk-stale-hint",
    "desk-empty-data-hint",
    "desk-human-line",
    "desk-cadence-chip",
    "desk-retry",
    "desk-money-check",
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
    "ga4",
    "attribution",
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

# Forbidden on Demand Desk primary surface (empty/error/CTA strings).
# Diagnostics JSON dump is allowed to keep technical keys.
DESK_PRIMARY_FORBIDDEN = (
    "CONTENT-CALENDAR",
    "ALLOWLIST.json",
    "ENGAGE-LOG",
    "set-now",
    "DEMAND_OS_",
    "fixture fake",
    "Dry komentarz",
    "BRAK POŁĄCZENIA",
    "Ledger dziś",
    "Money Check błąd",
    "Hunt dry OK",
    "Hunt dry błąd",
)


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


def test_bottom_nav_primary_desk_not_marketing():
    start = HTML.index('id="bottom-nav"')
    end = HTML.index("</nav>", start)
    bottom = HTML[start:end]
    assert bottom.count('data-view="') == 4
    assert 'data-view="demand-desk"' in bottom
    assert 'data-view="home"' in bottom
    assert 'data-view="hq"' not in bottom
    assert 'data-view="marketing"' not in bottom
    assert 'id="open-more-nav-bottom"' in bottom


def test_main_nav_no_marketing_desk_first():
    start = HTML.index('id="main-nav"')
    end = HTML.index("</nav>", start)
    nav = HTML[start:end]
    assert 'data-view="demand-desk"' in nav
    assert nav.index('data-view="demand-desk"') < nav.index('data-view="home"')
    assert 'data-view="marketing"' not in nav
    assert 'data-view="hq"' not in nav
    assert 'id="open-more-nav"' in nav


def test_vhq_only_in_more_sheet():
    assert 'data-vhq-entry="1"' in HTML
    assert 'id="more-to-vhq"' in HTML
    assert "Mission Control (VHQ)" in HTML


def test_desk_nav_desktop_and_more_sheet():
    assert 'data-view="demand-desk"' in HTML
    assert "Biuro Popytu" in HTML
    assert 'id="more-to-demand-desk"' in HTML


def test_cache_bust_desk_dash10():
    assert HTML.count("desk-dash10") >= 2
    assert "desk-dash09" not in HTML
    assert "coi-commander-desk-dash10" in SW


def test_ux_repair_honesty_guards():
    assert "#desk-connection-banner[hidden]" in CSS
    assert "display: none !important" in CSS.split("#desk-connection-banner[hidden]")[1][:120]
    assert "desk-cadence-chip" in HTML
    assert "desk-human-line" in HTML
    assert "demand-desk-icp-details" in HTML
    section = _desk_js_section()
    assert "live_cadence" in section
    assert "bez publikacji" in section
    assert "if (!confirmed?.ok) return" in section
    assert '!can || ds === "SENT"' in section


def test_desk_primary_surface_no_internal_jargon():
    """K4: empty/error/CTA strings must be plain language."""
    section = _desk_js_section()
    # Exclude diagnostics JSON dump which may stringify technical keys.
    primary = section
    if "desk-diagnostics-body" in primary:
        # Keep full section but assert forbidden tokens are not in user-facing string literals.
        pass
    for token in DESK_PRIMARY_FORBIDDEN:
        assert token not in section, f"forbidden jargon on desk surface: {token}"
    assert "DESK_COPY" in section
    assert "niedostępne" in section
    assert "Dziennik" in HTML
    assert "Sesje GA4" in HTML
    assert "Brak połączenia" in HTML


def test_desk_ga4_tile_honest_unavailable():
    section = _desk_js_section()
    assert "ga4_sessions_7d" in section
    assert 'ga4.status === "ok"' in section
    assert "DESK_COPY.ga4Unavailable" in section
    assert "to nie starty Wizard" in section


def test_k6_show_view_sets_inert_on_hidden():
    assert 'v.setAttribute("inert"' in APP or 'setAttribute("inert"' in APP
    assert 'aria-hidden", "true"' in APP


def test_k7_mobile_css_safe_area_and_touch():
    assert "safe-area-inset-bottom" in CSS
    assert "min-height: 44px" in CSS


def test_k10_typed_errors_helper():
    assert "function deskTypedError" in APP
    assert "correlationId" in APP


def test_k11_offline_banner_and_sw_stale_while_revalidate():
    assert "deskUpdateOfflineBanner" in APP
    assert "desk-offline-banner" in APP
    assert "deskPersistCache" in APP
    assert "desk_cache_v1" in APP
    assert "Stale-while-revalidate" in SW or "stale-while-revalidate" in SW.lower()
    assert "/api/" in SW


def test_k3_cookie_session_probe_and_no_jwt_url():
    assert "probeSession" in APP
    assert "hasSession" in APP
    assert "auth/session" in APP
    assert "Link z tokenem jest wyłączony" in APP
    assert "Zaawansowane (awaryjny token)" in HTML


def test_k10_api_errors_not_raw_json():
    assert "function apiErrorMessage" in APP
    assert "JSON.stringify(detail)" not in APP.split("// --- Demand Desk")[0]


def test_vhq_lazy_manifest_deferred():
    bind_start = APP.index("function bindVhqShell()")
    bind_end = APP.index("bindVhqShell();", bind_start)
    bind_body = APP[bind_start:bind_end]
    assert "vhqRenderAllManifestSurfaces()" not in bind_body
    assert "function vhqEnsureManifest()" in APP
    assert "vhqEnsureManifest();" in APP


def test_vhq_inert_when_hidden():
    assert 'id="view-hq"' in HTML
    hq = HTML[HTML.index('id="view-hq"'): HTML.index('id="view-home"')]
    assert "inert" in hq
    assert 'aria-hidden="true"' in hq


def test_open_queue_clears_vhq_url():
    assert "function clearVhqUrlParam()" in APP
    assert "async function openQueueView()" in APP
    assert "clearVhqUrlParam();" in APP.split("async function openDemandDeskView()")[1][:400]


def test_render_queue_hides_ceo_stubs():
    start = APP.index("function renderQueue(items)")
    body = APP[start:start + 800]
    assert "isCeoStubItem" in body
    assert "queue-hygiene-label" not in body
    assert "badge-stub" not in body


def test_desk_fixture_banner_in_header():
    header = HTML[HTML.index('id="desk-header"'): HTML.index('id="desk-ab-row"')]
    assert 'id="desk-fixture-banner"' in header
    assert "demand-desk-banner--prominent" in header


def test_hunt_sent_optimistic_ui():
    assert "desk-badge--sent" in APP
    assert "CSS.escape(targetId)" in APP.split("async function deskHuntDry")[1][:600]


def test_bootstrap_auth_defers_refresh_to_vhq_boot():
    start = APP.index("async function bootstrapAuth()")
    end = APP.index("\n// --- Demand Desk", start)
    body = APP[start:end]
    assert "refresh()" not in body or body.count("refresh()") == 0


def test_vhq_enrich_demand_os_non_critical_auth():
    assert 'api("/api/v1/commander/demand-os/status", { authCritical: false })' in APP


def test_desk_design_link_in_html():
    assert "DEMAND-CONTROL-PANEL-DESIGN.md" in HTML
    assert "Design v2.1" in HTML


def test_desk_ab_row_layout():
    ab_start = HTML.index('id="desk-ab-row"')
    praca = HTML.index('id="desk-praca"', ab_start)
    puls = HTML.index('id="desk-puls"', ab_start)
    assert praca < puls
    assert ".demand-desk-ab-row" in CSS
    assert ".demand-desk-cd-row" in CSS


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
    assert "dual.open_fail" in section
    assert "dual.red" in section


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
    assert "#desk-icp-form input" in section


def test_desk_retry_and_money_check_wired():
    section = _desk_js_section()
    assert "desk-retry" in section
    assert "deskMoneyCheck" in section
    assert "deskFormatWow" in section
    assert "aria-busy" in section


def test_marketing_legacy_banner():
    assert "Legacy organic" in HTML
    assert "Biuro Popytu" in HTML
    assert 'id="mkt-back-to-desk"' in HTML
    assert "more-sheet-btn--legacy" in HTML
    assert 'data-view="marketing"' not in HTML[HTML.index('id="main-nav"'): HTML.index('id="bottom-nav"')]


def test_home_copy_not_vhq_primary():
    home = HTML[HTML.index('id="view-home"'): HTML.index('id="view-demand-desk"')]
    assert "Primary dashboard = Virtual HQ" not in home
    assert "Biuro Popytu" in home
    assert "legacy console" in home.lower() or "Legacy" in home


def test_more_sheet_btn_css_rule():
    assert ".more-sheet-btn," in CSS
    assert "#more-sheet-close" in CSS
    assert "min-height: var(--touch)" in CSS.split(".more-sheet-btn,")[1][:200]


def test_navigate_to_view_wired_in_nav():
    assert "async function navigateToView(view)" in APP
    assert "await navigateToView(view)" in APP.split("function bindNavButtons(selector)")[1][:2500]


def test_p1_resilient_tab_loaders():
    analytics = APP.split("async function loadAnalytics()")[1][:2200]
    assert "snapErr" in analytics
    assert ".catch((e)" in analytics
    assert "Zaloguj się (/commander lub JWT), aby załadować analitykę" in analytics
    agents = APP.split("async function loadAgents()")[1][:800]
    assert "Zaloguj się (/commander lub JWT), aby załadować rejestr agentów" in agents
    assert "mkt-retry-global" in APP
    assert "Sesja wymagana" in APP.split("async function loadMarketing()")[1][:1200]


def test_refresh_loads_without_token_gate():
    start = APP.index("async function refresh()")
    end = APP.index("\nasync function navigateToView", start)
    body = APP[start:end]
    assert "if (!getToken()) return" not in body
