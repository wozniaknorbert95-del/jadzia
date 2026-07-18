"""Read-only legacy revenue reconciliation and explicit classification apply step."""

from __future__ import annotations

import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Iterable

from agent.revenue.classification import (
    ClassificationResult,
    canonical_order_id,
    classify_legacy_record,
)


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    ).fetchone()
    return row is not None


def _rows(conn: sqlite3.Connection, query: str) -> list[dict[str, Any]]:
    return [dict(row) for row in conn.execute(query).fetchall()]


def _latest_persisted(conn: sqlite3.Connection) -> dict[tuple[str, str], dict[str, Any]]:
    if not _table_exists(conn, "revenue_classification_events"):
        return {}
    rows = _rows(
        conn,
        """
        SELECT event.entity_type, event.entity_key, event.classification,
               event.reason_code, event.evidence_json, event.classified_by
        FROM revenue_classification_events AS event
        JOIN (
            SELECT entity_type, entity_key, MAX(id) AS latest_id
            FROM revenue_classification_events
            GROUP BY entity_type, entity_key
        ) AS latest ON latest.latest_id = event.id
        """,
    )
    return {(row["entity_type"], row["entity_key"]): row for row in rows}


def _legacy_entities(conn: sqlite3.Connection) -> list[tuple[str, str, dict[str, Any]]]:
    entities: list[tuple[str, str, dict[str, Any]]] = []
    if _table_exists(conn, "orders"):
        for row in _rows(
            conn,
            """
            SELECT order_id, status, total_gross, payment_id, customer_email,
                   created_at, updated_at, classification, classification_reason,
                   is_test, schema_version
            FROM orders
            ORDER BY id
            """,
        ):
            entities.append(("order", str(row["order_id"]), row))
    if _table_exists(conn, "leads"):
        for row in _rows(
            conn,
            """
            SELECT id, email, source, consent_status, created_at, updated_at
            FROM leads
            ORDER BY id
            """,
        ):
            entities.append(("lead", str(row["id"]), row))
    if _table_exists(conn, "portal_qual_leads"):
        for row in _rows(
            conn,
            """
            SELECT id, session_id, source, consent, created_at
            FROM portal_qual_leads
            ORDER BY id
            """,
        ):
            entities.append(("portal_qual_lead", str(row["id"]), row))
    return entities


def build_reconciliation_report(
    conn: sqlite3.Connection | None = None,
    ga4_transaction_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Build a PII-free report. This function never writes to SQLite."""
    if conn is None:
        from agent.db import get_connection

        conn = get_connection()
    conn.row_factory = sqlite3.Row

    persisted = _latest_persisted(conn)
    candidates: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    orders: list[dict[str, Any]] = []
    normalized_order_ids: dict[str, list[str]] = defaultdict(list)

    for entity_type, entity_key, row in _legacy_entities(conn):
        proposed = classify_legacy_record(entity_type, row)
        if entity_type == "order" and row.get("schema_version") == "int-002.v2":
            stored = str(row.get("classification") or "").strip().lower()
            if stored in {"real", "test", "unknown"}:
                proposed = ClassificationResult(
                    stored,
                    str(row.get("classification_reason") or "int002_consumer"),
                    {"schema_version": row.get("schema_version")},
                )
        current = persisted.get((entity_type, entity_key))
        classification = current["classification"] if current else proposed.classification
        reason_code = current["reason_code"] if current else proposed.reason_code
        counts[classification] += 1
        candidates.append(
            {
                "entity_type": entity_type,
                "entity_key": entity_key,
                "classification": classification,
                "reason_code": reason_code,
                "persisted": current is not None,
                "proposed_classification": proposed.classification,
                "proposed_reason_code": proposed.reason_code,
                "proposed_evidence": proposed.evidence,
            }
        )
        if entity_type == "order":
            normalized = canonical_order_id(entity_key)
            normalized_order_ids[normalized].append(entity_key)
            orders.append(
                {
                    "order_id": entity_key,
                    "canonical_order_id": normalized,
                    "classification": classification,
                    "reason_code": reason_code,
                    "kpi_paid_eligible": classification == "real",
                }
            )

    duplicates = [
        {"canonical_order_id": key, "source_order_ids": values}
        for key, values in sorted(normalized_order_ids.items())
        if len(values) > 1
    ]

    ga4_ids = None
    if ga4_transaction_ids is not None:
        ga4_ids = {canonical_order_id(item) for item in ga4_transaction_ids if str(item).strip()}
    jadzia_ids = {
        order["canonical_order_id"] for order in orders if order["classification"] != "test"
    }
    if ga4_ids is None:
        ga4_reconciliation: dict[str, Any] = {
            "status": "insufficient_evidence",
            "reason": "transaction_level_ga4_export_not_supplied",
        }
    else:
        matched = sorted(jadzia_ids & ga4_ids)
        missing_ga4 = sorted(jadzia_ids - ga4_ids)
        ga4_orphans = sorted(ga4_ids - jadzia_ids)
        ga4_reconciliation = {
            "status": "matched" if not missing_ga4 and not ga4_orphans else "gaps_found",
            "matched_order_ids": matched,
            "missing_ga4_order_ids": missing_ga4,
            "ga4_orphan_transaction_ids": ga4_orphans,
        }

    return {
        "contract_version": "revenue_event.v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "mode": "read_only",
        "history_preserved": True,
        "summary": {
            "entities_total": len(candidates),
            "classifications": {
                "real": counts["real"],
                "test": counts["test"],
                "unknown": counts["unknown"],
            },
            "paid_orders_kpi_eligible": sum(1 for order in orders if order["kpi_paid_eligible"]),
            "normalized_order_duplicates": len(duplicates),
        },
        "classification_candidates": candidates,
        "orders": orders,
        "normalized_order_duplicates": duplicates,
        "ga4_order_reconciliation": ga4_reconciliation,
        "funnel_reconciliation": {
            "status": "insufficient_evidence",
            "reason": "canonical_lead_and_funnel_event_ledger_not_implemented_until_REV_R1",
        },
    }


def apply_unpersisted_classifications(report: dict[str, Any]) -> dict[str, int]:
    """Persist proposed classifications once; never overwrite an existing decision."""
    from agent.db import db_record_revenue_classification

    inserted = 0
    skipped = 0
    for item in report["classification_candidates"]:
        if item["persisted"]:
            skipped += 1
            continue
        db_record_revenue_classification(
            entity_type=item["entity_type"],
            entity_key=item["entity_key"],
            classification=item["proposed_classification"],
            reason_code=item["proposed_reason_code"],
            evidence=item["proposed_evidence"],
        )
        inserted += 1
    return {"inserted": inserted, "skipped_existing": skipped}
