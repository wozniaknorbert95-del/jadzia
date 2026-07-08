"""Unit tests for inspire tier_resolver."""

from __future__ import annotations

from pathlib import Path

import pytest

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


def test_caddy_private_use_prefers_magnet(matrix_path: Path) -> None:
    b, a = resolve_tier_skus("caddy", {"vehicle_use": "private"}, matrix_path=matrix_path)
    assert b.sku == "MA-005"
    assert a.sku == "CS-SET-PRO-ZZP"


def test_caddy_permanent_low_budget(matrix_path: Path) -> None:
    b, a = resolve_tier_skus(
        "caddy", {"branding_goal": "permanent_low_budget"}, matrix_path=matrix_path
    )
    assert b.sku == "CS-SET-LOGO-CONTACT"


def test_caddy_max_visibility_wrap(matrix_path: Path) -> None:
    b, a = resolve_tier_skus(
        "caddy", {"branding_goal": "max_visibility"}, matrix_path=matrix_path
    )
    assert a.sku == "NA-WRAP-BASIC"


def test_bus_l_defaults(matrix_path: Path) -> None:
    b, a = resolve_tier_skus("bus_l", {}, matrix_path=matrix_path)
    assert b.sku == "BLS-SET-LOGO-CONTACT"
    assert a.sku == "NA-WRAP-PRO"


def test_bus_xl_defaults(matrix_path: Path) -> None:
    b, a = resolve_tier_skus("bus_xl", {}, matrix_path=matrix_path)
    assert b.sku == "BXLS-SET-LOGO-CONTACT"
    assert a.sku == "NA-WRAP-MAX"


def test_passenger_defaults(matrix_path: Path) -> None:
    b, a = resolve_tier_skus("passenger", {}, matrix_path=matrix_path)
    assert b.sku == "PS-SET-LOGO-CONTACT"
    assert a.sku == "PS-SET-PRO-ZZP"


def test_explicit_sku_overrides(matrix_path: Path) -> None:
    b, a = resolve_tier_skus(
        "caddy",
        {"mockup_b_sku": "MA-005", "mockup_a_sku": "NA-WRAP-BASIC"},
        matrix_path=matrix_path,
    )
    assert b.sku == "MA-005"
    assert a.sku == "NA-WRAP-BASIC"


def test_invalid_vehicle_raises(matrix_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown vehicle"):
        resolve_tier_skus("truck", {}, matrix_path=matrix_path)
