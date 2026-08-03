"""Wave readiness — OS TARGET v5 §J PASS criteria with honest tool/human split.

Each wave reports:
- tool checks (mechanical, verified by code now)
- human/live criteria (PASS only after live cadence — PARKED until unlock)

A wave is never claimed PASS from tool checks alone: `overall` is
"tool_ready" when all tool checks pass, "waiting" otherwise. `live_pass`
stays false until the human/live criteria are met outside this tool.
"""

from __future__ import annotations

from typing import Any, Dict, List

from agent.demand_os.agents.registry import AGENT_REGISTRY, dispatch
from agent.demand_os.ledger import ledger_summary
from agent.demand_os.marketing_mode import is_marketing_parked, resolve_marketing_mode

WAVE_PASS_LIVE = {
    1: "3 TT/tydz · ledger prowadzony (live cadence)",
    2: "comments daily (live engage)",
    3: "1 article/tydz shipped (live blog)",
    4: "starts WoW ↑ (live measurement)",
}

WAVE_ROLES = {
    1: ["growth_lead", "icp_brain", "tt", "sales", "validator"],
    2: ["cf", "fb"],
    3: ["blog"],
    4: [],
}


def _role_tool_check(role: str) -> Dict[str, Any]:
    spec = AGENT_REGISTRY[role]
    # Probe with the first non-mutating declared action (roles don't all expose "status")
    action = next(
        (a for a in spec["actions"] if a not in spec["mutating_actions"]),
        spec["actions"][0],
    )
    out = dispatch(role, action=action)
    return {
        "check": f"role_{role}",
        "ok": bool(out.get("ok")),
        "detail": out.get("error", "") or f"probe={action}",
    }


def _tool_checks(wave: int) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = [_role_tool_check(r) for r in WAVE_ROLES[wave]]
    if wave == 1:
        led = ledger_summary()
        checks.append(
            {"check": "ledger_operational", "ok": led.get("ok") is True, "detail": f"rows={led.get('rows')}"}
        )
    if wave == 3:
        out = dispatch("blog", action="status")
        drafts = (out.get("result") or {}).get("draft_count")
        checks.append(
            {
                "check": "blog_pipeline",
                "ok": bool(out.get("ok")) and drafts is not None,
                "detail": f"drafts={drafts}",
            }
        )
    if wave == 4:
        out = dispatch("icp_brain", action="show")
        mem = out.get("result") or {}
        episodic = mem.get("episodic") if isinstance(mem, dict) else None
        checks.append(
            {
                "check": "episodic_memory_layer",
                "ok": bool(out.get("ok")) and episodic is not None,
                "detail": "episodic layer present" if episodic is not None else "missing",
            }
        )
    return checks


def wave_readiness() -> Dict[str, Any]:
    mode = resolve_marketing_mode()
    parked = is_marketing_parked(marketing=mode)
    waves: List[Dict[str, Any]] = []
    for wave in (1, 2, 3, 4):
        checks = _tool_checks(wave)
        tool_ok = all(c["ok"] for c in checks)
        waves.append(
            {
                "wave": wave,
                "roles": WAVE_ROLES[wave],
                "tool_checks": checks,
                "tool_ok": tool_ok,
                "overall": "tool_ready" if tool_ok else "waiting",
                "live_pass_criteria": WAVE_PASS_LIVE[wave],
                "live_pass": False,
                "live_blocked_reason": (
                    "live cadence gated — marketing PARKED until Dowódca unlock" if parked else ""
                ),
            }
        )
    return {
        "ok": all(w["tool_ok"] for w in waves),
        "marketing": mode,
        "waves": waves,
        "roles_total": len(AGENT_REGISTRY),
        "note": "tool_ready ≠ live PASS — live criteria are human cadence after unlock",
    }
