"""Design Agent generate endpoint — ZZPackage voertuigreclame mockups."""

from __future__ import annotations

import os

from fastapi import APIRouter, File, Form, Header, Request, UploadFile

from agent.design_agent_service import process_design_agent_generate
from core.models import DesignAgentGenerateResponse

router = APIRouter(tags=["design-agent"])


@router.get("/api/v1/design-agent/health")
async def design_agent_health() -> dict:
    """Public readiness probe for Commander system map / Agenci INSPIRE hop."""
    provider = (os.getenv("INSPIRE_GENERATOR_PROVIDER") or "stub").strip() or "stub"
    return {
        "status": "ok",
        "service": "design-agent",
        "inspire_provider": provider,
        "routes": {
            "generate": "/api/v1/design-agent/generate",
            "chat": "/api/v1/design-agent/chat",
        },
    }


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
    diensten: str = Form(""),
    doelgroep: str = Form(""),
    positionering: str = Form(""),
    stijl: str = Form("strak"),
    regio: str = Form(""),
    vehicle_usage: str = Form(""),
    desired_impression: str = Form(""),
    budget_range: str = Form(""),
    budget_explicit: str = Form("false"),
    mockup_b_sku: str = Form(""),
    mockup_a_sku: str = Form(""),
    brief_confirmed: str = Form("false"),
    session_id: str = Form(""),
    logo: UploadFile = File(...),
    x_fg_design_agent_key: str | None = Header(None, alias="X-FG-Design-Agent-Key"),
) -> DesignAgentGenerateResponse:
    """Generate 2 inspiration mockups (INSPIRE v4 — inspirationOnly, no fal customer path)."""
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
        diensten=diensten,
        doelgroep=doelgroep,
        positionering=positionering,
        stijl=stijl,
        regio=regio,
        vehicle_usage=vehicle_usage,
        desired_impression=desired_impression,
        budget_range=budget_range,
        budget_explicit=budget_explicit,
        mockup_b_sku=mockup_b_sku,
        mockup_a_sku=mockup_a_sku,
        brief_confirmed=brief_confirmed,
        logo=logo,
        client_ip=client_ip,
        api_key=x_fg_design_agent_key,
        session_id=session_id or None,
    )
