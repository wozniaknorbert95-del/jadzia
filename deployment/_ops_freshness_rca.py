"""One-shot RCA for OPS-FRESHNESS-01 — run on VPS, no secrets printed."""
from __future__ import annotations

import os

from agent.commander.settings import get_settings
from agent.commander.sla import freshness_status
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
    print("order_updated", orders[0].get("updated_at") if orders else None)
    print("lead_updated", leads[0].get("updated_at") if leads else None)
    print("ga4_generated", rows[0].get("generated_at") if rows else None)
    print("dowodca_last_active", settings.get("dowodca_last_active_at"))
    print("DTL_INTERVAL", os.getenv("MARKETING_DTL_INGEST_INTERVAL_SECONDS"))
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
        ts = None
        if latest:
            ts = latest.get("fetched_at") or latest.get("created_at")
        print("ingest", src, ts, "status", (latest or {}).get("status"))
    print(
        "fresh_orders",
        freshness_status("orders", orders[0].get("updated_at") if orders else None),
    )
    print(
        "fresh_leads",
        freshness_status("leads", leads[0].get("updated_at") if leads else None),
    )
    print("fresh_worker", freshness_status("worker", settings.get("dowodca_last_active_at")))
    print(
        "fresh_ga4",
        freshness_status("ga4", rows[0].get("generated_at") if rows else None),
    )


if __name__ == "__main__":
    main()
