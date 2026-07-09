"""Deterministic PIL overlay — logo + contact text from LayoutSpec."""

from __future__ import annotations

import io
import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from agent.inspire.layout_spec import LayoutSpec

logger = logging.getLogger(__name__)

FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/arial.ttf",
)


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    paths = FONT_CANDIDATES if bold else reversed(FONT_CANDIDATES)
    for path in paths:
        if Path(path).is_file():
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def _text_for_element(element_type: str, brief: dict[str, str | list]) -> str:
    if element_type == "bedrijfsnaam":
        return str(brief.get("bedrijfsnaam", ""))
    if element_type == "telefoon":
        return str(brief.get("telefoon", ""))
    if element_type == "website":
        return str(brief.get("website", ""))
    if element_type == "slogan":
        return str(brief.get("slogan", ""))
    return ""


def apply_overlay(
    png_bytes: bytes,
    layout: LayoutSpec,
    logo_bytes: bytes,
    brief: dict[str, str | list],
) -> bytes:
    """Apply logo and text overlays on fal background PNG."""
    base = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    w, h = base.size
    draw = ImageDraw.Draw(base)

    for panel in layout.panels:
        for element in panel.elements:
            ax = int(w * element.anchor.x_pct)
            ay = int(h * element.anchor.y_pct)
            aw = max(1, int(w * element.anchor.w_pct))
            ah = max(1, int(h * element.anchor.h_pct))

            if element.type == "logo":
                try:
                    logo = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
                except Exception as exc:
                    logger.warning("overlay logo skip: %s", exc)
                    continue
                ratio = min(aw / max(logo.width, 1), ah / max(logo.height, 1))
                new_size = (max(1, int(logo.width * ratio)), max(1, int(logo.height * ratio)))
                logo = logo.resize(new_size, Image.Resampling.LANCZOS)
                base.paste(logo, (ax, ay), logo)
                continue

            if element.type == "accent_graphic":
                continue

            text = _text_for_element(element.type, brief)
            if not text:
                continue

            bold = element.style.weight in ("bold", "700")
            font = _load_font(element.style.size_px, bold=bold)
            color = element.style.color if element.style.color.startswith("#") else "#111111"
            draw.text((ax, ay), text, fill=color, font=font)

    out = io.BytesIO()
    base.convert("RGB").save(out, format="PNG", optimize=True)
    return out.getvalue()
