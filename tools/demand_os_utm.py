#!/usr/bin/env python3
"""CLI: Demand OS UTM Lock + ledger audit (F1)."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.demand_os.growth_events import append_growth_event
from agent.demand_os.utm_lock import build_wizard_utm, validate_utm_url

LEDGER = ROOT / "docs/ops/demand-os/set-now/LEDGER.csv"


def cmd_build(args: argparse.Namespace) -> int:
    url = build_wizard_utm(args.channel, args.role, args.asset_id, medium=args.medium)
    append_growth_event(
        "cta_issued",
        asset_id=args.asset_id,
        channel=args.channel,
        utm_link=url,
        ok=True,
        notes="cli build",
    )
    print(url)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    result = validate_utm_url(args.url)
    et = "cta_validated" if result["ok"] else "cta_rejected"
    append_growth_event(
        et,
        asset_id=(result.get("parts") or {}).get("asset_id"),
        channel=(result.get("parts") or {}).get("channel"),
        utm_link=args.url,
        ok=result["ok"],
        errors=result["errors"],
        notes="cli validate",
    )
    if result["ok"]:
        print("PASS")
        return 0
    print("FAIL:", "; ".join(result["errors"]))
    return 1


def _audit_csv(path: Path, *, min_ok: int = 0) -> int:
    if not path.is_file():
        print(f"FAIL: missing {path}")
        return 2
    checked = 0
    fails = 0
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            link = (row.get("utm_link") or "").strip()
            if not link:
                continue
            checked += 1
            result = validate_utm_url(link)
            asset = row.get("asset_id") or "?"
            if result["ok"]:
                print(f"PASS {asset}")
            else:
                fails += 1
                print(f"FAIL {asset}: {'; '.join(result['errors'])}")
    print(f"summary checked={checked} fail={fails} file={path.name}")
    if checked < 1:
        return 2
    if min_ok and checked < min_ok:
        print(f"FAIL: need ≥{min_ok} links, got {checked}")
        return 2
    return 0 if fails == 0 else 1


def cmd_audit_ledger(args: argparse.Namespace) -> int:
    path = Path(args.ledger) if args.ledger else LEDGER
    return _audit_csv(path)


def cmd_audit_sample(args: argparse.Namespace) -> int:
    path = (
        Path(args.sample)
        if args.sample
        else ROOT / "docs/ops/demand-os/set-now/UTM-AUDIT-SAMPLE.csv"
    )
    return _audit_csv(path, min_ok=10)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Demand OS UTM Lock CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="Build canonical Wizard UTM URL")
    b.add_argument("--channel", required=True)
    b.add_argument("--role", required=True)
    b.add_argument("--asset-id", required=True, dest="asset_id")
    b.add_argument("--medium", default="organic")
    b.set_defaults(func=cmd_build)

    v = sub.add_parser("validate", help="Validate a CTA URL")
    v.add_argument("url")
    v.set_defaults(func=cmd_validate)

    a = sub.add_parser("audit-ledger", help="Audit LEDGER.csv utm_link column")
    a.add_argument("--ledger", default="")
    a.set_defaults(func=cmd_audit_ledger)

    s = sub.add_parser(
        "audit-sample",
        help="Audit UTM-AUDIT-SAMPLE.csv (≥10 growth CTAs)",
    )
    s.add_argument("--sample", default="")
    s.set_defaults(func=cmd_audit_sample)

    args = p.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
