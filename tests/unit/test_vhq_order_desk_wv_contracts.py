"""VF-ORDER-DESK-WV-00 — thin mirror Work View contracts (PARKED honesty)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = (ROOT / "commander-ui" / "app.js").read_text(encoding="utf-8")
HTML = (ROOT / "commander-ui" / "index.html").read_text(encoding="utf-8")
SW = (ROOT / "commander-ui" / "sw.js").read_text(encoding="utf-8")
DB = (ROOT / "agent" / "db.py").read_text(encoding="utf-8")


def _order_room_chunk() -> str:
    start = APP.index('"order-desk": {')
    end = APP.index('"production-control": {', start)
    return APP[start:end]


def test_w1_mirror_section_in_order_work_view():
    assert 'id="vhq-work-order-mirror"' in HTML
    assert 'id="vhq-work-order-mirror-body"' in HTML
    assert "function vhqRenderOrderDeskMirror" in APP


def test_w2_ops_state_honesty_in_renderer():
    assert '"insufficient_data"' in APP
    assert "vhqRenderOrderDeskMirror" in APP
    chunk = APP.split("function vhqRenderOrderDeskMirror")[1].split("function ")[0]
    assert "insufficient_data" in chunk
    assert "/api/v1/orders" in chunk


def test_w3_no_session_honesty():
    chunk = APP.split("function vhqRenderOrderDeskMirror")[1].split("function ")[0]
    assert "No session" in chunk or "Session required" in chunk


def test_w4_room_stays_parked_ev():
    chunk = _order_room_chunk()
    assert 'status: "PARKED"' in chunk
    assert "EV-W2-010" in chunk
    assert "ORDER-DESK-SOT-v0 ACCEPTED" in chunk
    assert "action: null" in chunk
    assert 'value: "insufficient_data"' in chunk


def test_w5_cache_vhq_w68a():
    assert "vhq-w68a" in HTML
    assert "coi-commander-shell-vhq-w68a" in SW


def test_w5_list_orders_projects_pay_fields():
    assert "orders.payment_status" in DB
    assert "orders.paid_at" in DB
    assert "orders.currency" in DB
    assert 'item["ops_state"] = None' in DB


def test_w4_no_fulfilil_cta_in_order_panel():
    panel = HTML.split('id="vhq-work-order"')[1].split('id="vhq-work-production"')[0]
    assert "Accept to production" not in panel
    assert "Ship" not in panel or "Hard STOP" in panel
    assert "EV-W2-010" in panel
