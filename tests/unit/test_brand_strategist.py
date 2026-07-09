"""Unit tests for brand strategist (Brain2)."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent.inspire.brand_strategist import load_playbook, produce_brand_strategy
from agent.inspire.tier_resolver import resolve_tier_skus

PLAYBOOK = (
    Path(__file__).resolve().parents[2].parent
    / "zzpackage.flexgrafik.nl"
    / "brain-design-agent"
    / "marketing-playbook-nl-zzp.json"
)
MATRIX = (
    Path(__file__).resolve().parents[2].parent
    / "zzpackage.flexgrafik.nl"
    / "brain-design-agent"
    / "tier-matrix.json"
)


@pytest.fixture
def playbook_path() -> Path:
    if not PLAYBOOK.is_file():
        pytest.skip(f"playbook missing: {PLAYBOOK}")
    return PLAYBOOK


@pytest.fixture
def matrix_path() -> Path:
    if not MATRIX.is_file():
        pytest.skip(f"tier matrix missing: {MATRIX}")
    return MATRIX


def test_quietforge_strategy(playbook_path: Path, matrix_path: Path) -> None:
    playbook = load_playbook(playbook_path)
    tier_b, tier_a = resolve_tier_skus("caddy", {}, matrix_path=matrix_path)
    strategy = produce_brand_strategy(
        branche="IT-automatisering",
        diensten="Automation Map, inbox automation",
        doelgroep="NL ZZP en MKB",
        positionering="strak",
        brand_colors=["#1a1a1a", "#d4af37"],
        tier_b=tier_b,
        tier_a=tier_a,
        playbook=playbook,
    )
    assert strategy.branche_cluster == "it_zzp"
    assert strategy.sales_angle_nl
    assert "logo" in strategy.message_hierarchy
    assert len(strategy.active_panels_a) >= len(strategy.active_panels_b)


def test_bouw_cluster(playbook_path: Path, matrix_path: Path) -> None:
    playbook = load_playbook(playbook_path)
    tier_b, tier_a = resolve_tier_skus("bus_l", {}, matrix_path=matrix_path)
    strategy = produce_brand_strategy(
        branche="Schilderbedrijf",
        diensten="Binnen- en buitenschilderwerk",
        doelgroep="Particulieren regio Brabant",
        positionering="opvallend",
        brand_colors=["#ffcc00"],
        tier_b=tier_b,
        tier_a=tier_a,
        playbook=playbook,
    )
    assert strategy.branche_cluster == "bouw_schilder"
    assert strategy.positionering == "opvallend"
