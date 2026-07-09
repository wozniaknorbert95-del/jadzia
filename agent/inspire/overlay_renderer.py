"""Deterministic PIL overlay v2 — vinyl typography (logo + contact text)."""

from __future__ import annotations

import io
import logging
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from agent.inspire.layout_spec import LayoutSpec

logger = logging.getLogger(__name__)

STRIP_ELEMENTS = frozenset({"bedrijfsnaam", "telefoon"})
SLOGAN_MAX_WORDS = 6
STRIP_OPACITY = 0.85
PANEL_SHADE_ALPHA = 38  # ~15% multiply feel on RGBA layer


def _assets_fonts_dir() -> Path:
    return Path(__file__).resolve().parent / "assets" / "fonts"


def _font_candidates(bold: bool) -> tuple[str, ...]:
    bundled = _assets_fonts_dir()
    names = (
        ("RobotoCondensed-Bold.ttf", "RobotoCondensed-Regular.ttf")
        if bold
        else ("RobotoCondensed-Regular.ttf", "RobotoCondensed-Bold.ttf")
    )
    bundled_paths = tuple(str(bundled / n) for n in names if (bundled / n).is_file())
    system = (
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
    )
    if bold:
        return bundled_paths + system[:4] + system[4:6] + system[6:8]
    return bundled_paths + (system[1], system[0], system[3], system[2], system[5], system[4], system[7], system[6])


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    size = max(12, size)
    for path in _font_candidates(bold):
        if Path(path).is_file():
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    raw = hex_color.lstrip("#")
    if len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)
    if len(raw) != 6:
        return 17, 17, 17
    return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)


def _luminance(hex_color: str) -> float:
    r, g, b = _hex_to_rgb(hex_color)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0


def _strip_colors(text_color: str) -> tuple[tuple[int, int, int, int], tuple[int, int, int]]:
    """Return (strip_rgba, ink_rgb) for vinyl contrast bar."""
    if _luminance(text_color) > 0.55:
        return (0, 0, 0, int(255 * STRIP_OPACITY)), (255, 255, 255)
    return (255, 255, 255, int(255 * STRIP_OPACITY)), _hex_to_rgb(text_color)


def _normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("0031"):
        digits = "0" + digits[4:]
    if digits.startswith("31") and len(digits) >= 10:
        digits = "0" + digits[2:]
    if digits.startswith("06") and len(digits) >= 10:
        return f"06-{digits[2:6]} {digits[6:10]}"
    if digits.startswith("0"):
        return raw.strip()
    return raw.strip()


def _truncate_slogan(text: str, max_words: int = SLOGAN_MAX_WORDS) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words])


def _text_for_element(element_type: str, brief: dict[str, str | list]) -> str:
    if element_type == "bedrijfsnaam":
        return str(brief.get("bedrijfsnaam", ""))
    if element_type == "telefoon":
        return _normalize_phone(str(brief.get("telefoon", "")))
    if element_type == "website":
        return str(brief.get("website", ""))
    if element_type == "slogan":
        return _truncate_slogan(str(brief.get("slogan", "")))
    return ""


def _text_bbox(font: ImageFont.FreeTypeFont | ImageFont.ImageFont, text: str) -> tuple[int, int]:
    dummy = Image.new("RGB", (4, 4))
    draw = ImageDraw.Draw(dummy)
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _fit_font(
    text: str,
    max_w: int,
    max_h: int,
    start_px: int,
    bold: bool,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    size = start_px
    while size >= 12:
        font = _load_font(size, bold=bold)
        tw, th = _text_bbox(font, text)
        if tw <= max_w and th <= max_h:
            return font
        size -= 1
    return _load_font(12, bold=bold)


def _draw_panel_shade(base: Image.Image, x: int, y: int, w: int, h: int) -> None:
    shade = Image.new("RGBA", (w, h), (0, 0, 0, PANEL_SHADE_ALPHA))
    base.paste(shade, (x, y), shade)


def _draw_vinyl_text(
    base: Image.Image,
    *,
    text: str,
    x: int,
    y: int,
    aw: int,
    ah: int,
    start_px: int,
    text_color: str,
    bold: bool,
    use_strip: bool,
) -> None:
    if not text:
        return
    font = _fit_font(text, max(1, aw - 8), max(1, ah - 4), start_px, bold)
    tw, th = _text_bbox(font, text)
    tx = x + max(0, (aw - tw) // 2)
    ty = y + max(0, (ah - th) // 2)

    if use_strip:
        pad_x, pad_y = 6, 4
        strip_rgba, ink = _strip_colors(text_color)
        strip = Image.new(
            "RGBA",
            (min(aw, tw + pad_x * 2), min(ah, th + pad_y * 2)),
            strip_rgba,
        )
        sx = x + max(0, (aw - strip.width) // 2)
        sy = y + max(0, (ah - strip.height) // 2)
        base.paste(strip, (sx, sy), strip)
        draw = ImageDraw.Draw(base)
        draw.text((sx + pad_x, sy + pad_y), text, fill=ink, font=font)
        return

    draw = ImageDraw.Draw(base)
    draw.text((tx, ty), text, fill=_hex_to_rgb(text_color), font=font)


def apply_overlay(
    png_bytes: bytes,
    layout: LayoutSpec,
    logo_bytes: bytes,
    brief: dict[str, str | list],
) -> bytes:
    """Apply logo and vinyl typography overlays on fal background PNG."""
    base = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    w, h = base.size

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
                lx = ax + max(0, (aw - logo.width) // 2)
                ly = ay + max(0, (ah - logo.height) // 2)
                base.paste(logo, (lx, ly), logo)
                continue

            if element.type == "accent_graphic":
                continue

            text = _text_for_element(element.type, brief)
            if not text:
                continue

            bold = element.style.weight in ("bold", "700") or element.type in ("bedrijfsnaam", "telefoon")
            color = element.style.color if element.style.color.startswith("#") else "#111111"
            use_strip = element.type in STRIP_ELEMENTS
            if element.type in ("website", "slogan"):
                _draw_panel_shade(base, ax, ay, aw, ah)

            _draw_vinyl_text(
                base,
                text=text,
                x=ax,
                y=ay,
                aw=aw,
                ah=ah,
                start_px=element.style.size_px,
                text_color=color,
                bold=bold,
                use_strip=use_strip,
            )

    out = io.BytesIO()
    base.convert("RGB").save(out, format="PNG", optimize=True)
    return out.getvalue()
