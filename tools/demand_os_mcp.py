#!/usr/bin/env python3
"""Demand OS MCP facades CLI — OS §E (no fake HTTP server)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.demand_os.content_calendar import load_calendar  # noqa: E402
from agent.demand_os.ga4_adapter import (  # noqa: E402
    fetch_wizard_starts,
    fetch_wizard_starts_by_utm,
    pull_ga4_into_dtl,
)
from agent.demand_os.gdrive_cf import list_cf_assets  # noqa: E402
from agent.demand_os.publish_gate_bridge import check_publish_allowed  # noqa: E402
from agent.demand_os.widget_leads import (  # noqa: E402
    emit_hot_lead,
    list_hot_leads,
)


def _print(obj: object) -> None:
    print(json.dumps(obj, ensure_ascii=True, indent=2))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Demand OS MCP facades")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("ga4")
    g.add_argument("--days", type=int, default=7)
    g.set_defaults(func=lambda a: (_print(fetch_wizard_starts(days=a.days)), 0)[1])

    gu = sub.add_parser("ga4-utm")
    gu.add_argument("--days", type=int, default=7)
    gu.set_defaults(
        func=lambda a: (_print(fetch_wizard_starts_by_utm(days=a.days)), 0)[1]
    )

    gp = sub.add_parser("ga4-dtl")
    gp.add_argument("--days", type=int, default=7)
    gp.set_defaults(func=lambda a: (_print(pull_ga4_into_dtl(days=a.days)), 0)[1])

    d = sub.add_parser("gdrive")
    d.add_argument("--limit", type=int, default=5)
    d.set_defaults(func=lambda a: (_print(list_cf_assets(limit=a.limit)), 0)[1])

    cal = sub.add_parser("calendar")
    cal.set_defaults(
        func=lambda a: (_print({"ok": True, "mode": "content_calendar", **load_calendar().to_dict()}), 0)[1]
    )

    gate = sub.add_parser("publish-gate")
    gate.add_argument("--asset-id", required=True, dest="asset_id")
    gate.set_defaults(
        func=lambda a: (_print(check_publish_allowed(a.asset_id).to_dict()), 0)[1]
    )

    w = sub.add_parser("leads")
    w.add_argument("--limit", type=int, default=20)
    w.set_defaults(func=lambda a: (_print(list_hot_leads(limit=a.limit)), 0)[1])

    e = sub.add_parser("emit-lead")
    e.add_argument("--lead-id", required=True, dest="lead_id")
    e.add_argument("--wizard-url", default="", dest="wizard_url")
    e.set_defaults(
        func=lambda a: (
            _print(emit_hot_lead(lead_id=a.lead_id, wizard_url=a.wizard_url)),
            0,
        )[1]
    )

    args = p.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
