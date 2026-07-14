"""Inspire engine — INSPIRE v4 inspiration mockups (inspirationOnly default; fal legacy disabled)."""

from __future__ import annotations

import base64
import logging
import os
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import List, Literal

from agent.inspire.brand_strategist import load_playbook, produce_brand_strategy
from agent.inspire.compose_ref import build_reference_png
from agent.inspire.creative_director import produce_layout_specs
from agent.inspire.fal_fullframe import generate_mockup_png
from agent.inspire.layout_spec import LayoutSpec
from agent.inspire.marketing_compliance import assert_layout_compliance
from agent.inspire.mockup_safety import check_mockup_safety, retry_negative_suffix
from agent.inspire.overlay_renderer import apply_overlay
from agent.inspire.prompt import BriefContext, VariantId, build_prompt
from agent.inspire.reco import RecommendedProduct, build_wizard_deeplink, resolve_recommendations
from agent.inspire.tier_resolver import TierMeta, resolve_tier_skus

logger = logging.getLogger(__name__)

Positionering = Literal["strak", "opvallend", "balanced"]
VARIANTS: tuple[VariantId, ...] = ("tier_b", "tier_a")
EST_COST_EUR_PER_MOCKUP = 0.11
EST_COST_EUR_STRATEGIST = 0.01


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
    user_stijl: str
    mockup_b_sku: str
    mockup_a_sku: str
    engine_mode: str = "enterprise"
    generator_provider: str = ""


def _enterprise_enabled() -> bool:
    if _inspiration_enabled():
        return False
    raw = os.getenv("INSPIRE_ENTERPRISE", "0").strip().lower()
    return raw in ("1", "true", "yes", "on")


def _inspiration_enabled() -> bool:
    raw = os.getenv("INSPIRE_RENDER_MODE", "inspirationOnly").strip().lower()
    if raw in ("controlled", "pil"):
        return True
    return raw in (
        "oneshot",
        "sales",
        "v3",
        "inspirationonly",
        "inspiration_only",
        "v4",
        "",
    )


def _try_inspiration_generate(**kwargs) -> InspireResponse | None:
    if not _inspiration_enabled():
        return None
    repo = _inspire_repo_path()
    if not repo.is_dir():
        logger.warning("inspiration mode but INSPIRE_REPO_PATH missing: %s", repo)
        return None
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    os.environ.setdefault("DA_TIER_MATRIX_PATH", str(repo / "brain" / "tier-matrix.json"))
    try:
        from engine.v4.intake.legacy_brief_adapter import legacy_brief_to_v4
        from engine.v4.pipeline import generate_inspiration_mockups

        brief_dict = {
            "vehicle": kwargs.get("vehicle", "caddy"),
            "branche": kwargs.get("branche", ""),
            "bedrijfsnaam": kwargs.get("bedrijfsnaam", ""),
            "telefoon": kwargs.get("telefoon", ""),
            "website": kwargs.get("website", ""),
            "brand_colors": kwargs.get("brand_colors", []),
            "tekst_opties": kwargs.get("tekst_opties", []),
            "slogan": kwargs.get("slogan", ""),
            "positionering": kwargs.get("positionering") or kwargs.get("stijl", "balanced"),
            "diensten": kwargs.get("diensten", ""),
            "doelgroep": kwargs.get("doelgroep", ""),
            "regio": kwargs.get("regio", ""),
            "vehicle_usage": kwargs.get("vehicle_use") or kwargs.get("vehicle_usage", "zakelijk"),
            "desired_impression": kwargs.get("desired_impression")
            or kwargs.get("positionering")
            or kwargs.get("stijl", "balanced"),
            "budget_range": kwargs.get("budget_range", ""),
            "brief_confirmed": True,
            "mockup_goal_acknowledged": True,
        }
        if kwargs.get("logo_bytes"):
            brief_dict["logo_status"] = "uploaded_png"
        design_brief = legacy_brief_to_v4(brief_dict)
        design_brief.consent.brief_confirmed = True
        raw = generate_inspiration_mockups(
            design_brief,
            logo_bytes=kwargs.get("logo_bytes"),
            output_dir=kwargs.get("output_dir"),
            public_base_url=kwargs.get("public_base_url", ""),
            ssot_path=kwargs.get("ssot_path"),
        )
        mockups = [
            MockupResult(
                variant="tier_b" if m.variant == "standard" else "tier_a",
                panel=m.panel,
                url=m.url,
                sku=m.sku,
                data_url=m.data_url,
                degraded=False,
            )
            for m in (raw.standard, raw.premium)
        ]
        return InspireResponse(
            brief_id=raw.brief_id,
            mockups=mockups,
            recommended_products=raw.recommended_products,
            wizard_deeplink=raw.wizard_deeplink,
            cost_eur=raw.cost_eur,
            positionering=kwargs.get("positionering") or kwargs.get("stijl", "balanced"),
            user_stijl=kwargs.get("stijl", "balanced"),
            mockup_b_sku=raw.mockup_b_sku,
            mockup_a_sku=raw.mockup_a_sku,
            engine_mode=raw.engine_mode,
            generator_provider=os.getenv("INSPIRE_GENERATOR_PROVIDER", "stub").strip().lower(),
        )
    except Exception as exc:
        if _inspiration_enabled():
            logger.error("inspiration engine failed (strict, no fal fallback): %s", exc)
            raise ValueError(f"Inspiration generation failed: {exc}") from exc
        logger.warning("inspiration engine failed, fallback: %s", exc)
        return None


def _inspire_repo_path() -> Path:
    env = os.getenv("INSPIRE_REPO_PATH", "").strip()
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[3].parent / "flexgrafik-inspire"


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


def _legacy_generate_variant(
    *,
    variant: VariantId,
    ctx: BriefContext,
    tier_meta: TierMeta,
    ref_png: bytes,
) -> bytes:
    prompt, negative = build_prompt(ctx, variant, tier_meta)
    png = generate_mockup_png(ref_png, prompt, negative)
    safety = check_mockup_safety(png)
    if not safety.ok:
        logger.warning("legacy OCR fail variant=%s reasons=%s retry", variant, safety.reasons)
        png = generate_mockup_png(ref_png, prompt, negative + retry_negative_suffix())
    return png


def _enterprise_generate_variant(
    *,
    layout: LayoutSpec,
    vehicle: str,
    logo_bytes: bytes,
    brief_dict: dict,
    playbook: dict,
    strategy,
) -> bytes:
    assert_layout_compliance(layout, strategy, brief_dict, playbook)
    ref_png = build_reference_png(vehicle, logo_bytes, layout=layout)
    bg = generate_mockup_png(ref_png, layout.fal_background_prompt, layout.fal_negative_prompt)
    safety = check_mockup_safety(bg)
    if not safety.ok:
        logger.warning("enterprise OCR fail variant=%s reasons=%s retry", layout.variant, safety.reasons)
        bg = generate_mockup_png(
            ref_png,
            layout.fal_background_prompt,
            layout.fal_negative_prompt + retry_negative_suffix(),
        )
    return apply_overlay(bg, layout, logo_bytes, brief_dict)


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
    regio: str = "",
    desired_impression: str = "",
    budget_range: str = "",
    branding_goal: str = "",
    mockup_b_sku: str = "",
    mockup_a_sku: str = "",
    logo_bytes: bytes,
    output_dir: Path,
    ssot_path: Path,
    public_base_url: str = "",
    tier_matrix_path: Path | None = None,
) -> InspireResponse:
    oneshot_kwargs = dict(
        vehicle=vehicle,
        branche=branche,
        bedrijfsnaam=bedrijfsnaam,
        telefoon=telefoon,
        website=website,
        brand_colors=brand_colors,
        tekst_opties=tekst_opties,
        slogan=slogan,
        stijl=stijl,
        positionering=positionering,
        diensten=diensten,
        doelgroep=doelgroep,
        vehicle_use=vehicle_use or "zakelijk",
        regio=regio,
        desired_impression=desired_impression or (positionering or stijl or "balanced"),
        budget_range=budget_range or "",
        mockup_b_sku=mockup_b_sku,
        mockup_a_sku=mockup_a_sku,
        logo_bytes=logo_bytes,
        output_dir=output_dir,
        ssot_path=ssot_path,
        public_base_url=public_base_url,
        tier_matrix_path=tier_matrix_path,
    )
    inspiration = _try_inspiration_generate(**oneshot_kwargs)
    if inspiration is not None:
        return inspiration

    if _inspiration_enabled():
        raise ValueError(
            "Inspiration pipeline unavailable — fal fallback disabled in inspirationOnly mode."
        )

    brief_id = str(uuid.uuid4())
    raw_pos = positionering or stijl
    if raw_pos in ("strak", "opvallend", "balanced"):
        pos: Positionering = raw_pos  # type: ignore[assignment]
    else:
        pos = "balanced"

    brief_dict: dict = {
        "vehicle": vehicle,
        "branche": branche,
        "bedrijfsnaam": bedrijfsnaam,
        "telefoon": telefoon,
        "website": website,
        "brand_colors": brand_colors,
        "tekst_opties": tekst_opties,
        "slogan": slogan,
        "positionering": pos,
        "diensten": diensten,
        "doelgroep": doelgroep,
        "vehicle_use": vehicle_use,
        "branding_goal": branding_goal,
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

    mockups: List[MockupResult] = []
    engine_mode = "legacy"
    cost = 0.0

    use_enterprise = _enterprise_enabled()
    playbook = None
    strategy = None
    layouts: dict[VariantId, LayoutSpec] = {}

    if use_enterprise:
        try:
            playbook = load_playbook()
            strategy = produce_brand_strategy(
                branche=branche,
                diensten=diensten,
                doelgroep=doelgroep,
                positionering=pos,
                brand_colors=brand_colors,
                tier_b=tier_b,
                tier_a=tier_a,
            )
            layout_b, layout_a = produce_layout_specs(
                vehicle=vehicle,
                brief=brief_dict,
                strategy=strategy,
                tier_b=tier_b,
                tier_a=tier_a,
            )
            layouts = {"tier_b": layout_b, "tier_a": layout_a}
            engine_mode = "enterprise"
            cost += EST_COST_EUR_STRATEGIST
        except Exception as exc:
            logger.warning("enterprise pipeline fallback to legacy: %s", exc)
            use_enterprise = False

    ref_png_legacy = build_reference_png(vehicle, logo_bytes, bedrijfsnaam, telefoon)

    for variant in VARIANTS:
        tier_meta = _tier_for_variant(variant, tier_b, tier_a)
        primary_panel = layouts[variant].panels[0].id if variant in layouts and layouts[variant].panels else "deur"

        if use_enterprise and variant in layouts and playbook and strategy:
            png = _enterprise_generate_variant(
                layout=layouts[variant],
                vehicle=vehicle,
                logo_bytes=logo_bytes,
                brief_dict=brief_dict,
                playbook=playbook,
                strategy=strategy,
            )
        else:
            png = _legacy_generate_variant(
                variant=variant,
                ctx=ctx,
                tier_meta=tier_meta,
                ref_png=ref_png_legacy,
            )

        url, data_url = _save_mockup(png, output_dir, brief_id, variant, public_base_url)
        mockups.append(
            MockupResult(
                variant=variant,
                panel=primary_panel,
                url=url,
                sku=tier_meta.sku,
                data_url=data_url,
                degraded=False,
            )
        )
        cost += EST_COST_EUR_PER_MOCKUP

    products = resolve_recommendations(tier_b.sku, tier_a.sku, ssot_path)
    deeplink = build_wizard_deeplink(vehicle, tier_b.sku)

    return InspireResponse(
        brief_id=brief_id,
        mockups=mockups,
        recommended_products=products,
        wizard_deeplink=deeplink,
        cost_eur=round(cost, 2),
        positionering=pos,
        user_stijl=pos,
        mockup_b_sku=tier_b.sku,
        mockup_a_sku=tier_a.sku,
        engine_mode=engine_mode,
    )
