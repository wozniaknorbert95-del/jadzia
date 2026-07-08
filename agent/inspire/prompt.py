"""Build fal prompts from Design Agent brief (sales inspiration, NL context)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from agent.inspire.tier_resolver import TierMeta

Positionering = Literal["strak", "opvallend", "balanced"]
VariantId = Literal["tier_b", "tier_a"]

VEHICLE_LABELS = {
    "caddy": "white VW Caddy compact commercial van",
    "bus_l": "white medium commercial van (Vito / Transporter size)",
    "bus_xl": "white large commercial van (Sprinter / Crafter size)",
    "passenger": "white passenger car or kombi",
}


@dataclass(frozen=True)
class BriefContext:
    vehicle: str
    branche: str
    bedrijfsnaam: str
    telefoon: str
    website: str
    brand_colors: list[str]
    tekst_opties: list[str]
    slogan: str
    positionering: Positionering = "balanced"
    diensten: str = ""
    doelgroep: str = ""


def _text_lines(ctx: BriefContext) -> str:
    parts: list[str] = [ctx.bedrijfsnaam]
    if "telefoon" in ctx.tekst_opties and ctx.telefoon:
        parts.append(ctx.telefoon)
    if "website" in ctx.tekst_opties and ctx.website:
        parts.append(ctx.website)
    if "slogan" in ctx.tekst_opties and ctx.slogan:
        parts.append(ctx.slogan)
    return ", ".join(parts)


def _positionering_style(positionering: str) -> str:
    if positionering == "strak":
        return (
            "restrained professional typography, corporate and trustworthy, "
            "subtle color blocks, modern sans-serif lettering"
        )
    if positionering == "opvallend":
        return (
            "bold high-contrast graphics, strong color blocks, dynamic layout, "
            "maximum visibility on the road"
        )
    return "balanced professional branding, clear readable contact details, modern trade look"


def build_prompt(
    ctx: BriefContext,
    variant: VariantId,
    tier_meta: TierMeta,
) -> tuple[str, str]:
    """Return (positive, negative) prompts for fal kontext."""
    vehicle = VEHICLE_LABELS.get(ctx.vehicle, "commercial vehicle")
    colors = ", ".join(ctx.brand_colors) if ctx.brand_colors else "professional brand colors"
    branche = ctx.branche or "local business"
    tier_label = "Smart Start" if variant == "tier_b" else "Premium Presence"
    coverage = tier_meta.coverage
    style = _positionering_style(ctx.positionering)

    positive = (
        f"Photorealistic professional commercial vehicle wrap mockup, studio automotive photography, "
        f"glossy paint reflections, Netherlands {branche} company branding on a {vehicle}. "
        f"Product tier: {tier_label}. Vehicle coverage: {coverage}. "
        f"{'Minimal door-panel branding only, small logo zone.' if variant == 'tier_b' else 'Full side wrap with large color blocks across multiple panels.'} "
        f"Company branding: logo and brand color blocks only on the vehicle body. "
        f"No phone numbers, no URLs, no slogans, no readable words except abstract logo shapes. "
        f"Brand colors: {colors}. Visual style: {style}. "
        f"Side view 3/4 angle, realistic vinyl wrap on body panels, sharp focus, 8k commercial photo."
    )
    negative = (
        "cartoon, illustration, flat sticker, distorted wheels, deformed vehicle, "
        "wrong perspective, blurry text, watermark, low quality, duplicate vehicle, "
        "misspelled words, gibberish letters, random characters on vehicle, "
        "phone numbers on doors, website URLs on body, offensive Dutch words"
    )
    return positive, negative
