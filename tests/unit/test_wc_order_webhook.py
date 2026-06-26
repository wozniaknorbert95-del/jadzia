"""Tests for POST /webhooks/woocommerce/order (INT-002)."""

import hashlib
import hmac
import json
import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from api.app import create_app


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


@pytest.fixture
def client():
    return TestClient(create_app())


def _valid_payload() -> dict:
    return {
        "order_id": "WC-5005",
        "status": "completed",
        "items": [{"sku": "PKG-GROW", "qty": 2, "price": 199.0}],
        "customer": {"email": "buyer@example.nl", "name": "Buyer"},
        "total_gross": 398.0,
        "payment_id": "tr_mollie_xyz",
    }


def test_wc_order_webhook_success(client, temp_db):
    r = client.post("/webhooks/woocommerce/order", json=_valid_payload())
    assert r.status_code == 200
    data = r.json()
    assert data["db_status"] == "success"
    assert data["order_internal_id"] == "1"


def test_wc_order_webhook_invalid_payload(client, temp_db):
    bad = _valid_payload()
    bad["status"] = "cancelled"
    r = client.post("/webhooks/woocommerce/order", json=bad)
    assert r.status_code == 422


def test_wc_order_webhook_hmac_required(monkeypatch, client, temp_db):
    monkeypatch.setenv("WC_WEBHOOK_SECRET", "test-secret")
    import api.routes.webhooks as wh_mod

    monkeypatch.setattr(wh_mod, "WC_WEBHOOK_SECRET", "test-secret")

    body = json.dumps(_valid_payload()).encode("utf-8")
    r = client.post(
        "/webhooks/woocommerce/order",
        content=body,
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 401

    sig = hmac.new(b"test-secret", body, hashlib.sha256).hexdigest()
    r = client.post(
        "/webhooks/woocommerce/order",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-WC-Signature": sig,
        },
    )
    assert r.status_code == 200
    assert r.json()["db_status"] == "success"
