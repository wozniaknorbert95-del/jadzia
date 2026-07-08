"""Inspire engine — 2 fal full-frame mockups per session (tier B/A)."""

from __future__ import annotations

import base64
import logging
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import List, Literal

from agent.inspire.compose_ref import build_reference_png
from agent.inspire.fal_fullframe import generate_mockup_png
from agent.inspire.prompt import BriefContext, VariantId, build_prompt
from agent.inspire.reco import RecommendedProduct, build_wizard_deeplink, resolve_recommendations
from agent.inspire.tier_resolver import TierMeta, resolve_tier_skus

logger = logging.getLogger(__name__)

Positionering = Literal["strak", "opvallend", "balanced"]
VARIANTS: tuple[VariantId, ...] = ("tier_b", "tier_a")
EST_COST_EUR_PER_MOCKUP = 0.11


@dataclass
class MockupResult:
    variant: VariantId
    panel: str
    url: str
    sku: str = ""
    data_url: str | None = None
    degraded: bool = False


@dataclass
class InspireResponse:
    brief_id: str
    mockups: List[MockupResult]
    recommended_products: List[RecommendedProduct]
    wizard_deeplink: str
    cost_eur: float
    positionering: Positionering
    user_stijl: str  # legacy alias for positionering
    mockup_b_sku: str
    mockup_a_sku: str


def _save_mockup(
    png_bytes: bytes,
    output_dir: Path,
    brief_id: str,
    variant: str,
    public_base: str,
) -> tuple[str, str | None]:
    work = output_dir / brief_id
    work.mkdir(parents=True, exist_ok=True)
    name = f"mockup_{variant}.png"
    path = work / name
    path.write_bytes(png_bytes)
    if public_base:
        url = f"{public_base.rstrip('/')}/{brief_id}/{name}"
        return url, None
    b64 = base64.b64encode(png_bytes).decode("ascii")
    return "", f"data:image/png;base64,{b64}"


def _tier_for_variant(variant: VariantId, tier_b: TierMeta, tier_a: TierMeta) -> TierMeta:
    return tier_b if variant == "tier_b" else tier_a


def generate_inspire_mockups(
    *,
    vehicle: str,
    branche: str,
    bedrijfsnaam: str,
    telefoon: str,
    website: str,
    brand_colors: list[str],
    tekst_opties: list[str],
    slogan: str,
    stijl: Positionering | str = "balanced",
    positionering: Positionering | str | None = None,
    diensten: str = "",
    doelgroep: str = "",
    vehicle_use: str = "",
    branding_goal: str = "",
    mockup_b_sku: str = "",
    mockup_a_sku: str = "",
    logo_bytes: bytes,
    output_dir: Path,
    ssot_path: Path,
    public_base_url: str = "",
    tier_matrix_path: Path | None = None,
) -> InspireResponse:
    brief_id = str(uuid.uuid4())
    pos: Positionering
    raw_pos = positionering or stijl
    if raw_pos in ("strak", "opvallend", "balanced"):
        pos = raw_pos  # type: ignore[assignment]
    else:
        pos = "balanced"

    brief_dict = {
        "vehicle_use": vehicle_use,
        "branding_goal": branding_goal,
        "positionering": pos,
        "stijl": stijl if isinstance(stijl, str) else pos,
        "mockup_b_sku": mockup_b_sku or None,
        "mockup_a_sku": mockup_a_sku or None,
    }
    tier_b, tier_a = resolve_tier_skus(vehicle, brief_dict, matrix_path=tier_matrix_path)

    ctx = BriefContext(
        vehicle=vehicle,
        branche=branche,
        bedrijfsnaam=bedrijfsnaam,
        telefoon=telefoon,
        website=website,
        brand_colors=brand_colors,
        tekst_opties=tekst_opties,
        slogan=slogan,
        positionering=pos,
        diensten=diensten,
        doelgroep=doelgroep,
    )

    ref_png = build_reference_png(vehicle, logo_bytes, bedrijfsnaam, telefoon)
    mockups: List[MockupResult] = []

    for variant in VARIANTS:
        tier_meta = _tier_for_variant(variant, tier_b, tier_a)
        prompt, negative = build_prompt(ctx, variant, tier_meta)
        logger.info("inspire fal variant=%s sku=%s vehicle=%s", variant, tier_meta.sku, vehicle)
        png = generate_mockup_png(ref_png, prompt, negative)
        url, data_url = _save_mockup(png, output_dir, brief_id, variant, public_base_url)
        mockups.append(
            MockupResult(
                variant=variant,
                panel="deur",
                url=url,
                sku=tier_meta.sku,
                data_url=data_url,
                degraded=False,
            )
        )

    products = resolve_recommendations(tier_b.sku, tier_a.sku, ssot_path)
    deeplink = build_wizard_deeplink(vehicle, tier_b.sku)
    cost = EST_COST_EUR_PER_MOCKUP * len(mockups)

    return InspireResponse(
        brief_id=brief_id,
        mockups=mockups,
        recommended_products=products,
        wizard_deeplink=deeplink,
        cost_eur=cost,
        positionering=pos,
        user_stijl=pos,
        mockup_b_sku=tier_b.sku,
        mockup_a_sku=tier_a.sku,
    )
