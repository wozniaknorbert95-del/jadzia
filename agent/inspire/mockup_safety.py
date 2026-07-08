"""Post-fal mockup safety — OCR text detect + NL blocklist when available."""

from __future__ import annotations

import io
import logging
import os
import re
import tempfile
from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING

from PIL import Image, ImageFilter, ImageOps

if TYPE_CHECKING:
    import easyocr  # noqa: F401

logger = logging.getLogger(__name__)

NL_BLOCKLIST = (
    "moord",
    "dood",
    "kanker",
    "hoer",
    "kut",
    "shit",
    "fuck",
)

PHONE_RE = re.compile(r"\b0[1-9][\s\-]?\d{7,8}\b|\b06[\s\-]?\d{8}\b")
URL_RE = re.compile(r"\bwww\.|\.nl\b|\.com\b|https?://", re.I)

# Min readable characters from OCR to treat as P0 text on vehicle.
OCR_ALNUM_FAIL = 8
TEXT_RISK_THRESHOLD = 0.52  # fallback only when OCR unavailable


@dataclass(frozen=True)
class MockupSafetyResult:
    ok: bool
    text_risk: float
    reasons: tuple[str, ...]
    ocr_text: str = ""


def _ocr_enabled() -> bool:
    raw = os.getenv("INSPIRE_MOCKUP_OCR", "auto").strip().lower()
    if raw in ("0", "false", "no", "off"):
        return False
    if raw in ("1", "true", "yes", "on"):
        return True
    return True  # auto: use when import works


@lru_cache(maxsize=1)
def _ocr_reader() -> "easyocr.Reader | None":
    if not _ocr_enabled():
        return None
    try:
        import easyocr

        return easyocr.Reader(["nl", "en"], gpu=False, verbose=False)
    except Exception as exc:
        logger.warning("easyocr unavailable, using edge fallback: %s", exc)
        return None


def _extract_ocr_text(png_bytes: bytes) -> str:
    reader = _ocr_reader()
    if reader is None:
        return ""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(png_bytes)
        path = tmp.name
    try:
        lines = reader.readtext(path, detail=0, paragraph=True)
        return " ".join(lines).strip()
    except Exception as exc:
        logger.warning("OCR read failed: %s", exc)
        return ""
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def estimate_text_risk(png_bytes: bytes) -> float:
    """Pillow edge-density fallback when OCR is unavailable."""
    img = Image.open(io.BytesIO(png_bytes)).convert("L")
    w, h = img.size
    crop = img.crop((int(w * 0.08), int(h * 0.22), int(w * 0.92), int(h * 0.82)))
    crop = ImageOps.autocontrast(crop)
    edges = crop.filter(ImageFilter.FIND_EDGES)
    pixels = list(edges.getdata())
    if not pixels:
        return 0.0
    hot = sum(1 for p in pixels if p > 48)
    ratio = hot / len(pixels)
    return min(1.0, ratio * 6.5)


def _scan_text(text: str) -> tuple[float, list[str]]:
    reasons: list[str] = []
    lowered = text.lower()
    alnum = sum(c.isalnum() for c in text)
    risk = min(1.0, alnum / 40.0) if alnum else 0.0

    if alnum >= OCR_ALNUM_FAIL:
        reasons.append("ocr_text_on_image")
        risk = max(risk, 0.85)
    for word in NL_BLOCKLIST:
        if word in lowered:
            reasons.append(f"blocklist:{word}")
            risk = 1.0
    if PHONE_RE.search(text):
        reasons.append("phone_pattern")
        risk = max(risk, 0.9)
    if URL_RE.search(text):
        reasons.append("url_pattern")
        risk = max(risk, 0.9)
    return risk, reasons


def check_mockup_safety(
    png_bytes: bytes,
    *,
    text_risk_threshold: float = TEXT_RISK_THRESHOLD,
) -> MockupSafetyResult:
    ocr_text = _extract_ocr_text(png_bytes)
    reasons: list[str] = []

    if ocr_text:
        risk, ocr_reasons = _scan_text(ocr_text)
        reasons.extend(ocr_reasons)
    else:
        risk = estimate_text_risk(png_bytes)
        if risk >= text_risk_threshold:
            reasons.append("likely_text_on_vehicle")

    return MockupSafetyResult(
        ok=len(reasons) == 0,
        text_risk=round(risk, 3),
        reasons=tuple(reasons),
        ocr_text=ocr_text[:200],
    )


def retry_negative_suffix() -> str:
    return (
        ", absolutely no typography, no letters, no numbers, no words, no business name text, "
        "no phone numbers, no URLs, abstract geometric brand graphics only, offensive Dutch words"
    )
