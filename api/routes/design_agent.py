"""Design Agent generate endpoint — ZZPackage voertuigreclame mockups."""

from __future__ import annotations

from fastapi import APIRouter, File, Form, Header, Request, UploadFile

from agent.design_agent_service import process_design_agent_generate
from core.models import DesignAgentGenerateResponse

router = APIRouter(tags=["design-agent"])


@router.post("/api/v1/design-agent/generate", response_model=DesignAgentGenerateResponse)
async def design_agent_generate(
    request: Request,
    vehicle: str = Form(...),
    branche: str = Form(""),
    bedrijfsnaam: str = Form(...),
    telefoon: str = Form(""),
    website: str = Form(""),
    brand_colors: str = Form("[]"),
    tekst_opties: str = Form("[]"),
    slogan: str = Form(""),
    stijl: str = Form("strak"),
    logo: UploadFile = File(...),
    x_fg_design_agent_key: str | None = Header(None, alias="X-FG-Design-Agent-Key"),
) -> DesignAgentGenerateResponse:
    """Generate 2 photoreal inspiration mockups (INSPIRE v2 fal full-frame)."""
    client_ip = request.client.host if request.client else "unknown"
    return await process_design_agent_generate(
        vehicle=vehicle,
        branche=branche,
        bedrijfsnaam=bedrijfsnaam,
        telefoon=telefoon,
        website=website,
        brand_colors=brand_colors,
        tekst_opties=tekst_opties,
        slogan=slogan,
        stijl=stijl,
        logo=logo,
        client_ip=client_ip,
        api_key=x_fg_design_agent_key,
    )
