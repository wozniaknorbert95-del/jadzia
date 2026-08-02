#!/usr/bin/env python3
"""Demand OS F2 CLI — Validator gate + content_calendar (MCP tool surface)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.demand_os.content_calendar import (
    CalendarSlot,
    add_slot,
    assert_publish_allowed,
    list_slots,
    load_calendar,
    save_calendar,
    set_slot_status,
)
from agent.demand_os.publish_request import PublishRequest
from agent.demand_os.utm_lock import build_wizard_utm
from agent.demand_os.validator import ADS_FREEZE_UNTIL, evaluate_publish_request, rules_catalog


def cmd_rules(_: argparse.Namespace) -> int:
    for r in rules_catalog():
        print(r)
    print(f"ads_freeze_until={ADS_FREEZE_UNTIL.isoformat()}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    caption = args.caption
    if args.caption_file:
        caption = Path(args.caption_file).read_text(encoding="utf-8")
    utm = args.utm
    if not utm and args.content_type != "game_post":
        utm = build_wizard_utm(args.channel, args.role, args.asset_id)
    req = PublishRequest(
        asset_id=args.asset_id,
        channel=args.channel,
        icp_role=args.role,
        caption=caption or "",
        utm_link=utm or "",
        content_type=args.content_type,
        hero_is_hq=args.hero_hq,
        ads_boost=args.ads_boost,
        offerte_only=args.offerte_only,
    )
    as_of = date.fromisoformat(args.as_of) if args.as_of else None
    decision = evaluate_publish_request(
        req,
        as_of=as_of,
        log=not args.no_log,
        emit_events=not args.no_log,
    )
    print(json.dumps(decision.to_dict(), ensure_ascii=False, indent=2))
    if decision.ok and args.calendar_bind:
        cal = load_calendar()
        try:
            cal = set_slot_status(
                cal,
                asset_id=req.asset_id,
                status="validated",
                request_id=req.request_id,
                pass_token=decision.pass_token,
                notes=f"Val PASS {decision.decided_at}",
            )
        except KeyError:
            cal = add_slot(
                cal,
                CalendarSlot(
                    date=(args.slot_date or date.today().isoformat()),
                    channel=req.channel if req.channel in ("tiktok", "facebook", "blog") else "tiktok",
                    asset_id=req.asset_id,
                    status="validated",
                    request_id=req.request_id,
                    pass_token=decision.pass_token,
                    notes=f"Val PASS {decision.decided_at}",
                ),
            )
        save_calendar(cal)
        print("calendar: bound validated + pass_token")
    return 0 if decision.ok else 1


def cmd_calendar_list(args: argparse.Namespace) -> int:
    cal = load_calendar()
    rows = list_slots(cal, channel=args.channel or None, status=args.status or None)
    print(json.dumps({"week": cal.week, "slots": [s.__dict__ for s in rows]}, indent=2))
    return 0


def cmd_calendar_add(args: argparse.Namespace) -> int:
    cal = load_calendar()
    if not cal.week:
        cal.week = args.week or "2026-W32"
    cal = add_slot(
        cal,
        CalendarSlot(
            date=args.date,
            channel=args.channel,
            asset_id=args.asset_id,
            status=args.status,
            notes=args.notes or "",
        ),
    )
    save_calendar(cal)
    print("OK added", args.asset_id)
    return 0


def cmd_gate(args: argparse.Namespace) -> int:
    """Refuse publish unless calendar slot validated + token."""
    cal = load_calendar()
    try:
        assert_publish_allowed(cal, args.asset_id)
    except PermissionError as exc:
        print(f"GATE DENY: {exc}")
        return 1
    print(f"GATE ALLOW: {args.asset_id}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Demand OS F2 — Validator + calendar")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("rules", help="List C.5 rule IDs")
    r.set_defaults(func=cmd_rules)

    v = sub.add_parser("validate", help="Run Sniper Validator on publish_request")
    v.add_argument("--asset-id", required=True, dest="asset_id")
    v.add_argument("--channel", required=True)
    v.add_argument("--role", required=True)
    v.add_argument("--caption", default="")
    v.add_argument("--caption-file", default="")
    v.add_argument("--utm", default="")
    v.add_argument("--content-type", default="organic_post", dest="content_type")
    v.add_argument("--as-of", default="", help="YYYY-MM-DD for ads freeze")
    v.add_argument("--hero-hq", action="store_true", dest="hero_hq")
    v.add_argument("--ads-boost", action="store_true", dest="ads_boost")
    v.add_argument("--offerte-only", action="store_true", dest="offerte_only")
    v.add_argument("--no-log", action="store_true")
    v.add_argument("--calendar-bind", action="store_true")
    v.add_argument("--slot-date", default="")
    v.set_defaults(func=cmd_validate)

    c = sub.add_parser("calendar", help="content_calendar tools")
    csub = c.add_subparsers(dest="cal_cmd", required=True)
    cl = csub.add_parser("list")
    cl.add_argument("--channel", default="")
    cl.add_argument("--status", default="")
    cl.set_defaults(func=cmd_calendar_list)
    ca = csub.add_parser("add")
    ca.add_argument("--date", required=True)
    ca.add_argument("--channel", required=True)
    ca.add_argument("--asset-id", required=True, dest="asset_id")
    ca.add_argument("--status", default="planned")
    ca.add_argument("--week", default="")
    ca.add_argument("--notes", default="")
    ca.set_defaults(func=cmd_calendar_add)

    g = sub.add_parser("gate", help="Hard gate: validated + pass_token required")
    g.add_argument("--asset-id", required=True, dest="asset_id")
    g.set_defaults(func=cmd_gate)

    args = p.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
