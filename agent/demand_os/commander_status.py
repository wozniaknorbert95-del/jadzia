"""Commander Demand OS status payload — Desk v2.1.1 contract (API + tests)."""

from __future__ import annotations

import csv
import logging
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
from agent.demand_os.attribution import attribution_summary
from agent.demand_os.desk_copy import CASH_WARNING_PARKED, EMPTY_TOP_ASSETS_NOTE
from agent.demand_os.ga4_adapter import fetch_wizard_starts
from agent.demand_os.marketing_mode import (
    is_marketing_parked,
    marketing_hitl_gate,
    resolve_marketing_mode,
)
from agent.demand_os.observability import build_screen, money_check
from agent.demand_os.stl_monitor import stl_report
from agent.demand_os.week_ritual import go_day_ready

logger = logging.getLogger(__name__)

GATE = "DEMAND-OS-DESK-CONTRACT-00"
DESK = "Demand Desk v2.1"


def build_demand_os_status(
    *,
    set_now: Optional[Path] = None,
    events_path: Optional[Path] = None,
    with_full_doctor: bool = False,
) -> Dict[str, Any]:
    screen = build_screen(set_now=set_now, events_path=events_path)
    mc = money_check(set_now=set_now, events_path=events_path)
    marketing = resolve_marketing_mode()
    starts = int(mc.get("starts_utm") or 0)
    publish = int(mc.get("publish_count") or 0)
    go = go_day_ready()
    stl = stl_report()
    robota = resolve_robota_dnia(marketing=marketing)
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
    screen_dict["top_wizard_note"] = "" if top5 else EMPTY_TOP_ASSETS_NOTE
    screen_dict["hitl_queue"] = screen_dict.get("hitl_queue") or []

    files_ok = lightweight_doctor_ok()
    doctor_scope = "lightweight"
    doctor_ok = False
    if with_full_doctor:
        from agent.demand_os.doctor import run_doctor

        doctor_scope = "full"
        doctor_ok = run_doctor().ok

    hitl_gate = marketing_hitl_gate(marketing=marketing)

    try:
        ga4 = fetch_wizard_starts(days=7)
    except Exception as exc:
        logger.warning("GA4 adapter error in desk status: %s", exc)
        ga4 = {
            "ok": False,
            "status": "unavailable",
            "mode": "error",
            "starts": [],
            "ga4_sessions_7d": None,
            "ga4_wizard_starts_7d": None,
            "error": str(exc)[:200],
            "reason": str(exc)[:200],
        }
    ga4_status = ga4.get("status") or ("ok" if ga4.get("ok") else "unavailable")
    ga4_sessions = ga4.get("ga4_sessions_7d")
    if ga4_sessions is None and ga4.get("ok") and ga4.get("aggregate"):
        ga4_sessions = ga4["aggregate"].get("sessions")
    ga4_wizard_starts = ga4.get("ga4_wizard_starts_7d")
    try:
        attribution = attribution_summary(days=7)
    except Exception as exc:
        logger.warning("attribution summary error: %s", exc)
        attribution = {
            "ok": False,
            "status": "unavailable",
            "total": 0,
            "by_status": {},
            "top_assets": [],
            "window_days": 7,
            "error": str(exc)[:200],
        }

    return {
        "ok": True,
        "gate": GATE,
        "tool": "desk_contract_active",
        "desk": DESK,
        "contract_version": CONTRACT_VERSION,
        "marketing": marketing,
        "robota_dnia": robota,
        "icp_role_week": icp["icp_role_week"],
        "icp": icp,
        "iso_week": iso_week_label(),
        "state": desk_state(marketing=marketing),
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
            "utm_attributed_starts": starts if starts else 0,
            "wizard_starts_wow_delta": wow,
            "paid": mc.get("paid") or 0,
            "validator_fail": validator_fail_display(
                publish_count=publish,
                validator_fail=int(mc.get("validator_fail") or 0),
            ),
            "top_hook": mc.get("top_hook") or "none",
            "publish_count": publish,
            "comments_sent": mc.get("comments_sent") or 0,
            "ga4_sessions_7d": ga4_sessions,
            "ga4_wizard_starts_7d": ga4_wizard_starts,
        },
        "ga4": {
            "ok": bool(ga4.get("ok")),
            "status": ga4_status,
            "mode": ga4.get("mode", "stub"),
            "sessions": ga4_sessions,
            "ga4_sessions_7d": ga4_sessions,
            "ga4_wizard_starts_7d": ga4_wizard_starts,
            "utm_attributed_starts": starts if starts else 0,
            "freshness": ga4.get("freshness"),
            "error": ga4.get("error", ""),
            "reason": ga4.get("reason") or ga4.get("error", ""),
        },
        "attribution": attribution,
        "footer": build_desk_footer(
            gate=GATE,
            data_mode=dm["data_mode"],
            last_real=dm["last_real_event"],
            doctor_ok=doctor_ok,
            doctor_scope=doctor_scope,
            doctor_files_ok=files_ok,
        ),
        "cash_warning": (
            CASH_WARNING_PARKED if is_marketing_parked(marketing=marketing) else None
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
            "live_cadence": "PARKED",
            "note": "env GO ≠ cadence unlock — see UNLOCK-LIVE-P0.md",
        },
    }
