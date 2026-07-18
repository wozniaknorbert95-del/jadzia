"""Tests for PII-free, no-delete REV-R0-02 reconciliation."""

import os
import tempfile

import pytest

from agent.db import (
    db_create_lead,
    db_get_revenue_classification,
    db_list_revenue_classifications,
    db_record_revenue_classification,
    db_upsert_order,
    get_connection,
)
from agent.revenue.reconciliation import (
    apply_unpersisted_classifications,
    build_reconciliation_report,
)


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


def _order(order_id: str, payment_id: str, total: float = 349.0) -> dict:
    return {
        "order_id": order_id,
        "status": "processing",
        "items": [{"sku": "PKG-START", "qty": 1, "price": total}],
        "customer": {"email": "customer@bouw.nl", "name": "Customer"},
        "total_gross": total,
        "payment_id": payment_id,
    }


def _seed_legacy_data() -> None:
    db_upsert_order(_order("4201", "tr_live_4201"))
    db_upsert_order(_order("SMOKE-1", "tr_test_smoke"))
    db_create_lead(
        {
            "email": "int004-e2e-20260717@flexgrafik.nl",
            "name": "E2E",
            "source": "game",
            "consent_status": True,
        }
    )
    db_create_lead(
        {
            "email": "customer@bouw.nl",
            "name": "Customer",
            "source": "game",
            "consent_status": True,
        }
    )
    conn = get_connection()
    conn.execute("""
        INSERT INTO portal_qual_leads (
            session_id, recommended_preset_id, source, consent, created_at
        ) VALUES ('portal-1', 'starter', 'portal_qual', 1, '2026-07-17T10:00:00Z')
        """)
    conn.commit()


def test_report_is_read_only_and_excludes_test_order_from_ga4_gap(temp_db):
    _seed_legacy_data()
    conn = get_connection()
    before = {
        table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in ("orders", "leads", "portal_qual_leads")
    }

    report = build_reconciliation_report(conn, ga4_transaction_ids=["WC-4201"])

    after = {
        table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in ("orders", "leads", "portal_qual_leads")
    }
    assert after == before
    assert report["history_preserved"] is True
    assert report["summary"]["classifications"] == {
        "real": 1,
        "test": 2,
        "unknown": 2,
    }
    assert report["summary"]["paid_orders_kpi_eligible"] == 1
    assert report["ga4_order_reconciliation"] == {
        "status": "matched",
        "matched_order_ids": ["4201"],
        "missing_ga4_order_ids": [],
        "ga4_orphan_transaction_ids": [],
    }
    assert "customer@bouw.nl" not in str(report)


def test_apply_is_idempotent_and_never_overwrites_existing_decision(temp_db):
    _seed_legacy_data()
    first_report = build_reconciliation_report()
    first = apply_unpersisted_classifications(first_report)
    second_report = build_reconciliation_report()
    second = apply_unpersisted_classifications(second_report)

    assert first == {"inserted": 5, "skipped_existing": 0}
    assert second == {"inserted": 0, "skipped_existing": 5}
    assert len(db_list_revenue_classifications()) == 5

    db_record_revenue_classification(
        "lead",
        "2",
        "real",
        "manual_verification",
        classified_by="human:dowodca",
    )
    latest = db_get_revenue_classification("lead", "2")
    assert latest is not None
    assert latest["classification"] == "real"
    assert latest["classified_by"] == "human:dowodca"

    third = apply_unpersisted_classifications(build_reconciliation_report())
    assert third == {"inserted": 0, "skipped_existing": 5}
    latest_after = db_get_revenue_classification("lead", "2")
    assert latest_after == latest


def test_normalized_duplicate_is_reported(temp_db):
    db_upsert_order(_order("4201", "tr_live_4201"))
    db_upsert_order(_order("WC-4201", "tr_live_legacy"))

    report = build_reconciliation_report()

    assert report["summary"]["normalized_order_duplicates"] == 1
    assert report["normalized_order_duplicates"] == [
        {
            "canonical_order_id": "4201",
            "source_order_ids": ["4201", "WC-4201"],
        }
    ]
