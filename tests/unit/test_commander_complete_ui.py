"""CMD-DASH Complete + UX Polish — static UI contracts (cache mkt-dash08)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "commander-ui" / "index.html").read_text(encoding="utf-8")
JS = (ROOT / "commander-ui" / "app.js").read_text(encoding="utf-8")
CSS = (ROOT / "commander-ui" / "styles.css").read_text(encoding="utf-8")


def test_cache_bust_mkt_dash08():
    assert HTML.count("mkt-dash08") >= 2
    assert "mkt-dash07" not in HTML
    assert "mkt-dash06" not in HTML
    assert "mkt-dash05" not in HTML
    assert "mkt-dash04" not in HTML


def test_wave_a_decision_rail():
    assert 'id="mkt-decision-rail"' in HTML
    assert "H-Meta" not in HTML
    assert "propose-preflight" in JS


def test_wave_b_home_ops_and_agents_truth():
    assert 'id="home-ops-rail"' in HTML
    assert 'id="home-ops-chips"' in HTML
    assert 'id="ai-os-map"' in HTML
    assert "phase-c-cards" not in HTML
    assert "phase-c" not in JS.lower() or "phase-c-cards" not in JS
    assert "next_expected_run" in JS


def test_wave_c_analytics_audit_more():
    assert 'id="analytics-kpi-tiles"' in HTML
    assert 'id="orders-table"' in HTML
    assert 'id="audit-verify-banner"' in HTML
    assert 'id="more-sheet"' in HTML
    assert 'id="open-more-sheet"' in HTML
    assert ".data-table" in CSS
    assert ".kpi-grid" in CSS


def test_hard_stops():
    assert "actions/execute" not in JS
    start = HTML.index('id="bottom-nav"')
    end = HTML.index("</nav>", start)
    bottom = HTML[start:end]
    assert bottom.count('data-view="') == 5
    assert 'data-view="audit"' not in bottom


def test_h1_ops_freshness_hierarchy():
    assert "freshnessSev" in JS
    assert "worstSev" in JS
    assert "worstFreshStatus" in JS
    assert "pipelineFresh" in JS
    assert 'sevChip("Freshness"' in JS
    assert "Ops: OK" in JS
    assert "Ops: UWAGA" in JS
    assert "Worker freshness:" not in JS
    assert "dowodca_last_active" not in JS


def test_h2_preflight_propose_not_panic():
    assert "isProposeMode" in JS
    assert 'text: "N/A"' in JS
    assert "runtime: propose" in JS
    assert "oczekiwane w propose" in JS


def test_h3_touch_44px():
    assert "--touch: 44px" in CSS
    assert "--touch: 40px" not in CSS


def test_m1_organic_humanize():
    assert "humanizeOrganicReason" in JS
    assert "Brak insights" in JS
    assert "text-overflow: ellipsis" in CSS


def test_m2_agents_configured_without_last():
    assert 'statusLabel === "configured"' in JS or 'statusLabel = a.status === "LIVE" && !hasLast ? "configured"' in JS
    assert '"n/a"' in JS
    assert "a.sla_ok === false" in JS


def test_m3_dtl_facts_stale():
    assert "factsStaleFromSnap" in JS
    assert "pipeline OK · facts STALE" in JS
