"""Inbound webhook routes — INT-002 WooCommerce order ingestion."""

from __future__ import annotations

import hashlib
import hmac
import logging
import os

from fastapi import APIRouter, HTTPException, Request
from pydantic import ValidationError

from core.config import require_secrets_enabled
from core.models import WooOrderWebhookRequest, WooOrderWebhookResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["webhooks"])

WC_WEBHOOK_SECRET = os.getenv("WC_WEBHOOK_SECRET", "")


def _validate_wc_hmac(body: bytes, signature: str | None) -> None:
    """Validate HMAC-SHA256 signature when WC_WEBHOOK_SECRET is configured."""
    if not WC_WEBHOOK_SECRET:
        if require_secrets_enabled():
            raise HTTPException(status_code=500, detail="WC_WEBHOOK_SECRET not configured")
        logger.warning("WC_WEBHOOK_SECRET not configured — webhook auth skipped")
        return

    if not signature:
        raise HTTPException(status_code=401, detail="Missing X-WC-Signature header")

    expected = hmac.new(
        WC_WEBHOOK_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()

    provided = signature.removeprefix("sha256=").strip()
    if not hmac.compare_digest(expected, provided):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")


@router.post(
    "/webhooks/woocommerce/order",
    response_model=WooOrderWebhookResponse,
)
async def woocommerce_order_webhook(request: Request) -> WooOrderWebhookResponse:
    """Receive order payload from zzpackage WooCommerce (INT-002)."""
    body = await request.body()
    _validate_wc_hmac(body, request.headers.get("X-WC-Signature"))

    try:
        payload = WooOrderWebhookRequest.model_validate_json(body)
    except ValidationError as e:
        logger.warning("[WCWebhook] Invalid payload: %s", e)
        raise HTTPException(status_code=422, detail=e.errors()) from e

    from agent.nodes.order_node import process_order_webhook

    return process_order_webhook(payload)
