"""Unit tests for creative director (Brain3)."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent.inspire.brand_strategist import load_panel_map, load_playbook, produce_brand_strategy
from agent.inspire.creative_director import produce_layout_specs
from agent.inspire.tier_resolver import resolve_tier_skus

PLAYBOOK = (
    Path(__file__).resolve().parents[2].parent
    / "zzpackage.flexgrafik.nl"
    / "brain-design-agent"
    / "marketing-playbook-nl-zzp.json"
)
PANEL_MAP = (
    Path(__file__).resolve().parents[2].parent
    / "zzpackage.flexgrafik.nl"
    / "brain-design-agent"
    / "panel-map.json"
)
MATRIX = (
    Path(__file__).resolve().parents[2].parent
    / "zzpackage.flexgrafik.nl"
    / "brain-design-agent"
    / "tier-matrix.json"
)


@pytest.fixture
def fixtures() -> tuple[dict, dict, Path]:
    if not PLAYBOOK.is_file() or not PANEL_MAP.is_file() or not MATRIX.is_file():
        pytest.skip("zzpackage brain assets missing")
    return load_playbook(PLAYBOOK), load_panel_map(PANEL_MAP), MATRIX


def test_layout_specs_quietforge(fixtures: tuple[dict, dict, Path]) -> None:
    playbook, panel_map, matrix_path = fixtures
    tier_b, tier_a = resolve_tier_skus("caddy", {}, matrix_path=matrix_path)
    strategy = produce_brand_strategy(
        branche="IT-automatisering",
        diensten="Automation Map",
        doelgroep="NL ZZP",
        positionering="strak",
        brand_colors=["#111111"],
        tier_b=tier_b,
        tier_a=tier_a,
        playbook=playbook,
        panel_map=panel_map,
    )
    brief = {
        "branche": "IT-automatisering",
        "diensten": "Automation Map",
        "doelgroep": "NL ZZP",
        "positionering": "strak",
        "bedrijfsnaam": "Quietforge",
        "telefoon": "06-12345678",
        "website": "quietforge.flexgrafik.nl",
        "slogan": "Conversion Systems Architect",
        "brand_colors": ["#111111"],
        "tekst_opties": ["telefoon", "website", "slogan"],
    }
    layout_b, layout_a = produce_layout_specs(
        vehicle="caddy",
        brief=brief,
        strategy=strategy,
        tier_b=tier_b,
        tier_a=tier_a,
        panel_map=panel_map,
    )
    assert layout_b.variant == "tier_b"
    assert layout_a.variant == "tier_a"
    assert layout_b.sku == tier_b.sku
    assert "Automation Map" in layout_b.fal_background_prompt
    assert "no words" in layout_b.fal_background_prompt.lower() or "no typography" in layout_b.fal_background_prompt.lower()

    b_types = [el.type for p in layout_b.panels for el in p.elements]
    assert "logo" in b_types
    assert "bedrijfsnaam" in b_types
    assert len(layout_a.panels) >= len(layout_b.panels)
