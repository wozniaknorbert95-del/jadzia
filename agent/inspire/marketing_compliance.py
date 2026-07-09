"""Marketing compliance checks vs NL ZZP playbook."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent.inspire.brand_strategy_spec import BrandStrategySpec
from agent.inspire.layout_spec import LayoutSpec


@dataclass(frozen=True)
class ComplianceResult:
    ok: bool
    reasons: tuple[str, ...]


def _element_types(layout: LayoutSpec) -> list[str]:
    types: list[str] = []
    for panel in layout.panels:
        for el in panel.elements:
            types.append(el.type)
    return types


def check_layout_compliance(
    layout: LayoutSpec,
    strategy: BrandStrategySpec,
    brief: dict[str, Any],
    playbook: dict[str, Any],
) -> ComplianceResult:
    reasons: list[str] = []
    types = _element_types(layout)
    hierarchy = strategy.message_hierarchy

    if "logo" in hierarchy and "logo" not in types:
        reasons.append("missing_logo")
    if "bedrijfsnaam" in hierarchy and "bedrijfsnaam" not in types:
        reasons.append("missing_bedrijfsnaam")

    tekst_opties = brief.get("tekst_opties") or []
    if "telefoon" in tekst_opties and brief.get("telefoon") and "telefoon" not in types:
        reasons.append("phone_if_opted_missing")

    if layout.variant == "tier_b" and len(layout.panels) > len(strategy.active_panels_b) + 1:
        reasons.append("tier_b_too_many_panels")
    if layout.variant == "tier_a" and len(layout.panels) < max(1, len(strategy.active_panels_b)):
        reasons.append("tier_a_not_greater_than_b")

    typo = playbook.get("typography_defaults", {})
    phone_min = int(typo.get("phone_min_px", 28))
    naam_min = int(typo.get("naam_min_px", 36))
    slogan_min = int(typo.get("slogan_max_px", 24)) - 4  # allow slogan at max-4
    website_min = int(typo.get("website_max_px", 20)) - 4
    min_by_type = {
        "bedrijfsnaam": naam_min - 4,
        "telefoon": phone_min - 4,
        "slogan": max(16, slogan_min),
        "website": max(14, website_min),
    }
    for panel in layout.panels:
        for el in panel.elements:
            if el.type in min_by_type:
                min_px = min_by_type[el.type]
                if el.style.size_px < min_px:
                    reasons.append(f"font_too_small:{el.type}")

    return ComplianceResult(ok=len(reasons) == 0, reasons=tuple(reasons))


def assert_layout_compliance(
    layout: LayoutSpec,
    strategy: BrandStrategySpec,
    brief: dict[str, Any],
    playbook: dict[str, Any],
) -> None:
    result = check_layout_compliance(layout, strategy, brief, playbook)
    if not result.ok:
        raise ValueError(f"marketing compliance failed: {', '.join(result.reasons)}")
