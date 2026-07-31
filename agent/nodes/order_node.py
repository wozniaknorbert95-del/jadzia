"""Order ingestion node — INT-002 WooCommerce webhook processor."""

from __future__ import annotations

import logging

from agent.db import db_get_order_by_wc_id, db_upsert_order
from core.models import WooOrderWebhookRequest, WooOrderWebhookResponse

logger = logging.getLogger(__name__)


def process_order_webhook(payload: WooOrderWebhookRequest) -> WooOrderWebhookResponse:
    """
    Persist WooCommerce order mirror to jadzia.db.

    Agent card output: db_status, order_internal_id.
    Emits ops_bus order_created on first insert only (VF-VHQ-W5).
    """
    was_new = db_get_order_by_wc_id(payload.order_id) is None
    order_data = _payload_to_db_dict(payload)
    internal_id = db_upsert_order(order_data)

    if not internal_id:
        logger.error("[OrderNode] Persist failed order_id=%s", payload.order_id)
        return WooOrderWebhookResponse(db_status="fail", order_internal_id="")

    if was_new:
        try:
            from agent.ops_bus import emit_ops_bus_event

            items = list(payload.items or [])
            emit_ops_bus_event(
                event_type="order_created",
                source_room="wizard-quote",
                dest_room="order-desk",
                payload_ref=str(payload.order_id),
                source_system="woocommerce",
                source_event_id=f"wc_order:{payload.order_id}:created",
                correlation_id=f"corr:order:{payload.order_id}",
                payload={
                    "order_id": payload.order_id,
                    "status": payload.status,
                    "total_gross": payload.total_gross,
                    "currency": getattr(payload, "currency", None),
                    "customer_email": (
                        payload.customer.email if payload.customer else None
                    ),
                    "is_test": getattr(payload, "is_test", None),
                    "classification": getattr(payload, "classification", None),
                    "item_count": len(items),
                },
                approval_level="L1",
                actor_id="woocommerce",
                actor_role="system",
                evidence_id="EV-W5-003",
            )
        except Exception as exc:
            logger.warning(
                "[OpsBus] order_created emit failed order_id=%s: %s",
                payload.order_id,
                exc,
            )

    logger.info(
        "[OrderNode] Order saved order_id=%s internal_id=%s status=%s was_new=%s",
        payload.order_id,
        internal_id,
        payload.status,
        was_new,
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
