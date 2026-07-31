"""VF-VHQ-FIRM-IA-00 UI string contracts (no browser)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = (ROOT / "commander-ui" / "app.js").read_text(encoding="utf-8")
HTML = (ROOT / "commander-ui" / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "commander-ui" / "styles.css").read_text(encoding="utf-8")

EXPECTED_FIRM_STAGES = {
    "mission-control": "direct",
    "approval-vault": "direct",
    "ai-agent-health": "direct",
    "boardroom": "direct",
    "analytics-finance": "direct",
    "compliance-audit": "direct",
    "knowledge-library": "direct",
    "data-ai-lab": "direct",
    "vcms-os-zone": "direct",
    "reception": "demand",
    "sales-room": "sell",
    "wizard-quote": "sell",
    "marketing-studio": "demand",
    "client-support": "sell",
    "design-studio": "sell",
    "design-agent-probe": "direct",
    "order-desk": "deliver",
    "production-control": "deliver",
    "preflight-quality": "deliver",
    "dispatch-returns": "deliver",
    "supplier-dock": "deliver",
    "asset-warehouse": "deliver",
    "partner-production-network": "deliver",
}

DELIVER_UNLOCK_ROOMS = [
    "order-desk",
    "production-control",
    "preflight-quality",
    "dispatch-returns",
    "supplier-dock",
    "asset-warehouse",
    "partner-production-network",
]


def test_esc_ladder_does_not_parent_to_console():
    # After fix: vhqEscLadder must not call vhqGoConsole when on MC
    assert "vhqGoConsole({ focusAuth: false, historyMode: \"push\" });" not in _esc_ladder_body()
    assert "stay in HQ" in APP or "Esc ladder ends at Mission Control" in APP


def _esc_ladder_body() -> str:
    start = APP.index("function vhqEscLadder()")
    end = APP.index("\nfunction ", start + 1)
    return APP[start:end]


def test_hint_does_not_send_esc_to_console():
    assert "Esc: room → Mission Control → Operations Console" not in HTML
    assert "Operations Console" not in HTML.split("vhq-shell__hint")[1][:200]


def test_tools_cta_not_operations_console_label():
    # #vhq-to-console button text
    assert ">Operations Console</button>" not in HTML or "Tools" in HTML
    assert "Tools / Sign in" in HTML or "Narzędzia / Logowanie" in HTML


def _room_chunk(room_id: str, span: int = 1400) -> str:
    idx = APP.index(f'"{room_id}":')
    return APP[idx : idx + span]


def test_firm_stage_on_room_manifest():
    for room_id, stage in EXPECTED_FIRM_STAGES.items():
        assert f'"{room_id}"' in APP
        chunk = _room_chunk(room_id)
        assert f'firmStage: "{stage}"' in chunk
        assert "firmRole" in chunk


def test_room_panel_renders_firm_role_and_unlock_hint_copy():
    assert 'vhqEl("p", "vhq-firm-role", room.firmRole)' in APP
    assert 'vhqEl("p", "hint vhq-unlock-hint", room.unlockHint)' in APP


def test_deliver_rooms_keep_unlock_hints_without_fake_live_claims():
    for room_id in DELIVER_UNLOCK_ROOMS:
        chunk = _room_chunk(room_id)
        assert "unlockHint" in chunk
    chunk = _room_chunk("order-desk")
    assert 'status: "PARKED"' in chunk
    assert "EV-W2-010" in chunk
    assert "unlockHint" in chunk


def test_firm_chain_strip_and_floor_labels_present_in_html():
    assert 'id="vhq-firm-chain"' in HTML
    assert 'data-firm-stage="demand"' in HTML and "1 Popyt" in HTML
    assert 'data-firm-stage="sell"' in HTML and "2 Sprzeda" in HTML
    assert 'data-firm-stage="deliver"' in HTML and "3 Realizacja" in HTML
    assert 'data-firm-stage="direct"' in HTML and "4 Sterowanie" in HTML

    assert '>P3 Sterowanie</button>' in HTML
    assert '>P2 Wiedza / ryzyko</button>' in HTML
    assert '>P1 Popyt / sprzeda' in HTML
    assert '>P0 Realizacja</button>' in HTML

    assert "P3 — Sterowanie" in HTML
    assert "P2 — Wiedza / ryzyko" in HTML
    assert "P1 — Popyt / sprzeda" in HTML
    assert "P0 — Realizacja" in HTML


def test_firm_chain_css_and_js_contracts_present():
    assert ".vhq-firm-chain" in CSS
    assert ".vhq-firm-stage" in CSS
    assert ".vhq-firm-stage.is-active" in CSS
    assert ".vhq-room-card[data-firm-stage].is-dim" in CSS

    assert 'const VHQ_FIRM_STAGES = ["demand", "sell", "deliver", "direct"];' in APP
    assert "function vhqSetFirmStageFilter(stage)" in APP
    assert 'document.querySelectorAll(".vhq-firm-stage")' in APP
    assert 'document.querySelectorAll(".vhq-room-card[data-firm-stage]")' in APP
    assert 'card.classList.toggle("is-dim", stage && !match);' in APP
    assert "function vhqBindFirmChain()" in APP
    assert "vhqBindFirmChain();" in APP
    assert "vhqSetFirmStageFilter(room.firmStage" in APP
    assert "btn.dataset.firmStage = room.firmStage" in APP
