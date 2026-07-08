"""Reference image composite — vehicle template + logo hint for fal kontext."""

from __future__ import annotations

import io
import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

VEHICLE_TEMPLATE = {
    "caddy": "voertuig_caddy.png",
    "bus_l": "voertuig_bus_l.png",
    "bus_xl": "voertuig_bus_xl.png",
    "passenger": "voertuig_passenger.png",
}

# Logo placement heuristic per vehicle (x, y, max_w fraction of image width)
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
    # Sibling repo default (local dev)
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "zzpackage.flexgrafik.nl" / "flexgrafik-wizard-theme" / "assets" / "images"
        if candidate.is_dir():
            return candidate
    return Path("assets/images")


def build_reference_png(
    vehicle: str,
    logo_bytes: bytes,
    bedrijfsnaam: str,
    telefoon: str,
) -> bytes:
    """PIL composite: vehicle picker + logo + company name (approximate inspiration ref)."""
    assets = resolve_assets_dir()
    tpl_name = VEHICLE_TEMPLATE.get(vehicle, "voertuig_caddy.png")
    tpl_path = assets / tpl_name
    if not tpl_path.is_file():
        raise FileNotFoundError(f"Vehicle template not found: {tpl_path}")

    base = Image.open(tpl_path).convert("RGBA")
    w, h = base.size

    try:
        logo = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
    except Exception as exc:
        raise ValueError("Logo could not be read as image") from exc

    bx = LOGO_BOX.get(vehicle, LOGO_BOX["caddy"])
    max_w = int(w * bx[2])
    ratio = max_w / max(logo.width, 1)
    new_size = (max(1, int(logo.width * ratio)), max(1, int(logo.height * ratio)))
    logo = logo.resize(new_size, Image.Resampling.LANCZOS)
    px, py = int(w * bx[0]), int(h * bx[1])
    base.paste(logo, (px, py), logo)

    draw = ImageDraw.Draw(base)
    try:
        font = ImageFont.truetype("arial.ttf", max(14, int(h * 0.035)))
    except OSError:
        font = ImageFont.load_default()
    text_y = py + logo.height + 8
    draw.text((px, text_y), bedrijfsnaam[:40], fill=(20, 20, 20, 255), font=font)
    if telefoon:
        draw.text((px, text_y + int(h * 0.05)), telefoon[:20], fill=(40, 40, 40, 255), font=font)

    out = io.BytesIO()
    base.convert("RGB").save(out, format="PNG", optimize=True)
    return out.getvalue()
