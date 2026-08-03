#!/usr/bin/env python3
"""Demand OS Hub — Growth Lead control plane (OS TARGET §E · §F · §G · §M).

No network. No VPS. Marketing HITL is OUT of this CLI.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.demand_os.a2a_bus import (  # noqa: E402
    HANDOFF_TYPES,
    ack_handoff,
    emit_handoff,
    list_handoffs,
)
from agent.demand_os.memory import (  # noqa: E402
    load_memory,
    set_semantic_icp,
    sync_episodic_from_ledger,
)
from agent.demand_os.commander_status import build_demand_os_status  # noqa: E402
from agent.demand_os.desk_contract import format_desk_pretty  # noqa: E402
from agent.demand_os.observability import build_screen, money_check  # noqa: E402
from agent.demand_os.starts_ingest import (  # noqa: E402
    ingest_fixture_csv,
    ingest_row,
    write_sample_fixture,
)
from agent.demand_os.audit_log import append_audit, list_audit  # noqa: E402
from agent.demand_os.connectors.engage import comment_on_target  # noqa: E402
from agent.demand_os.db_utm import (  # noqa: E402
    sync_paid_from_ops_bus,
    sync_wizard_starts_from_ops_bus,
)
from agent.demand_os.design_wizard import check_design_lead  # noqa: E402
from agent.demand_os.doctor import run_doctor  # noqa: E402
from agent.demand_os.fatigue import fatigue_check  # noqa: E402
from agent.demand_os.ledger import ensure_today_row, ledger_summary  # noqa: E402
from agent.demand_os.marketing_mode import resolve_marketing_mode  # noqa: E402
from agent.demand_os.stl_monitor import stl_report  # noqa: E402
from agent.demand_os.utm_lock import build_wizard_utm  # noqa: E402
from agent.demand_os.week_ritual import go_day_ready, week_plan  # noqa: E402
from agent.demand_os.weekly_tune import weekly_success_report  # noqa: E402
from agent.demand_os.widget_leads import sync_hot_leads_to_a2a  # noqa: E402


def _print(obj: object) -> None:
    print(json.dumps(obj, ensure_ascii=True, indent=2))


def _hub_auth_gate(cmd: str) -> dict | None:
    """Optional CLI RBAC: set DEMAND_OS_ROLE=viewer|delegat|dowodca."""
    from agent.demand_os.rbac import classify_hub_cmd, can_act, can_read

    role = (os.getenv("DEMAND_OS_ROLE") or "").strip().lower()
    if not role:
        return None
    auth = {"role": role, "sub": f"cli:{role}"}
    kind = classify_hub_cmd(cmd)
    if kind == "act" and not can_act(auth):
        return {"ok": False, "error": f"DEMAND_OS_ROLE={role} missing demand_os:act", "cmd": cmd}
    if kind == "read" and not can_read(auth):
        return {"ok": False, "error": f"DEMAND_OS_ROLE={role} missing demand_os:read", "cmd": cmd}
    return None


def cmd_status(args: argparse.Namespace) -> int:
    """Desk v2.1 status (same builder as API). --screen-only = legacy screen."""
    if getattr(args, "screen_only", False):
        _print(build_screen().to_dict())
        return 0
    st = build_demand_os_status(with_full_doctor=bool(getattr(args, "with_doctor", False)))
    if getattr(args, "desk", False):
        text = format_desk_pretty(st)
        try:
            print(text)
        except UnicodeEncodeError:
            sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
        return 0
    _print(st)
    return 0


def cmd_money_check(_: argparse.Namespace) -> int:
    _print(money_check())
    return 0


def cmd_doctor(_: argparse.Namespace) -> int:
    report = run_doctor()
    _print(report.to_dict())
    return 0 if report.ok else 1


def cmd_owner_verify(_: argparse.Namespace) -> int:
    """Delegate to tools/demand_os_owner_verify.py (exit 0 = green)."""
    import subprocess

    script = ROOT / "tools" / "demand_os_owner_verify.py"
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    env.setdefault("DEMAND_OS_SET_NOW", "data/demand-os/set-now-sanitized")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(ROOT),
        env=env,
        timeout=600,
    )
    return int(proc.returncode)


def cmd_ingest(args: argparse.Namespace) -> int:
    if args.fixture:
        path = Path(args.fixture)
        if args.write_sample:
            write_sample_fixture(path)
        result = ingest_fixture_csv(path)
        _print(result)
        return 0 if result.get("ok") else 1
    try:
        rec = ingest_row(
            utm_link=args.utm,
            event_type=args.type,
            asset_id=args.asset_id or None,
            count=args.count,
        )
    except ValueError as exc:
        _print({"ok": False, "error": str(exc)})
        return 1
    _print(rec)
    return 0


def cmd_weekly(_: argparse.Namespace) -> int:
    _print(weekly_success_report())
    return 0


def cmd_sync_db(args: argparse.Namespace) -> int:
    result = sync_wizard_starts_from_ops_bus(
        limit=args.limit,
        dry_run=args.dry_run,
    )
    _print(result)
    return 0 if result.get("ok") else 1


def cmd_sync_leads(args: argparse.Namespace) -> int:
    result = sync_hot_leads_to_a2a(limit=args.limit, dry_run=args.dry_run)
    _print(result)
    return 0 if result.get("ok") else 1


def cmd_sync_paid(args: argparse.Namespace) -> int:
    result = sync_paid_from_ops_bus(limit=args.limit, dry_run=args.dry_run)
    _print(result)
    return 0 if result.get("ok") else 1


def cmd_a2a_emit(args: argparse.Namespace) -> int:
    payload = {}
    if args.payload_json:
        payload = json.loads(args.payload_json)
    rec = emit_handoff(
        args.type,
        asset_id=args.asset_id or None,
        from_agent=args.from_agent,
        to_agent=args.to_agent or "",
        payload=payload,
    )
    _print(rec)
    return 0


def cmd_a2a_ack(args: argparse.Namespace) -> int:
    rec = ack_handoff(args.id)
    _print(rec)
    return 0 if rec.get("sla_ok") else 2


def cmd_a2a_list(args: argparse.Namespace) -> int:
    rows = list_handoffs(
        handoff_type=args.type or None,
        status=args.status or None,
    )
    _print({"count": len(rows), "handoffs": rows})
    return 0


def cmd_memory_show(_: argparse.Namespace) -> int:
    _print(load_memory())
    return 0


def cmd_memory_sync(args: argparse.Namespace) -> int:
    store = sync_episodic_from_ledger(weekly_improvement=args.improvement or "")
    _print(store)
    return 0


def cmd_memory_icp(args: argparse.Namespace) -> int:
    store = set_semantic_icp(args.role, args.hook)
    _print(store)
    return 0


def cmd_ledger(args: argparse.Namespace) -> int:
    if args.ensure_today:
        _print(ensure_today_row(dry_run=args.dry_run))
        return 0
    _print(ledger_summary())
    return 0


def cmd_stl(_: argparse.Namespace) -> int:
    _print(stl_report())
    return 0


def cmd_fatigue(args: argparse.Namespace) -> int:
    _print(fatigue_check(args.asset_id))
    return 0


def cmd_week(args: argparse.Namespace) -> int:
    _print(week_plan(day=args.day or ""))
    return 0


def cmd_go_ready(_: argparse.Namespace) -> int:
    report = go_day_ready()
    append_audit("go_day_ready", detail={"score": report.get("score")})
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_design_check(args: argparse.Namespace) -> int:
    out = check_design_lead(
        message=args.message,
        wizard_url=args.wizard_url,
        lead_id=args.lead_id,
        hours_since_mockup=args.hours,
    )
    _print(out)
    return 0 if out.get("ok") else 1


def cmd_audit(args: argparse.Namespace) -> int:
    if args.action:
        _print(append_audit(args.action, actor=args.actor, detail={"note": args.note}))
        return 0
    _print(list_audit(limit=args.limit))
    return 0


def cmd_engage_dry(args: argparse.Namespace) -> int:
    """Always dry_run — never live comment from hub."""
    from agent.demand_os.connectors.allowlist import require_engage_target

    marketing = resolve_marketing_mode()
    try:
        target = require_engage_target(args.target_id)
    except Exception as exc:
        _print({"ok": False, "error": str(exc)[:300], "marketing": marketing})
        return 1
    channel = target.platform if target.platform in ("tiktok", "facebook", "blog", "whatsapp") else "facebook"
    utm = args.utm or build_wizard_utm(channel, args.icp_role, args.asset_id)
    role = args.icp_role
    text = args.text or (
        f"Herkenbaar voor {role} — witte bus, opdrachtgever ziet je niet. "
        f"Start wizard: {utm}"
    )
    try:
        out = comment_on_target(
            args.target_id,
            text,
            mode="mock",
            dry_run=True,
            asset_id=args.asset_id,
            icp_role=role,
        )
    except Exception as exc:
        _print({"ok": False, "error": str(exc)[:300], "marketing": marketing})
        return 1
    out["marketing"] = marketing
    out["live"] = False
    _print(out)
    return 0 if out.get("ok") else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Demand OS Hub — control plane")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("status", help="Demand Desk v2.1 status (API parity)")
    s.add_argument(
        "--screen-only",
        action="store_true",
        help="legacy ObservabilityScreen dump only",
    )
    s.add_argument(
        "--desk",
        action="store_true",
        help="pretty PL A0-F text (nice-to-have)",
    )
    s.add_argument(
        "--with-doctor",
        action="store_true",
        help="run full doctor for footer.doctor_ok (slow)",
    )
    s.set_defaults(func=cmd_status)

    m = sub.add_parser("money-check", help="Pon Money Check slice")
    m.set_defaults(func=cmd_money_check)

    d = sub.add_parser("doctor", help="PROGRAM SEAL integrity check")
    d.set_defaults(func=cmd_doctor)

    ov = sub.add_parser(
        "owner-verify",
        help="One-shot owner pack (doctor + pointers + pytest demand_os + footer)",
    )
    ov.set_defaults(func=cmd_owner_verify)

    ing = sub.add_parser("ingest", help="Ingest wizard_start/paid (fixture or row)")
    ing.add_argument("--fixture", default="")
    ing.add_argument("--write-sample", action="store_true")
    ing.add_argument("--utm", default="")
    ing.add_argument("--type", default="wizard_start", choices=["wizard_start", "paid"])
    ing.add_argument("--asset-id", default="", dest="asset_id")
    ing.add_argument("--count", type=int, default=1)
    ing.set_defaults(func=cmd_ingest)

    w = sub.add_parser("weekly", help="Success tune — 1 improvement, no live publish CTA")
    w.set_defaults(func=cmd_weekly)

    sd = sub.add_parser("sync-db", help="ops_bus wizard_started → growth_events")
    sd.add_argument("--limit", type=int, default=50)
    sd.add_argument("--dry-run", action="store_true")
    sd.set_defaults(func=cmd_sync_db)

    sl = sub.add_parser("sync-leads", help="hot leads → A2A lead_hot")
    sl.add_argument("--limit", type=int, default=10)
    sl.add_argument("--dry-run", action="store_true")
    sl.set_defaults(func=cmd_sync_leads)

    sp = sub.add_parser("sync-paid", help="ops_bus order_created → paid events")
    sp.add_argument("--limit", type=int, default=50)
    sp.add_argument("--dry-run", action="store_true")
    sp.set_defaults(func=cmd_sync_paid)

    a = sub.add_parser("a2a", help="A2A bus")
    asub = a.add_subparsers(dest="a2a_cmd", required=True)
    ae = asub.add_parser("emit")
    ae.add_argument("--type", required=True, choices=sorted(HANDOFF_TYPES))
    ae.add_argument("--asset-id", default="", dest="asset_id")
    ae.add_argument("--from-agent", default="Growth_Lead", dest="from_agent")
    ae.add_argument("--to-agent", default="", dest="to_agent")
    ae.add_argument("--payload-json", default="", dest="payload_json")
    ae.set_defaults(func=cmd_a2a_emit)
    aa = asub.add_parser("ack")
    aa.add_argument("--id", required=True)
    aa.set_defaults(func=cmd_a2a_ack)
    al = asub.add_parser("list")
    al.add_argument("--type", default="")
    al.add_argument("--status", default="")
    al.set_defaults(func=cmd_a2a_list)

    mem = sub.add_parser("memory", help="OS §F memory layers")
    msub = mem.add_subparsers(dest="mem_cmd", required=True)
    ms = msub.add_parser("show")
    ms.set_defaults(func=cmd_memory_show)
    my = msub.add_parser("sync")
    my.add_argument("--improvement", default="")
    my.set_defaults(func=cmd_memory_sync)
    mi = msub.add_parser("icp")
    mi.add_argument("--role", required=True)
    mi.add_argument("--hook", required=True)
    mi.set_defaults(func=cmd_memory_icp)

    led = sub.add_parser("ledger", help="OS C.7 ledger summary / hygiene row")
    led.add_argument("--ensure-today", action="store_true")
    led.add_argument("--dry-run", action="store_true")
    led.set_defaults(func=cmd_ledger)

    stl = sub.add_parser("stl", help="Speed-to-lead SLA on A2A hot")
    stl.set_defaults(func=cmd_stl)

    fat = sub.add_parser("fatigue", help="B.4 creative fatigue check")
    fat.add_argument("--asset-id", required=True, dest="asset_id")
    fat.set_defaults(func=cmd_fatigue)

    wk = sub.add_parser("week", help="OS §K day ritual")
    wk.add_argument("--day", default="", help="pon|wt|sr|czw|pt")
    wk.set_defaults(func=cmd_week)

    gr = sub.add_parser("go-ready", help="Organic GO-day tool readiness score")
    gr.set_defaults(func=cmd_go_ready)

    dc = sub.add_parser("design-check", help="Design Agent dual-cash → Wizard")
    dc.add_argument("--message", default="")
    dc.add_argument("--wizard-url", default="", dest="wizard_url")
    dc.add_argument("--lead-id", default="design_lead", dest="lead_id")
    dc.add_argument("--hours", type=float, default=None)
    dc.set_defaults(func=cmd_design_check)

    au = sub.add_parser("audit", help="Control plane audit log")
    au.add_argument("--action", default="")
    au.add_argument("--actor", default="agent")
    au.add_argument("--note", default="")
    au.add_argument("--limit", type=int, default=50)
    au.set_defaults(func=cmd_audit)

    eg = sub.add_parser("engage-dry", help="Mock comment dry-run (never live)")
    eg.add_argument("--target-id", required=True, dest="target_id")
    eg.add_argument("--text", default="")
    eg.add_argument("--utm", default="")
    eg.add_argument("--asset-id", default="engage_dry", dest="asset_id")
    eg.add_argument("--icp-role", default="installateur", dest="icp_role")
    eg.set_defaults(func=cmd_engage_dry)

    args = p.parse_args(argv)
    cmd = args.cmd or ""
    if cmd == "memory" and getattr(args, "mem_cmd", None) in ("icp", "sync"):
        cmd = f"memory-{args.mem_cmd}"
    elif cmd == "a2a" and getattr(args, "a2a_cmd", None) in ("emit", "ack"):
        cmd = f"a2a-{args.a2a_cmd}"
    elif cmd == "ledger" and getattr(args, "ensure_today", False):
        cmd = "ledger-ensure"
    elif cmd == "audit" and getattr(args, "action", None):
        cmd = "audit-write"
    gate = _hub_auth_gate(cmd)
    if gate is not None:
        _print(gate)
        return 1
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
