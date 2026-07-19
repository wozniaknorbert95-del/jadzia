#!/usr/bin/env python3
"""Propose cutover preflight — evidence + GO ticket (does NOT flip MB_MODE)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="MB propose cutover preflight")
    parser.add_argument("--window-days", type=int, default=14)
    parser.add_argument(
        "--ticket",
        action="store_true",
        help="Print only go_ticket line",
    )
    parser.add_argument("--tip", default=None, help="Override git tip in ticket")
    args = parser.parse_args()

    from agent.marketing.propose_preflight import run_propose_preflight

    out = run_propose_preflight(window_days=args.window_days, tip=args.tip)
    if args.ticket:
        print(out.get("go_ticket") or "")
    else:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out.get("verdict") == "READY_FOR_GO" else 1


if __name__ == "__main__":
    raise SystemExit(main())
