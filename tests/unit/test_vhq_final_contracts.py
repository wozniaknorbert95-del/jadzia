"""VF-VHQ-FINAL-00 UI contracts — one Firm Chain axis (F7)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = (ROOT / "commander-ui" / "app.js").read_text(encoding="utf-8")
HTML = (ROOT / "commander-ui" / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "commander-ui" / "styles.css").read_text(encoding="utf-8")
SW = (ROOT / "commander-ui" / "sw.js").read_text(encoding="utf-8")


def test_f7_no_floor_tabrow_in_html():
    assert 'id="vhq-floors"' not in HTML
    assert ">P3 Sterowanie</button>" not in HTML
    assert ">P0 Realizacja</button>" not in HTML
    assert ">MAG Network</button>" not in HTML


def test_f7_firm_chain_is_sole_filter_nav():
    assert 'id="vhq-firm-chain"' in HTML
    assert 'data-firm-stage="demand"' in HTML
    assert 'data-firm-stage="sell"' in HTML
    assert 'data-firm-stage="deliver"' in HTML
    assert 'data-firm-stage="direct"' in HTML
    assert "vhq-stage-band" in HTML
    assert 'data-firm-stage="deliver"' in HTML


def test_f7_js_stage_browse_not_floor_tabs():
    assert "function vhqShowStageBrowse(stage" in APP
    assert "VHQ_FIRM_STAGE_LABELS" in APP
    assert "vhqShowStageBrowse(stage" in APP
    assert 'querySelectorAll(".vhq-floor-btn")' not in APP or "vhq-floor-btn" not in APP.split("vhqBindFirmChain")[0][-200:]
    # binding must not attach floor buttons
    assert 'document.querySelectorAll(".vhq-floor-btn").forEach' not in APP


def test_f7_breadcrumb_uses_stage_labels():
    assert "vhqStageLabel(" in APP
    assert "HQ › ${vhqStageLabel" in APP or "HQ › ${label}" in APP


def test_f7_deliver_honesty_banner():
    assert 'id="vhq-deliver-honesty"' in HTML
    assert "EV-W2-010" in HTML


def test_f7_finish_card_chrome():
    assert "vhq-finish-card" in HTML
    assert "Finish Card" in HTML
    assert "not live-verified" in APP


def test_f7_cache_tag_consistent():
    """F7-era literal tag (vhq-w68a) rotated away; the durable contract is that
    HTML asset tags and the SW cache name share one tag (see commander_complete_ui)."""
    import re

    m = re.search(r'app\.js\?v=([a-z0-9-]+)"', HTML)
    assert m, "app.js must carry a ?v= cache tag"
    tag = m.group(1)
    assert f"coi-commander-{tag}" in SW


def test_f7_css_stage_bands():
    assert ".vhq-stage-band" in CSS
    assert ".vhq-deliver-honesty" in CSS


def test_w3_tools_cta_copy_on_finance_and_agents():
    assert "Open in Tools · Analityka" in APP
    assert "Open in Tools · Agenci" in APP
    assert "FREEZE do 2026-08-06" in APP
    assert "owner ${room.owner" in APP
