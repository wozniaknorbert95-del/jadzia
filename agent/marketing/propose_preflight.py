"""Propose cutover preflight — evidence pack before MB_MODE=propose (NO flip)."""

from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utc_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _git_tip_short() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return (out or "").strip() or "unknown"
    except Exception:
        return "unknown"


def build_propose_preflight(
    *,
    accuracy: Dict[str, Any],
    breakers: Dict[str, Any],
    data_health: Dict[str, Any],
    mb_mode: str,
    brain_bus: Optional[Dict[str, Any]] = None,
    memory: Optional[Dict[str, Any]] = None,
    tip: Optional[str] = None,
    l0_ic_pass: bool = True,
    purchase_park: bool = True,
) -> Dict[str, Any]:
    """
    Pure verdikt from already-fetched reports.
    Does NOT flip MB_MODE. Expected pre-GO mode is shadow.
    """
    tip = tip or _git_tip_short()
    mode = (mb_mode or "shadow").strip().lower()
    checks: List[Dict[str, Any]] = []
    hard_fail = False
    warns: List[str] = []

    gate_ready = bool(accuracy.get("gate_ready"))
    n_scored = int(accuracy.get("n_scored") or 0)
    acc_val = accuracy.get("accuracy")
    checks.append(
        {
            "id": "accuracy_gate",
            "ok": gate_ready,
            "detail": f"n={n_scored} accuracy={acc_val} reason={accuracy.get('gate_reason')}",
        }
    )
    if not gate_ready:
        hard_fail = True

    mode_ok = mode == "shadow"
    checks.append(
        {
            "id": "mb_mode",
            "ok": mode_ok,
            "detail": f"MB_MODE={mode} (expect shadow before GO)",
        }
    )
    if not mode_ok:
        hard_fail = True

    trips = list(breakers.get("trips") or [])
    trip_ids = [t.get("breaker_id") for t in trips]
    unexpected = [t for t in trips if t.get("breaker_id") != "CB_SHADOW"]
    breakers_ok = len(unexpected) == 0 and "CB_SHADOW" in trip_ids
    if not trips and mode == "shadow":
        # shadow without CB_SHADOW trip is suspicious but not hard-fail if mode says shadow
        breakers_ok = False
        warns.append("breakers_empty_while_shadow")
    checks.append(
        {
            "id": "breakers",
            "ok": breakers_ok and len(unexpected) == 0,
            "detail": f"trips={trip_ids} unexpected={[t.get('breaker_id') for t in unexpected]}",
        }
    )
    if unexpected:
        hard_fail = True
    if not breakers_ok:
        hard_fail = True

    overall = (data_health.get("overall_status") or "").lower()
    dh_ok = overall != "red"
    checks.append(
        {
            "id": "data_health",
            "ok": dh_ok,
            "detail": f"overall_status={overall or 'unknown'}",
        }
    )
    if not dh_ok:
        hard_fail = True

    eco_flags = list((brain_bus or {}).get("ecosystem_flags") or [])
    eco_red = [
        f
        for f in eco_flags
        if f.get("flag_type") == "ecosystem_red"
        or (f.get("severity") or "").lower() in ("critical", "red")
    ]
    eco_ok = len(eco_red) == 0
    checks.append(
        {
            "id": "brain_bus_ecosystem",
            "ok": eco_ok,
            "detail": f"ecosystem_red_or_critical={len(eco_red)}",
        }
    )
    if not eco_ok:
        hard_fail = True

    mem = memory or {}
    mem_backend = mem.get("memory_source") or mem.get("backend") or "unknown"
    mem_ok = mem.get("ok", True) is not False
    if mem.get("error") and mem.get("ok") is False:
        mem_ok = False
    if not mem_ok:
        hard_fail = True
    checks.append(
        {
            "id": "campaign_memory",
            "ok": mem_ok,
            "detail": f"source={mem_backend} count={mem.get('count')}",
        }
    )

    checks.append(
        {
            "id": "l0_initiate_checkout",
            "ok": bool(l0_ic_pass),
            "detail": "PASS (docs)" if l0_ic_pass else "MISSING",
        }
    )
    if not l0_ic_pass:
        hard_fail = True

    checks.append(
        {
            "id": "purchase_park_acknowledged",
            "ok": bool(purchase_park),
            "detail": "PARK Mollie (conscious)" if purchase_park else "NOT_ACKED",
        }
    )
    if not purchase_park:
        hard_fail = True

    note = accuracy.get("consecutive_weeks_note")
    if note:
        warns.append(str(note))

    verdict = "BLOCKED" if hard_fail else "READY_FOR_GO"
    acc_pct = ""
    try:
        acc_pct = f"{float(acc_val) * 100:.0f}%"
    except (TypeError, ValueError):
        acc_pct = str(acc_val)

    go_ticket = (
        f"GO propose {_utc_date()} — accuracy={acc_pct} "
        f"n={n_scored} — tip={tip} — preflight={verdict}"
    )

    return {
        "verdict": verdict,
        "checks": checks,
        "warns": warns,
        "go_ticket": go_ticket,
        "mb_mode_flip": "DO_NOT_FLIP",
        "mb_mode": mode,
        "tip": tip,
        "accuracy": {
            "n_scored": n_scored,
            "accuracy": acc_val,
            "gate_ready": gate_ready,
            "gate_reason": accuracy.get("gate_reason"),
        },
        "as_of": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }


def run_propose_preflight(
    *,
    window_days: int = 14,
    tip: Optional[str] = None,
) -> Dict[str, Any]:
    """Gather live reports and build verdikt (no env mutation)."""
    from agent.db import db_list_active_quality_flags, db_list_brain_events
    from agent.marketing.campaign_memory import memory_status
    from agent.marketing.circuit_breakers import is_execute_allowed
    from agent.marketing.dtl import build_data_health_report
    from agent.marketing.shadow_eval import compute_accuracy

    accuracy = compute_accuracy(window_days=window_days)
    breakers = is_execute_allowed()
    data_health = build_data_health_report()
    mb_mode = (os.getenv("MB_MODE") or "shadow").strip().lower()

    flags = [
        f
        for f in db_list_active_quality_flags(limit=50)
        if f.get("source") in ("vcms", "ceo_stub")
        or f.get("flag_type") in ("ecosystem_red", "ceo_priority")
    ]
    brain_bus = {
        "events": db_list_brain_events(limit=5),
        "ecosystem_flags": flags,
    }
    memory = memory_status()

    return build_propose_preflight(
        accuracy=accuracy,
        breakers=breakers,
        data_health=data_health,
        mb_mode=mb_mode,
        brain_bus=brain_bus,
        memory=memory,
        tip=tip,
    )
