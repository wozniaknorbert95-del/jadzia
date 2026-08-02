#!/usr/bin/env python3
"""Demand OS F3 CLI — allowlist engage (read/comment) + anti-spam."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.demand_os.connectors.allowlist import (
    AllowlistError,
    list_active_targets,
    list_pending_join,
    load_allowlist,
    set_target_status,
)
from agent.demand_os.connectors.anti_spam import AntiSpamError
from agent.demand_os.connectors.engage import comment_on_target, read_target
from agent.demand_os.utm_lock import build_wizard_utm


def cmd_allowlist(_: argparse.Namespace) -> int:
    data = load_allowlist()
    out = {
        "max_groups": data["max_groups"],
        "research": data.get("research"),
        "active": [t.__dict__ for t in list_active_targets()],
        "pending_join": [t.__dict__ for t in list_pending_join()],
        "all": [t.__dict__ for t in data["targets"]],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_activate(args: argparse.Namespace) -> int:
    try:
        t = set_target_status(args.target_id, "active")
    except (AllowlistError, ValueError) as exc:
        print(f"DENY: {exc}")
        return 1
    print(json.dumps(t.__dict__, ensure_ascii=False, indent=2))
    return 0


def cmd_read(args: argparse.Namespace) -> int:
    try:
        result = read_target(args.target_id, mode=args.mode)
    except AllowlistError as exc:
        print(f"DENY: {exc}")
        return 1
    print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    return 0 if result.ok else 1


def cmd_comment(args: argparse.Namespace) -> int:
    text = args.text
    if args.with_utm:
        url = build_wizard_utm(
            "tiktok" if args.target_id.startswith("tt") else "facebook",
            args.role,
            args.asset_id,
        )
        text = f"{text.rstrip()}\n{url}"
    try:
        result = comment_on_target(
            args.target_id,
            text,
            mode=args.mode,
            dry_run=not args.live,
            asset_id=args.asset_id,
            icp_role=args.role,
        )
    except (AllowlistError, AntiSpamError, ValueError) as exc:
        print(f"DENY: {exc}")
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


def cmd_smoke(_: argparse.Namespace) -> int:
    """DoD smoke: 1 read + 1 comment on allowlisted active targets."""
    read_res = read_target("fb_own_page", mode="mock")
    if not read_res.ok:
        print("SMOKE FAIL read", read_res.error)
        return 1
    print("SMOKE read PASS", read_res.target_id, "items", len(read_res.items))

    url = build_wizard_utm("tiktok", "installateur", "tt_engage_smoke_01")
    body = (
        "Goede tip voor installateurs: maak je bus herkenbaar.\n"
        f"Start in de Wizard: {url}"
    )
    try:
        cmt = comment_on_target(
            "tt_own",
            body,
            mode="mock",
            dry_run=True,
            asset_id="tt_engage_smoke_01",
            icp_role="installateur",
        )
    except Exception as exc:
        print("SMOKE FAIL comment", exc)
        return 1
    if not cmt.get("ok"):
        print("SMOKE FAIL comment", cmt)
        return 1
    print("SMOKE comment PASS", cmt["comment"].get("comment_id"))
    print("SMOKE PASS")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Demand OS F3 connectors")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("allowlist", help="Show allowlist")
    a.set_defaults(func=cmd_allowlist)

    act = sub.add_parser("activate", help="Mark group active after Join")
    act.add_argument("--target-id", required=True, dest="target_id")
    act.set_defaults(func=cmd_activate)

    r = sub.add_parser("read", help="Read allowlisted target")
    r.add_argument("--target-id", required=True, dest="target_id")
    r.add_argument("--mode", default="mock", choices=["mock", "live"])
    r.set_defaults(func=cmd_read)

    c = sub.add_parser("comment", help="Comment on allowlisted target")
    c.add_argument("--target-id", required=True, dest="target_id")
    c.add_argument("--text", required=True)
    c.add_argument("--mode", default="mock", choices=["mock", "live"])
    c.add_argument("--live", action="store_true", help="request non-dry-run (still gated)")
    c.add_argument("--with-utm", action="store_true")
    c.add_argument("--role", default="installateur")
    c.add_argument("--asset-id", default="engage_reply", dest="asset_id")
    c.set_defaults(func=cmd_comment)

    s = sub.add_parser("smoke", help="1 read + 1 comment DoD smoke")
    s.set_defaults(func=cmd_smoke)

    args = p.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
