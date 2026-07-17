"""Executable producer-consumer contract tests for INT-002 v2."""

from __future__ import annotations

import os
import sqlite3
import tempfile

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from agent.db import db_get_order_by_wc_id, db_upsert_order
from agent.nodes.order_node import process_order_webhook
from api.app import create_app
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
    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
    try:
        os.unlink(path)
    except OSError:
        pass


def _v2_payload(
    order_id: str = "5201",
    checkout_id: str = "00000000-0000-4000-8000-000000005201",
    *,
    is_test: bool = False,
) -> dict:
    classification = "test" if is_test else "real"
    reason = "known_test_email_pattern" if is_test else "live_payment_in_production"
    return {
        "schema_version": "int-002.v2",
        "order_id": order_id,
        "status": "processing",
        "items": [{"sku": "PKG-GROW", "qty": 1, "price": 199.0}],
        "customer": {
            "email": "e2e-revenue@example.test" if is_test else "buyer@example.nl",
            "name": "Revenue Evidence",
        },
        "currency": "EUR",
        "total_gross": 240.79,
        "total_net": 199.0,
        "tax_total": 41.79,
        "payment_id": "tr_test_5201" if is_test else "tr_live_5201",
        "payment_status": "paid",
        "payment_method": "mollie_wc_gateway_ideal",
        "payment_provider": "mollie",
        "payment_mode": "test" if is_test else "live",
        "paid_at": "2026-07-17T18:00:00+00:00",
        "classification": classification,
        "classification_reason": reason,
        "is_test": is_test,
        "test_reason": reason if is_test else None,
        "checkout_id": checkout_id,
        "checkout_started_at": "2026-07-17T17:55:00+00:00",
        "checkout_environment": "production",
        "attribution": {
            "first_touch_source": "email",
            "first_touch_medium": "crm",
            "first_touch_campaign": "rev-r0-02c",
            "first_touch_at": "2026-07-17T17:45:00+00:00",
            "last_touch_source": "email",
            "last_touch_medium": "crm",
            "last_touch_campaign": "rev-r0-02c",
            "last_touch_at": "2026-07-17T17:55:00+00:00",
            "partner_code": None,
            "wizard_link_id": "rev-r0-02c-5201",
            "ga_client_id": None,
            "utm_source": "email",
            "utm_medium": "crm",
            "utm_campaign": "rev-r0-02c",
            "attribution_status": "partial",
        },
    }


def test_v2_model_accepts_real_and_test_producer_payloads():
    real = WooOrderWebhookRequest.model_validate(_v2_payload())
    test = WooOrderWebhookRequest.model_validate(
        _v2_payload("5202", "00000000-0000-4000-8000-000000005202", is_test=True)
    )

    assert real.classification == "real"
    assert real.is_test is False
    assert test.classification == "test"
    assert test.is_test is True


def test_v2_rejects_noncanonical_or_inconsistent_revenue_evidence():
    prefixed = _v2_payload()
    prefixed["order_id"] = "WC-5201"
    with pytest.raises(ValidationError, match="canonical numeric"):
        WooOrderWebhookRequest.model_validate(prefixed)

    inconsistent = _v2_payload()
    inconsistent["is_test"] = True
    with pytest.raises(ValidationError, match="is_test=false"):
        WooOrderWebhookRequest.model_validate(inconsistent)

    missing = _v2_payload()
    del missing["attribution"]
    with pytest.raises(ValidationError, match="missing explicit fields: attribution"):
        WooOrderWebhookRequest.model_validate(missing)

    missing_reason = _v2_payload()
    missing_reason["classification_reason"] = None
    with pytest.raises(ValidationError, match="classification_reason must be non-empty"):
        WooOrderWebhookRequest.model_validate(missing_reason)


def test_v1_payload_remains_backward_compatible():
    payload = WooOrderWebhookRequest.model_validate(
        {
            "order_id": "WC-legacy-1",
            "status": "completed",
            "items": [{"sku": "LEGACY", "qty": 1, "price": 199.0}],
            "customer": {"email": "legacy@example.nl", "name": "Legacy"},
            "total_gross": 199.0,
            "payment_id": "tr_legacy",
        }
    )
    assert payload.schema_version == "int-002.v1"
    assert payload.classification is None


def test_v2_accepts_explicit_unknown_historical_checkout_evidence():
    historical = _v2_payload()
    historical.update(
        {
            "payment_id": "",
            "payment_status": "unknown",
            "payment_mode": None,
            "paid_at": None,
            "classification": "unknown",
            "classification_reason": "missing_payment_evidence",
            "is_test": None,
            "test_reason": None,
            "checkout_id": "",
            "checkout_started_at": "",
            "checkout_environment": "unknown",
            "attribution": {
                "first_touch_source": None,
                "first_touch_medium": None,
                "first_touch_campaign": None,
                "first_touch_at": None,
                "last_touch_source": None,
                "last_touch_medium": None,
                "last_touch_campaign": None,
                "last_touch_at": None,
                "partner_code": None,
                "wizard_link_id": None,
                "ga_client_id": None,
                "utm_source": None,
                "utm_medium": None,
                "utm_campaign": None,
                "attribution_status": "unknown",
            },
        }
    )

    payload = WooOrderWebhookRequest.model_validate(historical)
    assert payload.checkout_id == ""
    assert payload.checkout_started_at is None
    assert payload.classification == "unknown"


def test_v2_api_persists_all_evidence(temp_db):
    client = TestClient(create_app())
    response = client.post("/webhooks/woocommerce/order", json=_v2_payload())

    assert response.status_code == 200
    row = db_get_order_by_wc_id("5201")
    assert row is not None
    assert row["schema_version"] == "int-002.v2"
    assert row["currency"] == "EUR"
    assert row["payment_status"] == "paid"
    assert row["payment_mode"] == "live"
    assert row["classification"] == "real"
    assert row["is_test"] is False
    assert row["test_reason"] is None
    assert row["checkout_id"] == "00000000-0000-4000-8000-000000005201"
    assert row["attribution"]["wizard_link_id"] == "rev-r0-02c-5201"


def test_v1_retry_cannot_erase_persisted_v2_evidence(temp_db):
    payload = WooOrderWebhookRequest.model_validate(_v2_payload())
    assert process_order_webhook(payload).db_status == "success"

    legacy_retry = {
        "order_id": "5201",
        "status": "completed",
        "items": [{"sku": "PKG-GROW", "qty": 1, "price": 199.0}],
        "customer": {"email": "buyer@example.nl", "name": "Revenue Evidence"},
        "total_gross": 240.79,
        "payment_id": "tr_live_5201",
    }
    assert db_upsert_order(legacy_retry) == "1"

    row = db_get_order_by_wc_id("5201")
    assert row is not None
    assert row["status"] == "completed"
    assert row["schema_version"] == "int-002.v2"
    assert row["classification"] == "real"
    assert row["checkout_id"] == "00000000-0000-4000-8000-000000005201"


def test_checkout_id_is_unique_across_orders(temp_db):
    first = WooOrderWebhookRequest.model_validate(_v2_payload())
    second = WooOrderWebhookRequest.model_validate(_v2_payload(order_id="5202"))

    assert process_order_webhook(first).db_status == "success"
    assert process_order_webhook(second).db_status == "fail"


def test_existing_v1_database_is_migrated_without_data_loss(temp_db):
    import agent.db as db_mod

    conn = sqlite3.connect(temp_db)
    conn.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL,
            items_json TEXT NOT NULL,
            customer_email TEXT,
            customer_name TEXT,
            total_gross REAL NOT NULL,
            payment_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)
    conn.execute("""
        INSERT INTO orders (
            order_id, status, items_json, total_gross, created_at, updated_at
        ) VALUES ('legacy-42', 'completed', '[]', 199, 'before', 'before')
        """)
    conn.commit()
    conn.close()

    migrated = db_mod.get_connection()
    columns = {row[1] for row in migrated.execute("PRAGMA table_info(orders)").fetchall()}
    row = migrated.execute("SELECT order_id, schema_version, classification FROM orders").fetchone()

    assert "attribution_json" in columns
    assert row["order_id"] == "legacy-42"
    assert row["schema_version"] == "int-002.v1"
    assert row["classification"] == "unknown"
