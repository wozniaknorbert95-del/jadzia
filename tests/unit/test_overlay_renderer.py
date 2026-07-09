"""Unit tests for overlay renderer."""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

from agent.inspire.creative_director import produce_layout_specs
from agent.inspire.brand_strategist import load_panel_map, load_playbook, produce_brand_strategy
from agent.inspire.overlay_renderer import _normalize_phone, apply_overlay
from agent.inspire.tier_resolver import resolve_tier_skus

ASSETS = Path(__file__).resolve().parents[2].parent / "zzpackage.flexgrafik.nl"
PLAYBOOK = ASSETS / "brain-design-agent" / "marketing-playbook-nl-zzp.json"
PANEL_MAP = ASSETS / "brain-design-agent" / "panel-map.json"
MATRIX = ASSETS / "brain-design-agent" / "tier-matrix.json"
VEHICLE_IMG = ASSETS / "flexgrafik-wizard-theme" / "assets" / "images" / "voertuig_caddy.png"
LOGO = ASSETS / "docs" / "ops" / "inspire-v2" / "logos" / "quietforge-logo.png"


@pytest.mark.skipif(not VEHICLE_IMG.is_file(), reason="vehicle template missing")
def test_overlay_applies_text() -> None:
    if not all(p.is_file() for p in (PLAYBOOK, PANEL_MAP, MATRIX, LOGO)):
        pytest.skip("brain assets or logo missing")

    playbook = load_playbook(PLAYBOOK)
    panel_map = load_panel_map(PANEL_MAP)
    tier_b, tier_a = resolve_tier_skus("caddy", {}, matrix_path=MATRIX)
    strategy = produce_brand_strategy(
        branche="IT",
        diensten="Automation",
        doelgroep="ZZP",
        positionering="strak",
        brand_colors=["#111"],
        tier_b=tier_b,
        tier_a=tier_a,
        playbook=playbook,
        panel_map=panel_map,
    )
    brief = {
        "bedrijfsnaam": "Quietforge",
        "telefoon": "06-12345678",
        "tekst_opties": ["telefoon"],
        "positionering": "strak",
        "brand_colors": ["#111"],
    }
    layout_b, _ = produce_layout_specs(
        vehicle="caddy",
        brief=brief,
        strategy=strategy,
        tier_b=tier_b,
        tier_a=tier_a,
        panel_map=panel_map,
    )
    base = Image.open(VEHICLE_IMG).convert("RGB")
    buf = __import__("io").BytesIO()
    base.save(buf, format="PNG")
    logo_bytes = LOGO.read_bytes()
    out = apply_overlay(buf.getvalue(), layout_b, logo_bytes, brief)
    assert len(out) > 1000
    result = Image.open(__import__("io").BytesIO(out))
    assert result.size[0] > 0


def test_overlay_v2_uses_contrast_strip_vs_flat() -> None:
    """Vinyl strip path should differ from legacy flat text at same coords."""
    w, h = 640, 400
    base = Image.new("RGB", (w, h), (180, 180, 180))
    buf = io.BytesIO()
    base.save(buf, format="PNG")
    png = buf.getvalue()

    from agent.inspire.layout_spec import ElementAnchor, ElementStyle, LayoutElement, LayoutPanel, LayoutSpec

    layout = LayoutSpec(
        variant="tier_b",
        sku="MA-005",
        panels=[
            LayoutPanel(
                id="deur",
                elements=[
                    LayoutElement(
                        type="bedrijfsnaam",
                        anchor=ElementAnchor(x_pct=0.1, y_pct=0.2, w_pct=0.5, h_pct=0.15),
                        text_from_brief=True,
                        style=ElementStyle(size_px=36, color="#050608", weight="bold"),
                    )
                ],
            )
        ],
        fal_background_prompt="test no words no readable text",
    )
    brief = {"bedrijfsnaam": "Quietforge"}
    vinyl = apply_overlay(png, layout, b"", brief)

    flat_base = Image.open(io.BytesIO(png)).convert("RGBA")
    draw = ImageDraw.Draw(flat_base)
    font = ImageFont.load_default()
    draw.text((int(w * 0.1), int(h * 0.2)), "Quietforge", fill="#050608", font=font)
    flat_buf = io.BytesIO()
    flat_base.convert("RGB").save(flat_buf, format="PNG")

    assert vinyl != flat_buf.getvalue()
    assert _normalize_phone("06-12345678") == "06-1234 5678"
