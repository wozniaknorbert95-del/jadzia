"""Product recommendations from tier SKUs + ZZPackage SSoT."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class RecommendedProduct:
    sku: str
    naam: str
    price_suggested: float
    highlight: bool = False


def _load_ssot(ssot_path: Path) -> list[dict]:
    if not ssot_path.is_file():
        logger.warning("SSoT not found: %s", ssot_path)
        return []
    return json.loads(ssot_path.read_text(encoding="utf-8"))


def _product(rows: list[dict], sku: str, highlight: bool = False) -> Optional[RecommendedProduct]:
    for row in rows:
        if row.get("sku") == sku:
            return RecommendedProduct(
                sku=sku,
                naam=str(row.get("naam", sku)),
                price_suggested=float(row.get("price_suggested", 0)),
                highlight=highlight,
            )
    return None


def resolve_recommendations(
    b_sku: str,
    a_sku: str,
    ssot_path: Path,
) -> List[RecommendedProduct]:
    rows = _load_ssot(ssot_path)
    skus: list[tuple[str, bool]] = [
        (b_sku, True),
        (a_sku, True),
        ("DF-004", False),
    ]
    out: List[RecommendedProduct] = []
    seen: set[str] = set()
    for sku, hl in skus:
        if sku in seen:
            continue
        seen.add(sku)
        p = _product(rows, sku, highlight=hl)
        if p:
            out.append(p)
    return out


def build_wizard_deeplink(vehicle: str, highlight_sku: str) -> str:
    return f"https://zzpackage.flexgrafik.nl/wizard/?voertuig={vehicle}&highlight={highlight_sku}"
