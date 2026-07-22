"""CMD-DASH Wave A — static UI contracts (Decision Rail, no execute, D0.15)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "commander-ui" / "index.html").read_text(encoding="utf-8")
JS = (ROOT / "commander-ui" / "app.js").read_text(encoding="utf-8")
CSS = (ROOT / "commander-ui" / "styles.css").read_text(encoding="utf-8")


def test_cache_bust_mkt_dash04():
    assert HTML.count("mkt-dash04") >= 2


def test_decision_rail_and_forensic_present():
    assert 'id="mkt-decision-rail"' in HTML
    assert 'id="mkt-exec-chips"' in HTML
    assert 'id="mkt-forensic"' in HTML
    assert "H-Meta" not in HTML
    assert 'id="mkt-os-strip"' not in HTML


def test_ds0_severity_primitives():
    for token in (
        ".sev-chip--ok",
        ".sev-chip--warn",
        ".sev-chip--critical",
        ".exec-rail",
        ".forensic-panel",
        ".decision-card",
        ".kpi-tile",
    ):
        assert token in CSS


def test_wave_a_read_paths_wired():
    for path in (
        "/api/v1/commander/marketing/propose-preflight",
        "/api/v1/commander/marketing/breakers",
        "/api/v1/commander/marketing/shadow/accuracy",
        "/api/v1/commander/marketing/brain-bus",
        "/api/v1/commander/marketing/memory/status",
    ):
        assert path in JS


def test_hard_stop_no_execute_ui():
    assert "actions/execute" not in JS
    assert "marketing/actions/execute" not in HTML


def test_d015_five_primary_nav_no_audit_peer():
    # bottom nav block: five peers, Audyt only secondary (settings link)
    start = HTML.index('id="bottom-nav"')
    end = HTML.index("</nav>", start)
    bottom = HTML[start:end]
    assert bottom.count('data-view="') == 5
    assert 'data-view="audit"' not in bottom
    assert 'id="settings-to-audit"' in HTML
