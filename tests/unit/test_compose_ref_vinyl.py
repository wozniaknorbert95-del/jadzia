"""Unit tests for compose_ref v3 vinyl zone painting."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from agent.inspire.compose_ref import build_reference_png_from_layout, resolve_assets_dir
from agent.inspire.layout_spec import ElementAnchor, LayoutSpec, VinylZone

ASSETS = resolve_assets_dir()


@pytest.mark.skipif(not (ASSETS / "voertuig_caddy.png").is_file(), reason="vehicle template missing")
def test_compose_ref_paints_vinyl_zones() -> None:
    layout = LayoutSpec(
        variant="tier_b",
        sku="MA-005",
        panels=[],
        vinyl_zones=[
            VinylZone(
                panel_id="deur",
                anchor=ElementAnchor(x_pct=0.35, y_pct=0.35, w_pct=0.25, h_pct=0.3),
                fill_hex="#e8a33d",
                opacity=0.7,
            )
        ],
        fal_background_prompt="test no words no readable text",
    )
    logo = (Path(__file__).resolve().parents[2].parent / "zzpackage.flexgrafik.nl" / "docs" / "ops" / "spike-01" / "logos" / "elek-logo.png")
    if not logo.is_file():
        pytest.skip("logo fixture missing")
    png = build_reference_png_from_layout("caddy", logo.read_bytes(), layout)
    img = Image.open(__import__("io").BytesIO(png)).convert("RGB")
    # Sample center of zone — should differ from corner (zone painted)
    zone_px = img.getpixel((int(img.width * 0.42), int(img.height * 0.45)))
    corner_px = img.getpixel((10, 10))
    assert zone_px != corner_px
