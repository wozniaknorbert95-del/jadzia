"""Unit tests for tier B/A inspire prompts."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent.inspire.prompt import BriefContext, build_prompt
from agent.inspire.tier_resolver import resolve_tier_skus

MATRIX = (
    Path(__file__).resolve().parents[2].parent
    / "zzpackage.flexgrafik.nl"
    / "brain-design-agent"
    / "tier-matrix.json"
)


@pytest.fixture
def matrix_path() -> Path:
    if not MATRIX.is_file():
        pytest.skip(f"tier matrix missing: {MATRIX}")
    return MATRIX


def test_tier_b_prompt_contains_coverage(matrix_path: Path) -> None:
    tier_b, _ = resolve_tier_skus("caddy", {}, matrix_path=matrix_path)
    ctx = BriefContext(
        vehicle="caddy",
        branche="Elektricien",
        bedrijfsnaam="Test BV",
        telefoon="06-12345678",
        website="",
        brand_colors=["#003366"],
        tekst_opties=["telefoon"],
        slogan="",
        positionering="strak",
    )
    positive, _ = build_prompt(ctx, "tier_b", tier_b)
    assert tier_b.coverage in positive
    assert "Smart Start" in positive
    assert "strak vs opvallend" not in positive.lower()


def test_tier_a_prompt_premium_label(matrix_path: Path) -> None:
    _, tier_a = resolve_tier_skus("caddy", {"branding_goal": "max_visibility"}, matrix_path=matrix_path)
    ctx = BriefContext(
        vehicle="caddy",
        branche="Bouw",
        bedrijfsnaam="Bouw BV",
        telefoon="",
        website="",
        brand_colors=["#ffcc00"],
        tekst_opties=[],
        slogan="",
        positionering="opvallend",
    )
    positive, _ = build_prompt(ctx, "tier_a", tier_a)
    assert "Premium Presence" in positive
    assert tier_a.coverage in positive
