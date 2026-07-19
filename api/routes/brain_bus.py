"""Brain Bus inbound webhook — VCMS/KODA → jadzia (MKT-BRAIN-PRO F3)."""

from __future__ import annotations

import hmac
import logging
import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from core.config import require_secrets_enabled

logger = logging.getLogger(__name__)

router = APIRouter(tags=["brain-bus"])


class BrainBusEventIn(BaseModel):
    event_type: str
    source_brain: str = "vcms"
    payload: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None


def _require_brain_bus_secret(provided: Optional[str]) -> None:
    secret = os.getenv("BRAIN_BUS_SECRET", "").strip()
    if not secret:
        if require_secrets_enabled():
            raise HTTPException(status_code=500, detail="BRAIN_BUS_SECRET not configured")
        logger.warning("[brain_bus] BRAIN_BUS_SECRET unset — auth skipped (non-prod)")
        return
    if not provided or not hmac.compare_digest(provided.strip(), secret):
        raise HTTPException(status_code=401, detail="Invalid or missing X-Brain-Bus-Secret")


@router.post("/api/v1/brain-bus/events")
async def post_brain_bus_event(
    body: BrainBusEventIn,
    x_brain_bus_secret: Optional[str] = Header(default=None, alias="X-Brain-Bus-Secret"),
    process: bool = True,
) -> dict:
    """
    Ingest structured Brain Bus event.
    VCMS scan: event_type=system.health.degraded|recovered, payload.conflicts.
    """
    _require_brain_bus_secret(x_brain_bus_secret)
    from agent.marketing.brain_bus import ingest_brain_bus_event
    from agent.marketing.brain_events import process_brain_events

    try:
        enq = ingest_brain_bus_event(body.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not enq.get("ok"):
        raise HTTPException(status_code=500, detail=enq)
    out: Dict[str, Any] = {"ok": True, "enqueued": enq}
    if process:
        out["processed"] = process_brain_events(limit=10, send_telegram=True)
    return out
