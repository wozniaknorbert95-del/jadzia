#!/usr/bin/env python3
"""Locate legacy INT-004 E2E leads without deleting revenue history.

Usage:
  PYTHONPATH=. python deployment/cleanup-e2e-hot-leads.py --dry-run

Destructive apply was disabled by REV-R0-02. Use:
  PYTHONPATH=. python scripts/revenue_reconcile.py --apply-classifications

Match (email LIKE):
  deploy02-%
  int004-e2e-%
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
DEFAULT_DB = _root / "data" / "jadzia.db"

EMAIL_PATTERNS = (
    "deploy02-%",
    "int004-e2e-%",
)


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def find_e2e_leads(conn: sqlite3.Connection) -> list[dict]:
    clauses = " OR ".join(["lower(email) LIKE lower(?)" for _ in EMAIL_PATTERNS])
    sql = f"""
        SELECT id, email, name, source, game_score, created_at
        FROM leads
        WHERE {clauses}
        ORDER BY id ASC
    """
    rows = conn.execute(sql, EMAIL_PATTERNS).fetchall()
    return [dict(r) for r in rows]


def delete_leads(conn: sqlite3.Connection, ids: list[int]) -> int:
    """Block the legacy destructive operation; retained only for explicit failure."""
    del conn, ids
    raise RuntimeError(
        "Revenue history deletion is disabled; use revenue_reconcile.py classifications"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not args.db.exists():
        print(json.dumps({"status": "error", "message": f"missing db {args.db}"}))
        return 1

    conn = _connect(args.db)
    matches = find_e2e_leads(conn)
    payload = {
        "status": "dry_run" if args.dry_run else "blocked",
        "db": str(args.db),
        "match_count": len(matches),
        "leads": matches,
    }

    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    payload["deleted"] = 0
    payload["message"] = (
        "Deletion disabled by REV-R0-02; use scripts/revenue_reconcile.py "
        "--apply-classifications"
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
