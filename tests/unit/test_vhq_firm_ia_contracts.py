"""VF-VHQ-FIRM-IA-00 UI string contracts (no browser)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = (ROOT / "commander-ui" / "app.js").read_text(encoding="utf-8")
HTML = (ROOT / "commander-ui" / "index.html").read_text(encoding="utf-8")


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


def test_firm_stage_on_core_rooms():
    for room_id, stage in [
        ("marketing-studio", "demand"),
        ("sales-room", "sell"),
        ("wizard-quote", "sell"),
        ("order-desk", "deliver"),
        ("mission-control", "direct"),
    ]:
        assert f'"{room_id}"' in APP
        # room block contains firmStage
        idx = APP.index(f'"{room_id}":')
        chunk = APP[idx : idx + 800]
        assert f'firmStage: "{stage}"' in chunk


def test_order_desk_still_parked_ev_w2_010():
    idx = APP.index('"order-desk":')
    chunk = APP[idx : idx + 1200]
    assert 'status: "PARKED"' in chunk
    assert "EV-W2-010" in chunk
    assert "unlockHint" in chunk
