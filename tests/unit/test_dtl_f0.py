"""MKT-BRAIN-PRO F0 — Data Truth Layer unit tests (fixtures only, no fake prod)."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from unittest.mock import patch

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from agent.db import (
    db_get_order_margin_fact,
    db_list_active_quality_flags,
    db_list_marketing_facts,
    db_list_orders_full,
    db_margin_coverage_stats,
    db_upsert_order,
    get_connection,
)
from agent.marketing.dtl.attribution import (
    build_attribution_chains,
    channel_from_attribution,
    ingest_attribution,
)
from agent.marketing.dtl.margin import calc_margin_v1, ingest_order_margins
from agent.marketing.dtl.ops import ingest_leads_snapshot, ingest_orders_snapshot
from agent.marketing.dtl.pipeline import run_dtl_ingest
from agent.marketing.dtl.quality import evaluate_margin_coverage_flag, run_quality_pass
from agent.marketing.dtl.report import build_data_health_report
from api.app import create_app
from core.models import AnalyticsSnapshotResponse, AnalyticsSnapshotSources, AnalyticsSourceZzpackageMetrics

JWT_SECRET_VALUE = "test-secret-dtl-f0"


@pytest.fixture
def temp_db(monkeypatch):
    import tempfile

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr("agent.db.DB_PATH", path)
    import agent.db as db_mod

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
    yield path
    try:
        if hasattr(db_mod._local, "conn") and db_mod._local.conn:
            db_mod._local.conn.close()
            db_mod._local.conn = None
        os.unlink(path)
    except OSError:
        pass


def _seed_order(
    order_id: str,
    gross: float = 199.0,
    *,
    attribution: dict | None = None,
    checkout_id: str | None = None,
) -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    ok = db_upsert_order(
        {
            "order_id": order_id,
            "status": "completed",
            "items": [{"sku": "PKG", "qty": 1, "price": gross}],
            "customer": {"email": f"{order_id}@example.test", "name": "Test"},
            "total_gross": gross,
            "payment_id": f"pay_{order_id}",
            "checkout_id": checkout_id,
            "attribution": attribution or {},
            "created_at": now,
            "updated_at": now,
        }
    )
    assert ok is not None, f"seed order failed: {order_id}"


def test_dtl_schema_tables_exist(temp_db):
    conn = get_connection()
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    for name in (
        "marketing_raw_ingest",
        "marketing_facts",
        "data_quality_flags",
        "order_margin_facts",
    ):
        assert name in tables


def test_calc_margin_v1_playbook_60pct():
    calc = calc_margin_v1(200.0, shipping=10.0)
    assert calc["cogs"] == 80.0
    assert calc["net_margin"] == 110.0
    assert calc["net_margin_pct"] == pytest.approx(0.55)


def test_ingest_order_margins_and_coverage(temp_db):
    _seed_order("ord-100", 199.0, attribution={"utm_source": "meta", "utm_medium": "paid"})
    _seed_order("ord-101", 299.0, attribution={"utm_source": "blog", "utm_medium": "organic"})

    result = ingest_order_margins()
    assert result["status"] == "ok"
    assert result["written"] == 2

    m100 = db_get_order_margin_fact("ord-100")
    assert m100 is not None
    assert m100["cogs_method"] == "playbook_60pct"
    assert m100["gross"] == 199.0
    assert m100["cogs"] == pytest.approx(79.6)
    assert m100["attribution_channel"] == "meta/paid"

    stats = db_margin_coverage_stats()
    assert stats["orders_total"] == 2
    assert stats["margin_facts"] == 2
    assert stats["coverage_pct"] == 100.0

    flag = evaluate_margin_coverage_flag()
    assert flag is None


def test_attribution_l1_l2_stitch(temp_db):
    assert channel_from_attribution({}) == "unknown"
    assert channel_from_attribution({"utm_source": "meta", "utm_medium": "paid"}) == "meta/paid"

    # L2 stitch via ga_client_id (checkout_id is UNIQUE per order)
    _seed_order(
        "ord-a1",
        199.0,
        checkout_id="chk-a1",
        attribution={
            "utm_source": "meta",
            "utm_medium": "paid",
            "utm_campaign": "zzp_v1",
            "ga_client_id": "ga.1",
        },
    )
    _seed_order(
        "ord-a2",
        99.0,
        checkout_id="chk-a2",
        attribution={
            "utm_source": "blog",
            "utm_medium": "organic",
            "ga_client_id": "ga.1",
        },
    )
    _seed_order(
        "ord-orphan",
        50.0,
        attribution={"utm_source": "tiktok", "utm_medium": "organic"},
    )

    orders = db_list_orders_full(limit=50)
    chains = build_attribution_chains(orders)
    l2 = [c for c in chains if c["level"] == "L2"]
    assert len(l2) == 1
    assert l2[0]["assisted"] is True
    assert set(l2[0]["order_ids"]) == {"ord-a1", "ord-a2"}

    result = ingest_attribution()
    assert result["status"] == "ok"
    assert result["l2_sessions"] == 1
    assert result["coverage_pct"] > 0

    facts = db_list_marketing_facts(metric_key="orders_by_last_touch", limit=20)
    assert len(facts) >= 1


def test_ops_ingest_writes_facts(temp_db):
    _seed_order("ord-ops", 120.0)
    r1 = ingest_orders_snapshot()
    r2 = ingest_leads_snapshot()
    assert r1["status"] == "ok"
    assert r2["status"] == "ok"
    facts = db_list_marketing_facts(metric_key="ops_orders_count", limit=5)
    assert len(facts) == 1
    assert facts[0]["value"] == 1.0


def test_pipeline_with_mocked_ga4_and_l0(temp_db):
    _seed_order(
        "ord-pipe",
        199.0,
        checkout_id="chk-pipe",
        attribution={"utm_source": "meta", "utm_medium": "paid"},
    )
    fake_snap = AnalyticsSnapshotResponse(
        sync_status="success",
        generated_at="2026-07-19T10:00:00+00:00",
        period="last_7_days",
        sources=AnalyticsSnapshotSources(
            zzpackage=AnalyticsSourceZzpackageMetrics(
                sessions=10, conversions=1, purchase_revenue=199.0, aov=199.0
            )
        ),
        errors=[],
    )
    fake_l0 = {
        "url": "https://example.test/wizard/",
        "http_status": 200,
        "fbq": True,
        "fbevents": True,
        "gtm": True,
        "body_bytes": 100,
    }
    with patch(
        "agent.marketing.dtl.ga4.fetch_analytics_snapshot",
        create=True,
    ), patch(
        "agent.nodes.analytics_node.fetch_analytics_snapshot",
        return_value=fake_snap,
    ), patch(
        "agent.marketing.dtl.l0_probe.probe_wizard_html",
        return_value=fake_l0,
    ):
        summary = run_dtl_ingest(include_ga4=True, include_l0=True)

    assert summary["steps_error"] == 0
    assert summary["steps_ok"] >= 5
    report = build_data_health_report()
    assert report["panel"] == "data_health"
    assert "freshness" in report
    assert "margin_coverage" in report
    assert report["margin_coverage"]["margin_facts"] >= 1


def test_quality_flags_on_ga4_fail(temp_db):
    fail_snap = AnalyticsSnapshotResponse(
        sync_status="fail",
        generated_at="2026-07-19T10:00:00+00:00",
        period="last_7_days",
        sources=AnalyticsSnapshotSources(),
        errors=["ga4 not configured"],
    )
    with patch(
        "agent.nodes.analytics_node.fetch_analytics_snapshot",
        return_value=fail_snap,
    ):
        from agent.marketing.dtl.ga4 import ingest_ga4_snapshot

        result = ingest_ga4_snapshot()
    assert result["status"] == "error"
    flags = db_list_active_quality_flags()
    assert any(f["source"] == "ga4" and f["flag_type"] == "api_error" for f in flags)


def test_data_health_api(temp_db):
    client = TestClient(create_app())
    token = pyjwt.encode(
        {"sub": "norbert", "role": "dowodca"},
        JWT_SECRET_VALUE,
        algorithm="HS256",
    )
    headers = {"Authorization": f"Bearer {token}"}
    with patch.dict(os.environ, {"JWT_SECRET": JWT_SECRET_VALUE}, clear=False), patch(
        "api.dependencies.JWT_SECRET",
        JWT_SECRET_VALUE,
    ):
        r = client.get("/api/v1/commander/marketing/data-health", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["panel"] == "data_health"
    assert "freshness" in body
    assert "quality_flags" in body
    assert "margin_coverage" in body


def test_run_quality_pass_empty_db(temp_db):
    result = run_quality_pass()
    assert "stale_flags" in result
    assert result["margin_stats"]["orders_total"] == 0
