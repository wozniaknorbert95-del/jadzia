"""Success tune — OS §F weekly: 1 improvement from #1 hook (no live publish CTA)."""

from __future__ import annotations

from typing import Any, Dict, Optional
from pathlib import Path

from agent.demand_os.memory import sync_episodic_from_ledger
from agent.demand_os.observability import money_check


def weekly_success_report(
    *,
    set_now: Optional[Path] = None,
    memory_path: Optional[Path] = None,
) -> Dict[str, Any]:
    mc = money_check(set_now=set_now)
    top = mc.get("top_hook") or "none"
    starts = int(mc.get("starts_utm") or 0)
    compliance = mc.get("sniper_compliance")
    if starts <= 0:
        improvement = (
            f"Instrument starts ingest for top planned asset ({top}) — "
            "measure Wizard starts before any live content push"
        )
    elif (compliance or 1) < 0.9:
        improvement = (
            f"Raise sniper compliance (now {compliance}) — fix Val FAILs before scaling touches"
        )
    else:
        improvement = (
            f"Double down on angle behind #{top} next week — same ICP pain, new creative angle "
            "(fatigue 7-14d) — tool path only until GO MARKETING HITL"
        )
    store = sync_episodic_from_ledger(
        set_now=set_now,
        memory_path=memory_path,
        weekly_improvement=improvement,
    )
    return {
        "starts_utm": starts,
        "starts_by_utm": mc.get("starts_by_utm") or {},
        "paid": mc.get("paid") or 0,
        "top_hook": top,
        "sniper_compliance": compliance,
        "improvement": improvement,
        "live_publish_cta": False,
        "marketing": "PARKED_LAST",
        "memory_updated": store.get("updated"),
    }
