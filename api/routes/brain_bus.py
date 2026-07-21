"""Brain Bus inbound webhook — VCMS/KODA → jadzia (MKT-BRAIN-PRO F3)."""

from __future__ import annotations

import hmac
import logging
import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from core.config import require_secrets_enabled
from api.ingress import BRAIN_BUS_BODY_MAX_BYTES, read_limited_body_async

logger = logging.getLogger(__name__)

router = APIRouter(tags=["brain-bus"])


class BrainBusEventIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_type: str = Field(min_length=1, max_length=64)
    source_brain: str = Field(default="vcms", min_length=1, max_length=32)
    payload: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: str = Field(min_length=1, max_length=128)

    @field_validator("correlation_id")
    @classmethod
    def validate_correlation_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("correlation_id must not be blank")
        return value

    @model_validator(mode="after")
    def validate_payload_size(self) -> "BrainBusEventIn":
        import json

        encoded = json.dumps(self.payload, ensure_ascii=False, separators=(",", ":"))
        if len(encoded.encode("utf-8")) > 8_192:
            raise ValueError("payload exceeds 8192 bytes")
        return self


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
    request: Request,
    x_brain_bus_secret: Optional[str] = Header(default=None, alias="X-Brain-Bus-Secret"),
    process: bool = True,
) -> dict:
    """
    Ingest structured Brain Bus event.
    VCMS scan: event_type=system.health.degraded|recovered, payload.conflicts.
    """
    _require_brain_bus_secret(x_brain_bus_secret)
    body_raw = await read_limited_body_async(request, max_bytes=BRAIN_BUS_BODY_MAX_BYTES)
    try:
        body = BrainBusEventIn.model_validate_json(body_raw)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail="Invalid Brain Bus event payload") from exc
    from agent.db import db_claim_ingress_replay
    from agent.marketing.brain_bus import ingest_brain_bus_event, normalize_inbound_event
    from agent.marketing.brain_events import process_brain_events

    try:
        normalized = normalize_inbound_event(body.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not db_claim_ingress_replay(
        f"brain_bus:{normalized['source_brain']}",
        normalized["correlation_id"],
        ttl_sec=7 * 24 * 3600,
    ):
        return {"ok": True, "duplicate": True, "correlation_id": normalized["correlation_id"]}
    enq = ingest_brain_bus_event(normalized)
    if not enq.get("ok"):
        raise HTTPException(status_code=500, detail=enq)
    out: Dict[str, Any] = {"ok": True, "enqueued": enq}
    if process:
        out["processed"] = process_brain_events(limit=10, send_telegram=True)
    return out
