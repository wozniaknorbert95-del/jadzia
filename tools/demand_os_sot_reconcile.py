#!/usr/bin/env python3
"""K5 dual SoT reconcile — dry-run by default."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.demand_os.sot_reconcile import reconcile_dual_sot  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Reconcile SQLite authority vs set-now files")
    p.add_argument("--set-now", default="", help="Override DEMAND_OS_SET_NOW path")
    p.add_argument("--apply", action="store_true", help="Reserved; reconcile is read-only")
    args = p.parse_args()
    set_now = Path(args.set_now) if args.set_now else None
    report = reconcile_dual_sot(set_now=set_now, dry_run=not args.apply)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
