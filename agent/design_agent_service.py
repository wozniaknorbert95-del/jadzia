"""Design Agent REST handler — INSPIRE v4 inspirationOnly (legacy VGE optional)."""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path

from fastapi import HTTPException, UploadFile

from core.models import (
    DesignAgentGenerateResponse,
    DesignAgentMockupItem,
    DesignAgentProductItem,
)

logger = logging.getLogger(__name__)

_RATE: dict[str, list[float]] = {}
_RATE_LIMIT = 2
_RATE_WINDOW_SEC = 3600

_GENERATE_REQUIRED = (
    "bedrijfsnaam",
    "branche",
    "diensten",
    "doelgroep",
    "vehicle",
)

_ALLOWED_LOGO_MIMES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/svg+xml",
    "application/pdf",
}
_ALLOWED_LOGO_EXT = {".png", ".jpg", ".jpeg", ".svg", ".pdf"}

TIER_LABELS = {
    "tier_b": "Standard — Slim zichtbaar starten",
    "tier_a": "Premium — Maximale merkuitstraling",
    "standard": "Standard — Slim zichtbaar starten",
    "premium": "Premium — Maximale merkuitstraling",
}


def _client_variant(variant: str) -> str:
    if variant in ("tier_b", "standard"):
        return "standard"
    if variant in ("tier_a", "premium"):
        return "premium"
    return variant


def _resolve_engine_meta(result: object) -> tuple[str, str]:
    engine_mode = getattr(result, "engine_mode", None) or os.getenv(
        "INSPIRE_RENDER_MODE", "inspirationOnly"
    )
    provider = getattr(result, "generator_provider", None) or os.getenv(
        "INSPIRE_GENERATOR_PROVIDER", "stub"
    )
    return str(engine_mode).strip(), str(provider).strip().lower()


def _engine_mode() -> str:
    return os.getenv("DESIGN_AGENT_ENGINE", "inspire").strip().lower()


def _api_error(status: int, error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status,
        detail={"error_code": error_code, "message": message},
    )


def _validate_logo_upload(logo: UploadFile, logo_bytes: bytes) -> None:
    filename = (logo.filename or "").lower()
    ext = Path(filename).suffix
    if ext and ext not in _ALLOWED_LOGO_EXT:
        raise _api_error(400, "LOGO_INVALID", "Logo moet PNG, JPG, SVG of PDF zijn.")
    content_type = (logo.content_type or "").split(";")[0].strip().lower()
    if content_type and content_type not in _ALLOWED_LOGO_MIMES:
        raise _api_error(400, "LOGO_INVALID", "Logo moet PNG, JPG, SVG of PDF zijn.")
    if len(logo_bytes) < 32:
        raise _api_error(400, "LOGO_INVALID", "Logo-bestand is te klein of beschadigd.")


def _validate_generate_brief(
    *,
    bedrijfsnaam: str,
    branche: str,
    diensten: str,
    doelgroep: str,
    vehicle: str,
) -> None:
    missing: list[str] = []
    if not bedrijfsnaam.strip():
        missing.append("bedrijfsnaam")
    if not branche.strip():
        missing.append("branche")
    if not diensten.strip():
        missing.append("diensten")
    if not doelgroep.strip():
        missing.append("doelgroep")
    if not vehicle.strip():
        missing.append("vehicle")
    if missing:
        raise _api_error(
            400,
            "BRIEF_INCOMPLETE",
            f"Briefing incompleet — ontbrekend: {', '.join(missing)}.",
        )


def _log_generation_cost(brief_id: str, vehicle: str, cost_eur: float) -> None:
    logger.info(
        "design-agent cost brief_id=%s vehicle=%s cost_eur=%.4f engine=%s",
        brief_id,
        vehicle,
        cost_eur,
        _engine_mode(),
    )
    if cost_eur > 0.50:
        logger.warning(
            "Z05 cost cap exceeded brief_id=%s cost_eur=%.4f (log only, no block)",
            brief_id,
            cost_eur,
        )


def _check_rate_limit(client_ip: str, session_id: str | None = None) -> None:
    now = time.time()
    bucket = f"session:{session_id.strip()}" if session_id and session_id.strip() else f"ip:{client_ip}"
    hits = _RATE.get(bucket, [])
    hits = [t for t in hits if now - t < _RATE_WINDOW_SEC]
    if len(hits) >= _RATE_LIMIT:
        raise _api_error(
            429,
            "RATE_LIMIT",
            "Te veel verzoeken. Probeer het over een uur opnieuw.",
        )
    hits.append(now)
    _RATE[bucket] = hits


def _ensure_vge_import() -> None:
    vge_root = os.getenv("VGE_ROOT", "")
    if vge_root and vge_root not in sys.path:
        sys.path.insert(0, vge_root)
    try:
        from vge.models.design_agent_brief import DesignAgentBrief  # noqa: F401
        from vge.services.design_agent import generate_design_agent_mockups  # noqa: F401
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail="Design Agent engine niet beschikbaar (VGE_ROOT ontbreekt op server).",
        ) from exc


def _verify_api_key(header_key: str | None) -> None:
    expected = os.getenv("FG_DESIGN_AGENT_KEY", "")
    if not expected:
        return
    if not header_key or header_key != expected:
        raise HTTPException(status_code=401, detail="Ongeldige API-sleutel.")


def _parse_json_list(raw: str) -> list:
    try:
        val = json.loads(raw) if raw else []
        return val if isinstance(val, list) else []
    except json.JSONDecodeError:
        return []


def _parse_bool_form(raw: str) -> bool:
    return raw.strip().lower() in ("true", "1", "yes")


def _resolve_positionering(positionering: str, stijl: str) -> str:
    pos = (positionering or "").strip().lower()
    if pos in ("strak", "opvallend", "balanced"):
        return pos
    legacy = (stijl or "").strip().lower()
    if legacy in ("strak", "opvallend"):
        return legacy
    return "balanced"


def _load_ssot_rows(ssot_path: Path) -> list[dict]:
    if not ssot_path.is_file():
        return []
    return json.loads(ssot_path.read_text(encoding="utf-8"))


def _ssot_product(rows: list[dict], sku: str) -> tuple[str, float]:
    for row in rows:
        if row.get("sku") == sku:
            return str(row.get("naam", sku)), float(row.get("price_suggested", 0))
    return sku, 0.0


async def process_design_agent_generate(
    *,
    vehicle: str,
    branche: str,
    bedrijfsnaam: str,
    telefoon: str,
    website: str,
    brand_colors: str,
    tekst_opties: str,
    slogan: str,
    diensten: str,
    doelgroep: str,
    positionering: str,
    stijl: str,
    mockup_b_sku: str,
    mockup_a_sku: str,
    brief_confirmed: str,
    logo: UploadFile,
    client_ip: str,
    api_key: str | None,
    session_id: str | None = None,
) -> DesignAgentGenerateResponse:
    _verify_api_key(api_key)
    _check_rate_limit(client_ip, session_id)

    if not _parse_bool_form(brief_confirmed):
        raise _api_error(400, "BRIEF_INCOMPLETE", "Bevestig je briefing eerst.")

    if not bedrijfsnaam.strip():
        raise _api_error(400, "BRIEF_INCOMPLETE", "Bedrijfsnaam is verplicht.")

    _validate_generate_brief(
        bedrijfsnaam=bedrijfsnaam,
        branche=branche,
        diensten=diensten,
        doelgroep=doelgroep,
        vehicle=vehicle,
    )

    logo_bytes = await logo.read()
    if len(logo_bytes) > 5 * 1024 * 1024:
        raise _api_error(400, "LOGO_INVALID", "Logo mag maximaal 5 MB zijn.")
    _validate_logo_upload(logo, logo_bytes)

    colors = _parse_json_list(brand_colors)
    opts = _parse_json_list(tekst_opties)
    user_positionering = _resolve_positionering(positionering, stijl)

    output_root = Path(os.getenv("DESIGN_AGENT_OUTPUT_DIR", "output/design-agent"))
    ssot_path = Path(
        os.getenv(
            "ZZPACKAGE_SSOT_PATH",
            "../zzpackage.flexgrafik.nl/system/data/product-master-table.json",
        )
    )
    public_base = (
        os.getenv("DESIGN_AGENT_PUBLIC_URL", "").strip()
        or os.getenv("DESIGN_AGENT_MOCKUP_PUBLIC_BASE", "").strip()
    )
    if not public_base:
        logger.warning(
            "DESIGN_AGENT_PUBLIC_URL not set — mockups use base64 data URLs (large payloads)."
        )

    mode = _engine_mode()
    try:
        if mode == "inspire":
            from agent.inspire.engine import generate_inspire_mockups

            result = generate_inspire_mockups(
                vehicle=vehicle,
                branche=branche,
                bedrijfsnaam=bedrijfsnaam.strip(),
                telefoon=telefoon,
                website=website,
                brand_colors=colors,
                tekst_opties=opts,
                slogan=slogan,
                stijl=user_positionering,  # type: ignore[arg-type]
                positionering=user_positionering,  # type: ignore[arg-type]
                diensten=diensten,
                doelgroep=doelgroep,
                mockup_b_sku=mockup_b_sku,
                mockup_a_sku=mockup_a_sku,
                logo_bytes=logo_bytes,
                output_dir=output_root,
                ssot_path=ssot_path,
                public_base_url=public_base,
            )
        else:
            _ensure_vge_import()
            from vge.models.design_agent_brief import DesignAgentBrief
            from vge.services.design_agent import generate_design_agent_mockups

            brief = DesignAgentBrief(
                vehicle=vehicle,  # type: ignore[arg-type]
                branche=branche,
                bedrijfsnaam=bedrijfsnaam.strip(),
                telefoon=telefoon,
                website=website,
                brand_colors=colors,
                tekst_opties=opts,
                slogan=slogan,
                stijl=user_positionering,  # type: ignore[arg-type]
            )
            result = generate_design_agent_mockups(
                brief,
                logo_bytes,
                output_root,
                ssot_path,
                public_base_url=public_base,
            )
    except ValueError as exc:
        raise _api_error(400, "GENERATION_FAILED", str(exc)) from exc
    except RuntimeError as exc:
        logger.exception("design-agent inspire runtime error")
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("design-agent generate failed")
        raise HTTPException(
            status_code=500,
            detail="Mock-up generatie mislukt. Probeer het later opnieuw.",
        ) from exc

    _log_generation_cost(result.brief_id, vehicle, result.cost_eur)

    if session_id and session_id.strip():
        try:
            from agent.inspire.chat_advisor import mark_brief_confirmed

            mark_brief_confirmed(session_id.strip())
        except Exception:
            logger.debug("mark_brief_confirmed skipped session_id=%s", session_id)

    ssot_rows = _load_ssot_rows(ssot_path)
    engine_mode, generator_provider = _resolve_engine_meta(result)
    mockups: list[DesignAgentMockupItem] = []
    for m in result.mockups:
        url = m.url or m.data_url or ""
        sku = m.sku or ""
        client_variant = _client_variant(m.variant)
        naam, price = _ssot_product(ssot_rows, sku) if sku else ("", 0.0)
        mockups.append(
            DesignAgentMockupItem(
                variant=client_variant,
                panel=m.panel,
                url=url,
                sku=sku,
                naam=naam,
                price_suggested=price,
                label_nl=TIER_LABELS.get(client_variant, TIER_LABELS.get(m.variant, "")),
                degraded=m.degraded,
            )
        )

    products = [
        DesignAgentProductItem(
            sku=p.sku,
            naam=p.naam,
            price_suggested=p.price_suggested,
            highlight=p.highlight,
        )
        for p in result.recommended_products
    ]

    pos = getattr(result, "positionering", result.user_stijl)

    return DesignAgentGenerateResponse(
        brief_id=result.brief_id,
        mockups=mockups,
        recommended_products=products,
        wizard_deeplink=result.wizard_deeplink,
        cost_eur=result.cost_eur,
        positionering=pos,
        mockup_b_sku=getattr(result, "mockup_b_sku", ""),
        mockup_a_sku=getattr(result, "mockup_a_sku", ""),
        user_stijl=pos,
        engine_mode=engine_mode,
        generator_provider=generator_provider,
    )
