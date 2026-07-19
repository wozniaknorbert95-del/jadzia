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
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--format", choices=("json", "csv"), default="json")
    parser.add_argument("-o", "--output", help="Write to file (default stdout)")
    args = parser.parse_args()

    from agent.marketing.shadow_eval import (
        build_eval_pack,
        eval_pack_to_csv,
        eval_pack_to_json,
    )

    pack = build_eval_pack(limit=args.limit)
    text = (
        eval_pack_to_csv(pack)
        if args.format == "csv"
        else eval_pack_to_json(pack)
    )
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"wrote {args.output} count={pack.get('count')}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
