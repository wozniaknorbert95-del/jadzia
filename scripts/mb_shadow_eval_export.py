#!/usr/bin/env python3
"""Export Marketing Brain shadow Evaluation Pack (JSON or CSV)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running from repo root
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="MB shadow eval-pack export")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--window-days", type=int, default=7)
    parser.add_argument(
        "--dump",
        action="store_true",
        help="v1 raw dump (no stratification)",
    )
    parser.add_argument("--format", choices=("json", "csv"), default="json")
    parser.add_argument("-o", "--output", help="Write to file (default stdout)")
    args = parser.parse_args()

    from agent.marketing.shadow_eval import (
        build_eval_pack,
        eval_pack_to_csv,
        eval_pack_to_json,
    )

    pack = build_eval_pack(
        limit=args.limit,
        window_days=args.window_days,
        stratified=not args.dump,
    )
    text = (
        eval_pack_to_csv(pack)
        if args.format == "csv"
        else eval_pack_to_json(pack)
    )
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(
            f"wrote {args.output} n={pack.get('n')} ver={pack.get('pack_version')}",
            file=sys.stderr,
        )
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
