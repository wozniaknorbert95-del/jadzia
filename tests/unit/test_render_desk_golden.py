"""Golden desk status → render logic strings in app.js."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = (ROOT / "commander-ui" / "app.js").read_text(encoding="utf-8")
GOLDEN = json.loads(
    (ROOT / "tests" / "fixtures" / "desk_status_v21.min.json").read_text(encoding="utf-8")
)
MIXED = json.loads(
    (ROOT / "tests" / "fixtures" / "desk_status_v21_mixed.min.json").read_text(encoding="utf-8")
)


def _desk_js() -> str:
    marker = "// --- Demand Desk (Etap 5) ---"
    return APP[APP.index(marker) :]


def test_golden_contract_keys_referenced_in_render():
    section = _desk_js()
    for key in (
        "robota_dnia",
        "data_mode",
        "cash_warning",
        "dual_cash",
        "top_wizard_assets",
        "top_wizard_note",
        "hitl_queue",
        "hunt_queue",
        "week_calendar",
        "shells_line",
        "footer",
        "diagnostics",
        "contract_version",
    ):
        assert key in section, key


def test_render_dual_cash_columns_string():
    assert "dual.columns" in _desk_js()
    assert "verdict, offerte_only" in _desk_js()


def test_render_wow_format_helper():
    assert "function deskFormatWow" in _desk_js()
    assert "desk-wow--down" in _desk_js()


def test_render_prep_disables_hitl_actions():
    section = _desk_js()
    assert "desk_action === \"PREP\"" in section or 'desk_action === "PREP"' in section
    assert "isPrep" in section


def test_render_stale_and_empty_data_hints():
    section = _desk_js()
    assert "desk-stale-hint" in section
    assert "desk-empty-data-hint" in section


def test_golden_fixture_has_core_fields():
    for key in ("kpi", "screen", "footer", "data_mode", "robota_dnia"):
        assert key in GOLDEN


def test_mixed_fixture_data_mode():
    assert MIXED["data_mode"] in ("MIXED", "FIXTURE", "REAL")
