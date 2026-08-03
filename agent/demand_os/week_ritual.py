"""OS §K weekly ritual — one screen of day jobs (no live publish)."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

from agent.demand_os.content_factory import build_brief
from agent.demand_os.ledger import ledger_summary
from agent.demand_os.marketing_mode import (
    marketing_hitl_gate,
    resolve_marketing_mode,
)
from agent.demand_os.observability import money_check
from agent.demand_os.stl_monitor import stl_report
from agent.demand_os.weekly_tune import weekly_success_report


def _weekday() -> str:
    # Mon=0 … Sun=6
    return ["pon", "wt", "sr", "czw", "pt", "sob", "nd"][date.today().weekday()]


def week_plan(*, day: str = "") -> Dict[str, Any]:
    d = (day or _weekday()).strip().lower()
    jobs: Dict[str, Dict[str, Any]] = {
        "pon": {
            "title": "Money Check + episodic",
            "actions": ["hub money-check", "hub memory sync", "hub stl"],
        },
        "wt": {
            "title": "ICP brief + master asset",
            "actions": ["agents --role icp_brain", "agents --role cf --action brief"],
        },
        "sr": {
            "title": "TT publish HITL",
            "actions": ["agents --role tt", "f2 validate → Founder GO"],
            "live": "PARKED_LAST until GO MARKETING HITL",
        },
        "czw": {
            "title": "Blog ICP",
            "actions": ["tools/demand_os_f4.py", "1 article · Wizard UTM blog"],
            "live": "PARKED_LAST ship",
        },
        "pt": {
            "title": "FB hunt + STL drill",
            "actions": ["agents --role fb", "hub stl", "sales sync_hot"],
            "live": "PARKED_LAST until GO MARKETING HITL",
        },
        "sob": {"title": "Rest / ledger hygiene", "actions": ["hub ledger"]},
        "nd": {"title": "Rest / ledger hygiene", "actions": ["hub ledger"]},
    }
    job = jobs.get(d) or jobs["pon"]
    return {
        "ok": True,
        "day": d,
        "job": job,
        "ledger": ledger_summary(),
        "money": money_check() if d == "pon" else None,
        "stl": stl_report() if d in ("pon", "pt") else None,
        "brief": build_brief(channel="tiktok") if d == "wt" else None,
        "weekly": weekly_success_report() if d == "pon" else None,
        "marketing": "PARKED_LAST",
        "rhythm": "OS §K",
    }


def go_day_ready() -> Dict[str, Any]:
    """Readiness score for organic GO day (≥2026-08-02) — tool side."""
    from pathlib import Path

    repo = Path(__file__).resolve().parents[2]
    checks: List[Dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    go_doc = repo / "docs/ops/demand-os/set-now/GO-DAY-2026-08-02.md"
    add("go_day_doc", go_doc.is_file(), str(go_doc.name))
    shoot = repo / "docs/ops/demand-os/set-now/TT-SHOOT-PLAN-W1.md"
    add("tt_shoot_plan", shoot.is_file())
    captions = repo / "docs/ops/demand-os/set-now/TT-CAPTIONS-W1.md"
    add("tt_captions", captions.is_file())
    allow = repo / "docs/ops/demand-os/set-now/ALLOWLIST.json"
    add("allowlist", allow.is_file())
    utm = repo / "docs/ops/demand-os/set-now/UTM-TEMPLATE.md"
    add("utm_template", utm.is_file())
    led = ledger_summary()
    add("ledger_exists", led.get("rows", 0) > 0, f"rows={led.get('rows')}")
    mc = money_check()
    add("money_check", "starts_utm" in mc)
    brief = build_brief(channel="tiktok", asset_id="tt_w32_install_01")
    add("cf_brief", brief.get("ok") is True)
    stl = stl_report()
    add("stl_monitor", stl.get("ok") is True)

    ok_n = sum(1 for c in checks if c["ok"])
    score = round(100.0 * ok_n / max(len(checks), 1), 1)
    marketing = resolve_marketing_mode()
    return {
        "ok": score >= 90,
        "score": score,
        "checks": checks,
        "unlock_date": "2026-08-02",
        "blocker_live": (
            "Founder GO MARKETING HITL"
            if marketing_hitl_gate(marketing=marketing) == "BLOCKED"
            else None
        ),
        "marketing_hitl_gate": marketing_hitl_gate(marketing=marketing),
        "marketing": marketing,
        "note": "tool ready ≠ live publish done",
    }
