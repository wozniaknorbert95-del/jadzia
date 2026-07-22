"""Local RCA helper for OPS-AGENT-SLA-01 — agent_state vs DTL clocks."""

from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "jadzia.db"

DEFAULTS = [
    ("marketing", 3600),
    ("marketing_brain", 3600),
    ("analytics", 7200),
    ("sales", 1800),
    ("operations", 1800),
    ("design", 86400),
]


def parse_ts(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def sla_ok(last_run_at, interval_s):
    dt = parse_ts(last_run_at)
    if not dt:
        return False
    age = (datetime.now(timezone.utc) - dt).total_seconds()
    return age <= interval_s * 2


def main() -> int:
    if not DB.exists():
        print("NO_DB", DB)
        return 1
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    print("tables_has_agent_state", "commander_agent_state" in tables)
    states = {}
    if "commander_agent_state" in tables:
        for r in con.execute("SELECT * FROM commander_agent_state"):
            states[r["agent_id"]] = dict(r)
    print("=== agent_state rows ===")
    for aid, interval in DEFAULTS:
        row = states.get(aid, {})
        last = row.get("last_run_at")
        iv = row.get("expected_interval_seconds") or interval
        ok = sla_ok(last, iv)
        age = None
        dt = parse_ts(last)
        if dt:
            age = int((datetime.now(timezone.utc) - dt).total_seconds())
        print(
            f"{aid}: last={last!r} interval={iv} age_s={age} sla_ok={ok} status={row.get('status')}"
        )
    print("=== latest DTL ingest ===")
    if "marketing_raw_ingest" in tables:
        for src in ("ga4", "orders", "leads", "facebook_organic"):
            r = con.execute(
                "SELECT source, fetched_at FROM marketing_raw_ingest "
                "WHERE source=? ORDER BY fetched_at DESC LIMIT 1",
                (src,),
            ).fetchone()
            print(src, dict(r) if r else None)
    else:
        print("no marketing_raw_ingest")
    bad = sum(
        1
        for aid, interval in DEFAULTS
        if not sla_ok(
            states.get(aid, {}).get("last_run_at"),
            states.get(aid, {}).get("expected_interval_seconds") or interval,
        )
    )
    print("SLA_BAD_COUNT", bad)
    return 0


if __name__ == "__main__":
    sys.exit(main())
