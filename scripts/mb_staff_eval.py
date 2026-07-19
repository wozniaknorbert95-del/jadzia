#!/usr/bin/env python3
"""Run staff-eval batch (score unscored shadow + optional Telegram PL summary)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="MB staff-eval batch")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--window-days", type=int, default=14)
    parser.add_argument(
        "--no-telegram",
        action="store_true",
        help="Score only, skip Telegram summary",
    )
    args = parser.parse_args()

    from agent.marketing.shadow_eval import run_staff_eval_batch

    out = run_staff_eval_batch(
        limit=args.limit,
        window_days=args.window_days,
        notify_telegram=not args.no_telegram,
    )
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
