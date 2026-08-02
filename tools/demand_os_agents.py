#!/usr/bin/env python3
"""Demand OS agent shells CLI — Wave1–3 · no live publish."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.demand_os.agents.wave1 import WAVE1_ROLES, run_agent  # noqa: E402
from agent.demand_os.agents.wave2 import run_wave2  # noqa: E402
from agent.demand_os.agents.wave3 import WAVE3_ROLES, run_wave3  # noqa: E402

ALL_ROLES = sorted(WAVE1_ROLES | {"cf", "fb"} | WAVE3_ROLES)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Demand OS agent shells")
    p.add_argument("--role", required=True, choices=ALL_ROLES)
    p.add_argument("--action", default="status")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--icp-role", default="", dest="icp_role")
    p.add_argument("--hook", default="")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--channel", default="tiktok")
    p.add_argument("--asset-id", default="", dest="asset_id")
    p.add_argument("--label", default="")
    args = p.parse_args(argv)

    if args.role in WAVE1_ROLES:
        out = run_agent(
            args.role,
            action=args.action,
            dry_run=args.dry_run,
            icp_role=args.icp_role or None,
            hook=args.hook or None,
            limit=args.limit,
        )
    elif args.role in WAVE3_ROLES:
        out = run_wave3(
            args.role,
            action=args.action,
            limit=args.limit,
            icp_role=args.icp_role or "installateur",
            asset_id=args.asset_id or None,
        )
    else:
        out = run_wave2(
            args.role,
            action=args.action,
            dry_run=args.dry_run,
            channel=args.channel,
            asset_id=args.asset_id or None,
            limit=args.limit,
            label=args.label,
        )
    print(json.dumps(out, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
