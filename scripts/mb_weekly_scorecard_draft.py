#!/usr/bin/env python3
"""Build Marketing OS weekly scorecard draft from DTL facts (no Ads invent)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="MB weekly scorecard draft")
    parser.add_argument("--campaign", default=None)
    parser.add_argument("--iso-week", default=None)
    parser.add_argument(
        "--text",
        action="store_true",
        help="Print PL text only",
    )
    parser.add_argument(
        "--notify",
        action="store_true",
        help="Also send draft to Telegram admin chat",
    )
    args = parser.parse_args()

    from agent.marketing.weekly_scorecard import (
        build_weekly_scorecard_draft,
        send_weekly_scorecard_telegram,
    )

    kwargs = {}
    if args.campaign:
        kwargs["campaign"] = args.campaign
    if args.iso_week:
        kwargs["iso_week"] = args.iso_week
    out = build_weekly_scorecard_draft(**kwargs)
    if args.notify:
        push = send_weekly_scorecard_telegram(out)
        out["telegram"] = push
    if args.text:
        print(out.get("text_pl") or "")
    else:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
