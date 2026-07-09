"""Reference image composite — vehicle template + logo hint for fal kontext."""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image

if TYPE_CHECKING:
    from agent.inspire.layout_spec import LayoutSpec

logger = logging.getLogger(__name__)

VEHICLE_TEMPLATE = {
    "caddy": "voertuig_caddy.png",
    "bus_l": "voertuig_bus_l.png",
    "bus_xl": "voertuig_bus_xl.png",
    "passenger": "voertuig_passenger.png",
}

LOGO_BOX = {
    "caddy": (0.38, 0.42, 0.22),
    "bus_l": (0.35, 0.40, 0.25),
    "bus_xl": (0.35, 0.40, 0.25),
    "passenger": (0.40, 0.45, 0.18),
}


def resolve_assets_dir() -> Path:
    import os

    custom = os.getenv("ZZPACKAGE_THEME_ASSETS", "").strip()
    if custom:
        return Path(custom)
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "zzpackage.flexgrafik.nl" / "flexgrafik-wizard-theme" / "assets" / "images"
        if candidate.is_dir():
            return candidate
    return Path("assets/images")


def _paste_logo(base: Image.Image, logo_bytes: bytes, x_pct: float, y_pct: float, w_pct: float) -> None:
    w, h = base.size
    try:
        logo = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
    except Exception as exc:
        raise ValueError("Logo could not be read as image") from exc
    max_w = int(w * w_pct)
    ratio = max_w / max(logo.width, 1)
    new_size = (max(1, int(logo.width * ratio)), max(1, int(logo.height * ratio)))
    logo = logo.resize(new_size, Image.Resampling.LANCZOS)
    px, py = int(w * x_pct), int(h * y_pct)
    base.paste(logo, (px, py), logo)


def build_reference_png_from_layout(
    vehicle: str,
    logo_bytes: bytes,
    layout: LayoutSpec,
) -> bytes:
    """LayoutSpec-aware ref: vehicle template + logo hint at layout anchor (no contact text)."""
    assets = resolve_assets_dir()
    tpl_name = VEHICLE_TEMPLATE.get(vehicle, "voertuig_caddy.png")
    tpl_path = assets / tpl_name
    if not tpl_path.is_file():
        raise FileNotFoundError(f"Vehicle template not found: {tpl_path}")

    base = Image.open(tpl_path).convert("RGBA")
    logo_placed = False
    for panel in layout.panels:
        for element in panel.elements:
            if element.type == "logo":
                _paste_logo(
                    base,
                    logo_bytes,
                    element.anchor.x_pct,
                    element.anchor.y_pct,
                    element.anchor.w_pct,
                )
                logo_placed = True
                break
        if logo_placed:
            break

    if not logo_placed:
        bx = LOGO_BOX.get(vehicle, LOGO_BOX["caddy"])
        _paste_logo(base, logo_bytes, bx[0], bx[1], bx[2])

    out = io.BytesIO()
    base.convert("RGB").save(out, format="PNG", optimize=True)
    return out.getvalue()


def build_reference_png(
    vehicle: str,
    logo_bytes: bytes,
    bedrijfsnaam: str = "",
    telefoon: str = "",
    layout: LayoutSpec | None = None,
) -> bytes:
    """PIL composite: vehicle template + logo hint only (no contact text for fal)."""
    if layout is not None:
        return build_reference_png_from_layout(vehicle, logo_bytes, layout)

    assets = resolve_assets_dir()
    tpl_name = VEHICLE_TEMPLATE.get(vehicle, "voertuig_caddy.png")
    tpl_path = assets / tpl_name
    if not tpl_path.is_file():
        raise FileNotFoundError(f"Vehicle template not found: {tpl_path}")

    base = Image.open(tpl_path).convert("RGBA")
    bx = LOGO_BOX.get(vehicle, LOGO_BOX["caddy"])
    _paste_logo(base, logo_bytes, bx[0], bx[1], bx[2])
    _ = bedrijfsnaam, telefoon

    out = io.BytesIO()
    base.convert("RGB").save(out, format="PNG", optimize=True)
    return out.getvalue()
