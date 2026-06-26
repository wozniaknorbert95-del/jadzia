"""Order ingestion node — INT-002 WooCommerce webhook processor."""

from __future__ import annotations

import logging
from typing import Dict, List

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
        logger.error(
            "[OrderNode] Persist failed order_id=%s", payload.order_id
        )
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


def _payload_to_db_dict(payload: WooOrderWebhookRequest) -> Dict:
    items: List[Dict] = [
        {"sku": item.sku, "qty": item.qty, "price": item.price}
        for item in payload.items
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
    }
