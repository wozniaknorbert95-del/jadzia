"""CMD-DASH Complete — static UI contracts Waves A–D (cache mkt-dash05)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "commander-ui" / "index.html").read_text(encoding="utf-8")
JS = (ROOT / "commander-ui" / "app.js").read_text(encoding="utf-8")
CSS = (ROOT / "commander-ui" / "styles.css").read_text(encoding="utf-8")


def test_cache_bust_mkt_dash05():
    assert HTML.count("mkt-dash05") >= 2
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
