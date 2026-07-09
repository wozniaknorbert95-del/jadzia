"""Creative Director — BrandStrategySpec → LayoutSpec × 2 (Brain3)."""

from __future__ import annotations

from typing import Any

from agent.inspire.brand_strategy_spec import BrandStrategySpec
from agent.inspire.brand_strategist import load_panel_map
from agent.inspire.layout_spec import ElementAnchor, ElementStyle, LayoutElement, LayoutPanel, LayoutSpec
from agent.inspire.prompt import VEHICLE_LABELS, _positionering_style
from agent.inspire.tier_resolver import TierMeta

VariantId = str


def _panel_bbox(vehicle: str, panel_id: str, panel_map: dict[str, Any]) -> ElementAnchor:
    panels = panel_map.get("panels", {}).get(vehicle, {})
    box = panels.get(panel_id, {"x_pct": 0.38, "y_pct": 0.32, "w_pct": 0.22, "h_pct": 0.28})
    return ElementAnchor(
        x_pct=float(box["x_pct"]),
        y_pct=float(box["y_pct"]),
        w_pct=float(box["w_pct"]),
        h_pct=float(box["h_pct"]),
    )


def _build_elements_for_panel(
    panel_id: str,
    vehicle: str,
    brief: dict[str, Any],
    strategy: BrandStrategySpec,
    panel_map: dict[str, Any],
    *,
    is_primary_panel: bool,
) -> list[LayoutElement]:
    elements: list[LayoutElement] = []
    anchor = _panel_bbox(vehicle, panel_id, panel_map)
    typo = strategy.typography
    primary_color = strategy.color_strategy.primary
    tekst_opties = brief.get("tekst_opties") or []

    if "logo" in strategy.message_hierarchy and is_primary_panel:
        elements.append(
            LayoutElement(
                type="logo",
                anchor=ElementAnchor(
                    x_pct=anchor.x_pct,
                    y_pct=anchor.y_pct,
                    w_pct=min(anchor.w_pct * 0.6, 0.18),
                    h_pct=min(anchor.h_pct * 0.45, 0.14),
                ),
            )
        )

    if "bedrijfsnaam" in strategy.message_hierarchy and is_primary_panel:
        elements.append(
            LayoutElement(
                type="bedrijfsnaam",
                anchor=ElementAnchor(
                    x_pct=anchor.x_pct,
                    y_pct=anchor.y_pct + anchor.h_pct * 0.45,
                    w_pct=anchor.w_pct,
                    h_pct=anchor.h_pct * 0.25,
                ),
                text_from_brief=True,
                style=ElementStyle(size_px=typo.naam_min_px, color=primary_color, weight=typo.naam_weight),
            )
        )

    if "telefoon" in strategy.message_hierarchy and "telefoon" in tekst_opties and brief.get("telefoon"):
        phone_panel = panel_id if panel_id in ("deur", "achter") else "deur"
        if panel_id == phone_panel or (panel_id == "achter" and strategy.positionering == "opvallend"):
            phone_anchor = _panel_bbox(vehicle, phone_panel, panel_map)
            elements.append(
                LayoutElement(
                    type="telefoon",
                    anchor=ElementAnchor(
                        x_pct=phone_anchor.x_pct,
                        y_pct=phone_anchor.y_pct + phone_anchor.h_pct * 0.72,
                        w_pct=phone_anchor.w_pct * 0.9,
                        h_pct=phone_anchor.h_pct * 0.2,
                    ),
                    text_from_brief=True,
                    style=ElementStyle(size_px=typo.phone_min_px, color=primary_color, weight="bold"),
                )
            )

    if "slogan" in strategy.message_hierarchy and "slogan" in tekst_opties and brief.get("slogan") and is_primary_panel:
        elements.append(
            LayoutElement(
                type="slogan",
                anchor=ElementAnchor(
                    x_pct=anchor.x_pct,
                    y_pct=anchor.y_pct + anchor.h_pct * 0.68,
                    w_pct=anchor.w_pct,
                    h_pct=anchor.h_pct * 0.18,
                ),
                text_from_brief=True,
                style=ElementStyle(size_px=typo.slogan_max_px, color=primary_color, weight="normal"),
            )
        )

    if "website" in strategy.message_hierarchy and "website" in tekst_opties and brief.get("website") and is_primary_panel:
        elements.append(
            LayoutElement(
                type="website",
                anchor=ElementAnchor(
                    x_pct=anchor.x_pct,
                    y_pct=anchor.y_pct + anchor.h_pct * 0.85,
                    w_pct=anchor.w_pct,
                    h_pct=anchor.h_pct * 0.12,
                ),
                text_from_brief=True,
                style=ElementStyle(size_px=typo.website_max_px, color=primary_color, weight="normal"),
            )
        )

    return elements


def _fal_background_prompt(
    *,
    vehicle: str,
    branche: str,
    diensten: str,
    doelgroep: str,
    positionering: str,
    brand_colors: list[str],
    tier_meta: TierMeta,
    variant: VariantId,
    strategy: BrandStrategySpec,
) -> tuple[str, str]:
    vehicle_label = VEHICLE_LABELS.get(vehicle, "commercial vehicle")
    colors = ", ".join(brand_colors) if brand_colors else "professional brand colors"
    style = _positionering_style(positionering)
    tier_code = "entry_coverage" if variant == "tier_b" else "premium_coverage"
    cluster_tone = strategy.branche_cluster.replace("_", " ")

    positive = (
        f"Photorealistic professional commercial vehicle wrap mockup, studio automotive photography, "
        f"glossy paint reflections, {vehicle_label}. "
        f"Industry context: {branche}. Services: {diensten}. Target clients: {doelgroep}. "
        f"Product tier: {tier_code}. Coverage: {tier_meta.coverage}. "
        f"Visual tone for {cluster_tone} trade in Netherlands. "
        f"Branding: vinyl color blocks and abstract brand shapes on body panels only. "
        f"Absolutely no typography, no letters, no numbers, no words on the vehicle. "
        f"Brand colors: {colors}. Style: {style}. "
        f"Side view 3/4 angle, realistic vinyl wrap, sharp focus, 8k commercial photo."
    )
    negative = (
        "cartoon, illustration, flat sticker, distorted wheels, typography, lettering, words, "
        "phone numbers, URLs, business name text, offensive Dutch words, moord, dood"
    )
    return positive, negative


def produce_layout_specs(
    *,
    vehicle: str,
    brief: dict[str, Any],
    strategy: BrandStrategySpec,
    tier_b: TierMeta,
    tier_a: TierMeta,
    panel_map: dict[str, Any] | None = None,
) -> tuple[LayoutSpec, LayoutSpec]:
    """Produce tier B and tier A LayoutSpec from strategy + brief."""
    pm = panel_map if panel_map is not None else load_panel_map()
    brand_colors = list(brief.get("brand_colors") or [])
    positionering = str(brief.get("positionering") or strategy.positionering)

    layouts: list[LayoutSpec] = []
    for variant, tier_meta, active_panels in (
        ("tier_b", tier_b, strategy.active_panels_b),
        ("tier_a", tier_a, strategy.active_panels_a),
    ):
        panels: list[LayoutPanel] = []
        for idx, panel_id in enumerate(active_panels):
            pid = panel_id if panel_id in ("deur", "zij", "achter", "kap") else "deur"
            elements = _build_elements_for_panel(
                pid,
                vehicle,
                brief,
                strategy,
                pm,
                is_primary_panel=(idx == 0),
            )
            panels.append(LayoutPanel(id=pid, elements=elements))  # type: ignore[arg-type]

        fal_pos, fal_neg = _fal_background_prompt(
            vehicle=vehicle,
            branche=str(brief.get("branche", "")),
            diensten=str(brief.get("diensten", "")),
            doelgroep=str(brief.get("doelgroep", "")),
            positionering=positionering,
            brand_colors=brand_colors,
            tier_meta=tier_meta,
            variant=variant,
            strategy=strategy,
        )
        layouts.append(
            LayoutSpec(
                variant=variant,  # type: ignore[arg-type]
                sku=tier_meta.sku,
                panels=panels,
                fal_background_prompt=fal_pos,
                fal_negative_prompt=fal_neg,
                compliance_checks=["hierarchy_ok", "phone_if_opted", "tier_coverage"],
            )
        )

    return layouts[0], layouts[1]
