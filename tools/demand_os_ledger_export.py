#!/usr/bin/env python3
"""K13 ledger export from SQLite attribution — dry-run default."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.demand_os.ledger_export import export_ledger  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Export LEDGER.csv from SQLite attribution")
    p.add_argument("--set-now", default="")
    p.add_argument("--apply", action="store_true", help="Write LEDGER.csv (default dry-run)")
    args = p.parse_args()
    set_now = Path(args.set_now) if args.set_now else None
    result = export_ledger(set_now=set_now, dry_run=not args.apply)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
