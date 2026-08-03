#!/usr/bin/env python3
"""Demand OS agent shells CLI — registry-backed · no live publish.

Thin CLI over agent.demand_os.agents.registry.dispatch. Mutating actions stay
dry-run by default (pass --apply to execute).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.demand_os.agents.registry import AGENT_REGISTRY, all_roles, dispatch  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Demand OS agent shells (registry)")
    p.add_argument("--role", required=True, choices=all_roles())
    p.add_argument("--action", default="status")
    p.add_argument("--apply", action="store_true", help="execute mutating action (default dry-run)")
    p.add_argument("--icp-role", default="", dest="icp_role")
    p.add_argument("--hook", default="")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--channel", default="tiktok")
    p.add_argument("--asset-id", default="", dest="asset_id")
    p.add_argument("--label", default="")
    args = p.parse_args(argv)

    spec = AGENT_REGISTRY[args.role]
    act = (args.action or "status").strip().lower()
    kwargs: dict = {
        "limit": args.limit,
        "icp_role": args.icp_role or None,
        "hook": args.hook or None,
        "channel": args.channel,
        "asset_id": args.asset_id or None,
        "label": args.label,
    }
    if act in spec["mutating_actions"]:
        kwargs["dry_run"] = not args.apply

    out = dispatch(args.role, action=act, **kwargs)
    print(json.dumps(out, ensure_ascii=True, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
