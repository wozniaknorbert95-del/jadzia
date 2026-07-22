"""One-shot RCA for OPS-FRESHNESS — pipeline clocks (not business quiet).

Run on VPS:
  sudo -u jadzia env PYTHONPATH=/opt/jadzia ./venv/bin/python3 deployment/_ops_freshness_rca.py
"""
from __future__ import annotations

import os

from agent.commander.sla import (
    dtl_ingest_fetched_at,
    freshness_status,
    worker_heartbeat_at,
)
from agent.commander.settings import get_settings
from agent.db import (
    db_get_latest_marketing_raw_ingest,
    db_list_analytics_snapshots,
    db_list_leads,
    db_list_orders,
)


def main() -> None:
    orders = db_list_orders(limit=1)
    leads = db_list_leads(limit=1)
    rows = db_list_analytics_snapshots(limit=1)
    settings = get_settings()
    print("LEGACY_entity_order_updated", orders[0].get("updated_at") if orders else None)
    print("LEGACY_entity_lead_updated", leads[0].get("updated_at") if leads else None)
    print("LEGACY_dowodca_last_active", settings.get("dowodca_last_active_at"))
    print("ga4_generated", rows[0].get("generated_at") if rows else None)
    print("DTL_INTERVAL_env", os.getenv("MARKETING_DTL_INGEST_INTERVAL_SECONDS"))
    for src in (
        "ga4",
        "orders",
        "leads",
        "l0_pixel",
        "margin",
        "attribution",
        "facebook_organic",
    ):
        latest = db_get_latest_marketing_raw_ingest(src)
        ts = latest.get("fetched_at") if latest else None
        print("ingest", src, ts, "status", (latest or {}).get("status"))

    o = dtl_ingest_fetched_at("orders")
    l = dtl_ingest_fetched_at("leads")
    w = worker_heartbeat_at()
    print("PIPELINE_orders", freshness_status("orders", o))
    print("PIPELINE_leads", freshness_status("leads", l))
    print("PIPELINE_worker", freshness_status("worker", w))
    print(
        "PIPELINE_ga4",
        freshness_status("ga4", rows[0].get("generated_at") if rows else None),
    )


if __name__ == "__main__":
    main()
