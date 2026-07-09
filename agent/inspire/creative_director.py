"""Creative Director — BrandStrategySpec → LayoutSpec × 2 (Brain3)."""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Callable

import httpx
from pydantic import ValidationError

from agent.inspire.brand_strategy_spec import BrandStrategySpec
from agent.inspire.brand_strategist import load_panel_map
from agent.inspire.creative_director_prompts import CREATIVE_DIRECTOR_SYSTEM
from agent.inspire.layout_spec import ElementAnchor, ElementStyle, LayoutElement, LayoutPanel, LayoutSpec, VinylZone
from agent.inspire.prompt import VEHICLE_LABELS, _positionering_style
from agent.inspire.tier_resolver import TierMeta

logger = logging.getLogger(__name__)

VariantId = str

_LLM_CALLABLE: Callable[[list[dict[str, str]]], dict[str, Any]] | None = None


def set_creative_director_llm(fn: Callable[[list[dict[str, str]]], dict[str, Any]] | None) -> None:
    """Test hook — inject mock LLM responses."""
    global _LLM_CALLABLE
    _LLM_CALLABLE = fn


def _llm_enabled() -> bool:
    raw = os.getenv("INSPIRE_CD_LLM", "1").strip().lower()
    if raw in ("0", "false", "no", "off"):
        return False
    return bool(os.getenv("OPENROUTER_API_KEY", "").strip()) or _LLM_CALLABLE is not None


def _default_openrouter_call(messages: list[dict[str, str]]) -> dict[str, Any]:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY ontbreekt")
    model = os.getenv("DA_CD_MODEL", os.getenv("DA_CHAT_MODEL", "openai/gpt-4o-mini"))
    payload = {
        "model": model,
        "messages": messages,
        "response_format": {"type": "json_object"},
        "temperature": 0.35,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    with httpx.Client(timeout=90.0) as client:
        resp = client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return json.loads(content)


def _call_llm(messages: list[dict[str, str]]) -> dict[str, Any]:
    if _LLM_CALLABLE is not None:
        return _LLM_CALLABLE(messages)
    return _default_openrouter_call(messages)


def _fal_prompt_safe(text: str, brief: dict[str, Any]) -> bool:
    """Reject fal prompts that embed client-readable strings."""
    lowered = text.lower()
    for key in ("bedrijfsnaam", "telefoon", "website", "slogan"):
        val = str(brief.get(key, "")).strip()
        if val and len(val) >= 4 and val.lower() in lowered:
            return False
    if not re.search(r"no (typography|letters|words|readable text)", lowered):
        return False
    return True


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


def _zone_count(positionering: str, variant: VariantId) -> int:
    base = {"strak": 1, "balanced": 2, "opvallend": 3}.get(positionering, 2)
    if variant == "tier_a":
        base += 1
    return min(max(base, 1), 4)


def _build_vinyl_zones(
    *,
    vehicle: str,
    active_panels: list[str],
    panel_map: dict[str, Any],
    strategy: BrandStrategySpec,
    variant: VariantId,
    positionering: str,
    brand_colors: list[str],
) -> list[VinylZone]:
    count = _zone_count(positionering, variant)
    primary = strategy.color_strategy.primary
    accent = brand_colors[1] if len(brand_colors) > 1 else primary
    opacity = 0.45 if positionering == "strak" else 0.6 if positionering == "opvallend" else 0.55
    zones: list[VinylZone] = []
    for idx, panel_id in enumerate(active_panels[:count]):
        pid = panel_id if panel_id in ("deur", "zij", "achter", "kap") else "deur"
        bbox = _panel_bbox(vehicle, pid, panel_map)
        height_scale = 0.9 if idx == 0 else 0.7
        zones.append(
            VinylZone(
                panel_id=pid,  # type: ignore[arg-type]
                anchor=ElementAnchor(
                    x_pct=bbox.x_pct,
                    y_pct=bbox.y_pct,
                    w_pct=bbox.w_pct,
                    h_pct=bbox.h_pct * height_scale,
                ),
                fill_hex=primary if idx == 0 else accent,
                opacity=opacity,
            )
        )
    return zones


def _finalize_layout(
    layout: LayoutSpec,
    *,
    vehicle: str,
    active_panels: list[str],
    panel_map: dict[str, Any],
    strategy: BrandStrategySpec,
    positionering: str,
    brand_colors: list[str],
) -> LayoutSpec:
    if layout.vinyl_zones:
        return layout
    zones = _build_vinyl_zones(
        vehicle=vehicle,
        active_panels=active_panels,
        panel_map=panel_map,
        strategy=strategy,
        variant=layout.variant,
        positionering=positionering,
        brand_colors=brand_colors,
    )
    return layout.model_copy(update={"vinyl_zones": zones})


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
        f"Preserve and enhance the semi-transparent vinyl color zones in the reference image on body panels. "
        f"Branding: vinyl color blocks and abstract brand shapes aligned with reference zones only. "
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
    """Produce tier B and tier A LayoutSpec — LLM when enabled, else rules."""
    pm = panel_map if panel_map is not None else load_panel_map()
    if _llm_enabled():
        llm_result = _produce_layout_specs_llm(
            vehicle=vehicle,
            brief=brief,
            strategy=strategy,
            tier_b=tier_b,
            tier_a=tier_a,
            panel_map=pm,
        )
        if llm_result is not None:
            return llm_result
    return _produce_layout_specs_rules(
        vehicle=vehicle,
        brief=brief,
        strategy=strategy,
        tier_b=tier_b,
        tier_a=tier_a,
        panel_map=pm,
    )


def _build_llm_messages(
    *,
    vehicle: str,
    brief: dict[str, Any],
    strategy: BrandStrategySpec,
    tier_b: TierMeta,
    tier_a: TierMeta,
    panel_map: dict[str, Any],
) -> list[dict[str, str]]:
    payload = {
        "vehicle": vehicle,
        "brief": brief,
        "strategy": strategy.model_dump(),
        "tier_b": {"sku": tier_b.sku, "coverage": tier_b.coverage, "panels": strategy.active_panels_b},
        "tier_a": {"sku": tier_a.sku, "coverage": tier_a.coverage, "panels": strategy.active_panels_a},
        "panel_bboxes": panel_map.get("panels", {}).get(vehicle, {}),
        "output_schema": {
            "tier_b": "LayoutSpec JSON",
            "tier_a": "LayoutSpec JSON",
            "fields": [
                "variant",
                "sku",
                "panels[{id, elements[{type, anchor{x_pct,y_pct,w_pct,h_pct}, style?}]}]",
                "vinyl_zones[{panel_id, anchor, fill_hex, opacity}]",
                "fal_background_prompt",
                "fal_negative_prompt",
                "compliance_checks",
            ],
        },
    }
    return [
        {"role": "system", "content": CREATIVE_DIRECTOR_SYSTEM},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


def _coerce_layout(raw: dict[str, Any], *, variant: VariantId, tier_meta: TierMeta, brief: dict[str, Any]) -> LayoutSpec:
    data = dict(raw)
    data["variant"] = variant
    data["sku"] = tier_meta.sku
    if not data.get("fal_negative_prompt"):
        data["fal_negative_prompt"] = (
            "cartoon, illustration, typography, lettering, words, phone numbers, URLs, business name text"
        )
    layout = LayoutSpec.model_validate(data)
    if not _fal_prompt_safe(layout.fal_background_prompt, brief):
        raise ValueError(f"fal prompt unsafe for variant={variant}")
    return layout


def _produce_layout_specs_llm(
    *,
    vehicle: str,
    brief: dict[str, Any],
    strategy: BrandStrategySpec,
    tier_b: TierMeta,
    tier_a: TierMeta,
    panel_map: dict[str, Any],
) -> tuple[LayoutSpec, LayoutSpec] | None:
    try:
        messages = _build_llm_messages(
            vehicle=vehicle,
            brief=brief,
            strategy=strategy,
            tier_b=tier_b,
            tier_a=tier_a,
            panel_map=panel_map,
        )
        data = _call_llm(messages)
        raw_b = data.get("tier_b") or (data.get("layouts") or [{}])[0]
        raw_a = data.get("tier_a") or (data.get("layouts") or [{}, {}])[1]
        layout_b = _coerce_layout(raw_b, variant="tier_b", tier_meta=tier_b, brief=brief)
        layout_a = _coerce_layout(raw_a, variant="tier_a", tier_meta=tier_a, brief=brief)
        _assert_layout_hierarchy(layout_b)
        _assert_layout_hierarchy(layout_a)
        if len(layout_a.panels) < len(layout_b.panels):
            raise ValueError("tier_a must have >= panels than tier_b")
        pos = str(brief.get("positionering") or strategy.positionering)
        colors = list(brief.get("brand_colors") or [])
        layout_b = _finalize_layout(
            layout_b,
            vehicle=vehicle,
            active_panels=strategy.active_panels_b,
            panel_map=panel_map,
            strategy=strategy,
            positionering=pos,
            brand_colors=colors,
        )
        layout_a = _finalize_layout(
            layout_a,
            vehicle=vehicle,
            active_panels=strategy.active_panels_a,
            panel_map=panel_map,
            strategy=strategy,
            positionering=pos,
            brand_colors=colors,
        )
        return layout_b, layout_a
    except (ValidationError, ValueError, KeyError, IndexError, httpx.HTTPError, RuntimeError) as exc:
        logger.warning("creative director LLM fallback to rules: %s", exc)
        return None


def _assert_layout_hierarchy(layout: LayoutSpec) -> None:
    types = [el.type for panel in layout.panels for el in panel.elements]
    if "logo" not in types or "bedrijfsnaam" not in types:
        raise ValueError(f"missing hierarchy on {layout.variant}")


def _produce_layout_specs_rules(
    *,
    vehicle: str,
    brief: dict[str, Any],
    strategy: BrandStrategySpec,
    tier_b: TierMeta,
    tier_a: TierMeta,
    panel_map: dict[str, Any],
) -> tuple[LayoutSpec, LayoutSpec]:
    """Rule-engine LayoutSpec (fallback path)."""
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
                panel_map,
                is_primary_panel=(idx == 0),
            )
            panels.append(LayoutPanel(id=pid, elements=elements))  # type: ignore[arg-type]

        vinyl_zones = _build_vinyl_zones(
            vehicle=vehicle,
            active_panels=active_panels,
            panel_map=panel_map,
            strategy=strategy,
            variant=variant,  # type: ignore[arg-type]
            positionering=positionering,
            brand_colors=brand_colors,
        )

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
                vinyl_zones=vinyl_zones,
                fal_background_prompt=fal_pos,
                fal_negative_prompt=fal_neg,
                compliance_checks=["hierarchy_ok", "phone_if_opted", "tier_coverage"],
            )
        )

    return layouts[0], layouts[1]
