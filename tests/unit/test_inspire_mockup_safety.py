"""Unit tests for inspire mockup safety heuristic."""

from __future__ import annotations

import io

from PIL import Image, ImageDraw

from agent.inspire.mockup_safety import check_mockup_safety, estimate_text_risk


def _blank_van_png() -> bytes:
    img = Image.new("RGB", (1024, 768), (245, 245, 245))
    draw = ImageDraw.Draw(img)
    draw.rectangle((80, 200, 920, 620), fill=(255, 255, 255))
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


def _van_with_text_png() -> bytes:
    img = Image.new("RGB", (1024, 768), (200, 200, 200))
    draw = ImageDraw.Draw(img)
    draw.rectangle((80, 200, 920, 620), fill=(255, 255, 255))
    for y in range(360, 420, 8):
        draw.rectangle((180, y, 820, y + 4), fill=(0, 40, 120))
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


def test_blank_van_low_text_risk() -> None:
    risk = estimate_text_risk(_blank_van_png())
    assert risk < 0.25


def test_text_lines_raise_risk() -> None:
    assert estimate_text_risk(_van_with_text_png()) > estimate_text_risk(_blank_van_png())


def test_safety_passes_clean_mockup() -> None:
    import os

    from agent.inspire.mockup_safety import _ocr_reader

    os.environ["INSPIRE_MOCKUP_OCR"] = "off"
    _ocr_reader.cache_clear()
    result = check_mockup_safety(_blank_van_png())
    assert result.ok is True


def test_scan_text_detects_phone() -> None:
    from agent.inspire.mockup_safety import _scan_text

    risk, reasons = _scan_text("Bel 06-12345678 voor service")
    assert "phone_pattern" in reasons
    assert risk >= 0.9
