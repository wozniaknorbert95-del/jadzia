"""Tests for order_node (INT-002)."""

import os
import tempfile

import pytest

from agent.nodes.order_node import process_order_webhook
from core.models import WooOrderWebhookRequest


@pytest.fixture
def temp_db(monkeypatch):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr("agent.db.DB_PATH", path)
    import agent.db as db_mod

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


def _payload() -> WooOrderWebhookRequest:
    return WooOrderWebhookRequest.model_validate(
        {
            "order_id": "WC-9001",
            "status": "processing",
            "items": [{"sku": "BRAND-PRO", "qty": 1, "price": 499.0}],
            "customer": {"email": "klant@zzp.nl", "name": "Jan de Vries"},
            "total_gross": 499.0,
            "payment_id": "tr_test123",
        }
    )


def test_process_order_webhook_success(temp_db):
    result = process_order_webhook(_payload())
    assert result.db_status == "success"
    assert result.order_internal_id == "1"


def test_process_order_webhook_idempotent(temp_db):
    first = process_order_webhook(_payload())
    second = process_order_webhook(_payload())
    assert first.order_internal_id == second.order_internal_id
