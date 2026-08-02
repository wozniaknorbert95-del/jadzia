"""Commander Demand OS status payload — Desk v2.1.1 contract (API + tests)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, Optional

from agent.demand_os.desk_contract import (
    CONTRACT_VERSION,
    build_desk_footer,
    build_hunt_queue,
    build_week_calendar,
    desk_state,
    detect_data_mode,
    dual_cash_report,
    iso_week_label,
    lightweight_doctor_ok,
    resolve_icp_week,
    resolve_robota_dnia,
    set_now_path,
    shells_line,
    starts_wow_delta,
    top_wizard_assets,
    validator_fail_display,
)
from agent.demand_os.observability import build_screen, money_check
from agent.demand_os.stl_monitor import stl_report
from agent.demand_os.week_ritual import go_day_ready

GATE = "DEMAND-OS-DESK-CONTRACT-00"
DESK = "Demand Desk v2.1"
MARKETING = "PARKED_LAST"


def build_demand_os_status(
    *,
    set_now: Optional[Path] = None,
    events_path: Optional[Path] = None,
    with_full_doctor: bool = False,
) -> Dict[str, Any]:
    screen = build_screen(set_now=set_now, events_path=events_path)
    mc = money_check(set_now=set_now, events_path=events_path)
    starts = int(mc.get("starts_utm") or 0)
    publish = int(mc.get("publish_count") or 0)
    go = go_day_ready()
    stl = stl_report()
    robota = resolve_robota_dnia(marketing=MARKETING)
    hunt = build_hunt_queue(set_now=set_now)
    dual = dual_cash_report(set_now=set_now)
    icp = resolve_icp_week(set_now=set_now)

    root = set_now or set_now_path()
    ledger_rows: list = []
    led = root / "LEDGER.csv"
    if led.is_file():
        with led.open(encoding="utf-8", newline="") as fh:
            ledger_rows = list(csv.DictReader(fh))

    dm = detect_data_mode(
        set_now=set_now,
        events_path=events_path,
        ledger_rows=ledger_rows,
    )
    wow = starts_wow_delta(ledger_rows)
    top5 = top_wizard_assets(screen.wizard_starts_by_utm or {})

    screen_dict = screen.to_dict()
    screen_dict["hunt_queue"] = hunt
    screen_dict["top_wizard_assets"] = top5
    screen_dict["top_wizard_note"] = (
        "" if top5 else "brak starts UTM — pusta lista (nie fixture fake)"
    )
    screen_dict["hitl_queue"] = screen_dict.get("hitl_queue") or []

    doctor_ok = lightweight_doctor_ok()
    if with_full_doctor:
        from agent.demand_os.doctor import run_doctor

        doctor_ok = run_doctor().ok

    hitl_gate = "BLOCKED" if MARKETING.startswith("PARKED") else "READY"

    return {
        "ok": True,
        "gate": GATE,
        "tool": "desk_contract_active",
        "desk": DESK,
        "contract_version": CONTRACT_VERSION,
        "marketing": MARKETING,
        "robota_dnia": robota,
        "icp_role_week": icp["icp_role_week"],
        "icp": icp,
        "iso_week": iso_week_label(),
        "state": desk_state(marketing=MARKETING),
        "week_calendar": build_week_calendar(),
        "shells_line": shells_line(),
        "screen": screen_dict,
        "money_check": mc,
        "dual_cash": dual,
        "data_mode": dm["data_mode"],
        "last_real_event": dm["last_real_event"],
        "stl": {
            "open_hot": stl.get("open_hot"),
            "breaches": stl.get("breaches"),
            "overnight": stl.get("overnight"),
            "median_min": stl.get("median_min"),
            "closed_hot": stl.get("closed_hot"),
        },
        "kpi": {
            "wizard_starts_utm": starts if starts else 0,
            "wizard_starts_wow_delta": wow,
            "paid": mc.get("paid") or 0,
            "validator_fail": validator_fail_display(
                publish_count=publish,
                validator_fail=int(mc.get("validator_fail") or 0),
            ),
            "top_hook": mc.get("top_hook") or "none",
            "publish_count": publish,
            "comments_sent": mc.get("comments_sent") or 0,
        },
        "footer": build_desk_footer(
            gate=GATE,
            data_mode=dm["data_mode"],
            last_real=dm["last_real_event"],
            doctor_ok=doctor_ok,
        ),
        "cash_warning": (
            "PARKED - EUR nie powstaje z Desk dopoki brak GO MARKETING HITL"
            if MARKETING.startswith("PARKED")
            else None
        ),
        "diagnostics": {
            "go_ready": {
                "score": go.get("score"),
                "ok": go.get("ok"),
                "unlock_date": go.get("unlock_date"),
                "blocker_live": go.get("blocker_live"),
                "marketing_hitl_gate": hitl_gate,
            },
            "marketing_hitl_gate": hitl_gate,
        },
    }
