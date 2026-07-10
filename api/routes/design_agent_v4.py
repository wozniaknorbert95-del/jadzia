"""Design Agent v4 endpoints — intake, brief, recommend, render, checkout."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, Header, HTTPException, Request, UploadFile
from pydantic import BaseModel

from agent.design_agent_service import _verify_api_key

router = APIRouter(tags=["design-agent-v4"])


def _inspire_repo() -> Path:
    env = os.getenv("INSPIRE_REPO_PATH", "").strip()
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2].parent / "flexgrafik-inspire"


def _load_v4_handlers():
    repo = _inspire_repo()
    if not repo.is_dir():
        raise HTTPException(status_code=503, detail="INSPIRE v4 repo niet gevonden.")
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    from engine.v4 import api_handlers

    return api_handlers


class IntakeMessageRequest(BaseModel):
    session_id: str | None = None
    message: str = ""
    field_updates: dict[str, Any] | None = None


class BriefConfirmRequest(BaseModel):
    brief_draft: dict[str, Any]
    confirm: bool = True


class RecommendRequest(BaseModel):
    brief_draft: dict[str, Any]


class CheckoutDeeplinkRequest(BaseModel):
    vehicle: str
    sku: str


@router.post("/api/v1/design-agent/intake/message")
async def intake_message(
    request: Request,
    body: IntakeMessageRequest,
    x_fg_design_agent_key: str | None = Header(None, alias="X-FG-Design-Agent-Key"),
) -> dict[str, Any]:
    _verify_api_key(x_fg_design_agent_key)
    handlers = _load_v4_handlers()
    return handlers.handle_intake_message(
        session_id=body.session_id,
        message=body.message,
        field_updates=body.field_updates,
    )


@router.post("/api/v1/design-agent/brief/confirm")
async def brief_confirm(
    body: BriefConfirmRequest,
    x_fg_design_agent_key: str | None = Header(None, alias="X-FG-Design-Agent-Key"),
) -> dict[str, Any]:
    _verify_api_key(x_fg_design_agent_key)
    handlers = _load_v4_handlers()
    return handlers.handle_brief_confirm(body.brief_draft, confirm=body.confirm)


@router.post("/api/v1/design-agent/recommend")
async def recommend_products(
    body: RecommendRequest,
    x_fg_design_agent_key: str | None = Header(None, alias="X-FG-Design-Agent-Key"),
) -> dict[str, Any]:
    _verify_api_key(x_fg_design_agent_key)
    handlers = _load_v4_handlers()
    return handlers.handle_recommend(body.brief_draft)


@router.post("/api/v1/design-agent/mockups/render")
async def mockups_render(
    request: Request,
    brief_json: str = Form(...),
    logo: UploadFile | None = File(None),
    x_fg_design_agent_key: str | None = Header(None, alias="X-FG-Design-Agent-Key"),
) -> dict[str, Any]:
    _verify_api_key(x_fg_design_agent_key)
    import json

    handlers = _load_v4_handlers()
    brief_draft = json.loads(brief_json)
    logo_bytes = await logo.read() if logo else None
    public_base = os.getenv("DESIGN_AGENT_PUBLIC_BASE_URL", "").strip()
    output_dir = Path(os.getenv("DESIGN_AGENT_OUTPUT_DIR", "output/design-agent"))
    return handlers.handle_mockups_render(
        brief_draft,
        logo_bytes=logo_bytes,
        output_dir=output_dir,
        public_base_url=public_base,
    )


@router.post("/api/v1/design-agent/checkout/deeplink")
async def checkout_deeplink(
    body: CheckoutDeeplinkRequest,
    x_fg_design_agent_key: str | None = Header(None, alias="X-FG-Design-Agent-Key"),
) -> dict[str, Any]:
    _verify_api_key(x_fg_design_agent_key)
    handlers = _load_v4_handlers()
    return handlers.handle_checkout_deeplink(body.vehicle, body.sku)
