#!/usr/bin/env python3
"""Build a PII-free REV-R0-02 reconciliation report; writes require an explicit flag."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

from agent.revenue.reconciliation import (
    apply_unpersisted_classifications,
    build_reconciliation_report,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "jadzia.db"


def _load_ga4_transaction_ids(path: Path | None) -> list[str] | None:
    if path is None:
        return None
    payload: Any = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [str(item) for item in payload]
    if isinstance(payload, dict) and isinstance(payload.get("transaction_ids"), list):
        return [str(item) for item in payload["transaction_ids"]]
    raise ValueError("GA4 JSON must be a list or {'transaction_ids': [...]}")


def _read_only_connection(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _writable_connection(path: Path) -> sqlite3.Connection:
    import agent.db as db

    if hasattr(db._local, "conn") and db._local.conn:
        db._local.conn.close()
        db._local.conn = None
    db.DB_PATH = str(path)
    return db.get_connection()


def _emit(report: dict[str, Any], output: Path | None) -> None:
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if output:
        output.write_text(rendered + "\n", encoding="utf-8")
        return
    sys.stdout.write(rendered + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--ga4-transactions", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--apply-classifications",
        action="store_true",
        help="Append proposed classifications; existing decisions are never overwritten.",
    )
    args = parser.parse_args()

    if not args.db.exists():
        parser.error(f"database does not exist: {args.db}")

    ga4_ids = _load_ga4_transaction_ids(args.ga4_transactions)
    if args.apply_classifications:
        conn = _writable_connection(args.db)
        report = build_reconciliation_report(conn, ga4_ids)
        apply_result = apply_unpersisted_classifications(report)
        report = build_reconciliation_report(conn, ga4_ids)
        report["mode"] = "classifications_applied"
        report["apply_result"] = apply_result
    else:
        conn = _read_only_connection(args.db)
        report = build_reconciliation_report(conn, ga4_ids)

    _emit(report, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
