"""Order ingestion node — INT-002 WooCommerce webhook processor."""

from __future__ import annotations

import logging

from agent.db import db_upsert_order
from core.models import WooOrderWebhookRequest, WooOrderWebhookResponse

logger = logging.getLogger(__name__)


def process_order_webhook(payload: WooOrderWebhookRequest) -> WooOrderWebhookResponse:
    """
    Persist WooCommerce order mirror to jadzia.db.

    Agent card output: db_status, order_internal_id.
    """
    order_data = _payload_to_db_dict(payload)
    internal_id = db_upsert_order(order_data)

    if not internal_id:
        logger.error("[OrderNode] Persist failed order_id=%s", payload.order_id)
        return WooOrderWebhookResponse(db_status="fail", order_internal_id="")

    logger.info(
        "[OrderNode] Order saved order_id=%s internal_id=%s status=%s",
        payload.order_id,
        internal_id,
        payload.status,
    )
    return WooOrderWebhookResponse(
        db_status="success",
        order_internal_id=internal_id,
    )


def _payload_to_db_dict(payload: WooOrderWebhookRequest) -> dict:
    items: list[dict] = [
        {"sku": item.sku, "qty": item.qty, "price": item.price} for item in payload.items
    ]
    return {
        "order_id": payload.order_id,
        "status": payload.status,
        "items": items,
        "customer": {
            "email": payload.customer.email,
            "name": payload.customer.name,
        },
        "total_gross": payload.total_gross,
        "payment_id": payload.payment_id or None,
        "schema_version": payload.schema_version,
        "currency": payload.currency,
        "total_net": payload.total_net,
        "tax_total": payload.tax_total,
        "payment_status": payload.payment_status,
        "payment_method": payload.payment_method,
        "payment_provider": payload.payment_provider,
        "payment_mode": payload.payment_mode,
        "paid_at": payload.paid_at.isoformat() if payload.paid_at else None,
        "classification": payload.classification or "unknown",
        "classification_reason": payload.classification_reason,
        "is_test": payload.is_test,
        "test_reason": payload.test_reason,
        "checkout_id": payload.checkout_id,
        "checkout_started_at": (
            payload.checkout_started_at.isoformat() if payload.checkout_started_at else None
        ),
        "checkout_environment": payload.checkout_environment,
        "attribution": (payload.attribution.model_dump(mode="json") if payload.attribution else {}),
    }
