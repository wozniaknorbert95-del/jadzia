"""Tests for orders table persistence (INT-002)."""

import os
import tempfile

import pytest

from agent.db import db_get_order_by_internal_id, db_get_order_by_wc_id, db_upsert_order


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


def _sample_order(order_id: str = "WC-1001") -> dict:
    return {
        "order_id": order_id,
        "status": "processing",
        "items": [{"sku": "PKG-START", "qty": 1, "price": 299.0}],
        "customer": {"email": "test@example.nl", "name": "Test Klant"},
        "total_gross": 299.0,
        "payment_id": "tr_mollie_abc",
    }


def test_db_upsert_order_inserts_row(temp_db):
    internal_id = db_upsert_order(_sample_order())
    assert internal_id == "1"

    row = db_get_order_by_wc_id("WC-1001")
    assert row is not None
    assert row["order_id"] == "WC-1001"
    assert row["status"] == "processing"
    assert row["total_gross"] == 299.0
    assert row["customer"]["email"] == "test@example.nl"
    assert row["items"][0]["sku"] == "PKG-START"


def test_db_upsert_order_updates_existing(temp_db):
    db_upsert_order(_sample_order())
    updated = _sample_order()
    updated["status"] = "completed"
    updated["total_gross"] = 349.0

    internal_id = db_upsert_order(updated)
    assert internal_id == "1"

    row = db_get_order_by_wc_id("WC-1001")
    assert row is not None
    assert row["status"] == "completed"
    assert row["total_gross"] == 349.0


def test_db_get_order_by_internal_id(temp_db):
    internal_id = db_upsert_order(_sample_order("WC-2002"))
    row = db_get_order_by_internal_id(int(internal_id))
    assert row is not None
    assert row["order_internal_id"] == internal_id


def test_orders_table_exists_after_init(temp_db):
    from agent.db import get_connection

    conn = get_connection()
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    assert "orders" in tables

    cols = {
        r[1]
        for r in conn.execute("PRAGMA table_info(orders)").fetchall()
    }
    assert "order_id" in cols
    assert "items_json" in cols
