"""Design Agent REST handler — INSPIRE v2 (fal full-frame) or legacy VGE."""

from __future__ import annotations

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

_ALLOWED_LOGO_MIMES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/svg+xml",
    "application/pdf",
}
_ALLOWED_LOGO_EXT = {".png", ".jpg", ".jpeg", ".svg", ".pdf"}


def _engine_mode() -> str:
    return os.getenv("DESIGN_AGENT_ENGINE", "inspire").strip().lower()


def _validate_logo_upload(logo: UploadFile, logo_bytes: bytes) -> None:
    filename = (logo.filename or "").lower()
    ext = Path(filename).suffix
    if ext and ext not in _ALLOWED_LOGO_EXT:
        raise HTTPException(
            status_code=400,
            detail="Logo moet PNG, JPG, SVG of PDF zijn.",
        )
    content_type = (logo.content_type or "").split(";")[0].strip().lower()
    if content_type and content_type not in _ALLOWED_LOGO_MIMES:
        raise HTTPException(
            status_code=400,
            detail="Logo moet PNG, JPG, SVG of PDF zijn.",
        )
    if len(logo_bytes) < 32:
        raise HTTPException(status_code=400, detail="Logo-bestand is te klein of beschadigd.")


def _log_generation_cost(brief_id: str, vehicle: str, cost_eur: float) -> None:
    logger.info(
        "design-agent cost brief_id=%s vehicle=%s cost_eur=%.4f engine=%s",
        brief_id,
        vehicle,
        cost_eur,
        _engine_mode(),
    )


def _check_rate_limit(client_ip: str) -> None:
    now = time.time()
    hits = _RATE.get(client_ip, [])
    hits = [t for t in hits if now - t < _RATE_WINDOW_SEC]
    if len(hits) >= _RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Te veel verzoeken. Probeer het over een uur opnieuw.",
        )
    hits.append(now)
    _RATE[client_ip] = hits


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
    import json

    try:
        val = json.loads(raw) if raw else []
        return val if isinstance(val, list) else []
    except json.JSONDecodeError:
        return []


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
    stijl: str,
    logo: UploadFile,
    client_ip: str,
    api_key: str | None,
) -> DesignAgentGenerateResponse:
    _verify_api_key(api_key)
    _check_rate_limit(client_ip)

    if not bedrijfsnaam.strip():
        raise HTTPException(status_code=400, detail="Bedrijfsnaam is verplicht.")

    logo_bytes = await logo.read()
    if len(logo_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Logo mag maximaal 5 MB zijn.")
    _validate_logo_upload(logo, logo_bytes)

    colors = _parse_json_list(brand_colors)
    opts = _parse_json_list(tekst_opties)
    user_stijl = stijl if stijl in ("strak", "opvallend") else "strak"

    output_root = Path(os.getenv("DESIGN_AGENT_OUTPUT_DIR", "output/design-agent"))
    ssot_path = Path(
        os.getenv(
            "ZZPACKAGE_SSOT_PATH",
            "../zzpackage.flexgrafik.nl/system/data/product-master-table.json",
        )
    )
    public_base = os.getenv("DESIGN_AGENT_PUBLIC_URL", "")
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
                stijl=user_stijl,  # type: ignore[arg-type]
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
                stijl=user_stijl,  # type: ignore[arg-type]
            )
            result = generate_design_agent_mockups(
                brief,
                logo_bytes,
                output_root,
                ssot_path,
                public_base_url=public_base,
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
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

    mockups: list[DesignAgentMockupItem] = []
    for m in result.mockups:
        url = m.url or m.data_url or ""
        mockups.append(
            DesignAgentMockupItem(variant=m.variant, panel=m.panel, url=url, degraded=m.degraded)
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

    return DesignAgentGenerateResponse(
        brief_id=result.brief_id,
        mockups=mockups,
        recommended_products=products,
        wizard_deeplink=result.wizard_deeplink,
        cost_eur=result.cost_eur,
        user_stijl=result.user_stijl,
    )
