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

from agent.demand_os.agents.heartbeat import STALE_LIMITS_H as _STALE_LIMITS_H
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
    out = dispatch(role, action=action, probe=True)
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
        checks.append(_state_writers_check())
    if wave == 3:
        out = dispatch("blog", action="status", probe=True)
        drafts = (out.get("result") or {}).get("draft_count")
        checks.append(
            {
                "check": "blog_pipeline",
                "ok": bool(out.get("ok")) and drafts is not None,
                "detail": f"drafts={drafts}",
            }
        )
    if wave == 4:
        out = dispatch("icp_brain", action="show", probe=True)
        mem = out.get("result") or {}
        episodic = mem.get("episodic") if isinstance(mem, dict) else None
        episodic_keys = sorted(episodic.keys()) if isinstance(episodic, dict) else []
        checks.append(
            {
                "check": "episodic_memory_layer",
                "ok": bool(out.get("ok")) and bool(episodic_keys),
                "detail": (
                    f"keys={len(episodic_keys)} ({', '.join(episodic_keys[:4])})"
                    if episodic_keys
                    else "missing"
                ),
            }
        )
        from agent.demand_os.fatigue import fatigue_check

        probe = fatigue_check("__wave_probe__")
        checks.append(
            {
                "check": "fatigue_tool_probe",
                "ok": probe.get("ok") is True and probe.get("fatigue") is False,
                "detail": probe.get("note") or probe.get("error") or "B.4 probe",
            }
        )
        from agent.demand_os.a2a_bus import default_bus_path

        try:
            bus_path = default_bus_path()
            exists = bus_path.is_file()
            checks.append(
                {
                    "check": "a2a_bus_writable",
                    "ok": True,
                    "detail": (
                        f"{bus_path.name} present"
                        if exists
                        else f"resolvable at {bus_path.parent.name}/ (created on first handoff)"
                    ),
                }
            )
        except Exception as exc:  # noqa: BLE001
            checks.append(
                {"check": "a2a_bus_writable", "ok": False, "detail": str(exc)[:200]}
            )
    checks.append(_heartbeat_staleness_check())
    return checks


# Every Demand OS runtime writer with a default-path resolver (8-06). Each
# resolver must route through state_paths.resolve_writable_path (env override →
# writable set-now → data/demand-os fallback). The check probes the resolved
# parent dir for real writability — catches the prod PermissionError class
# (D8 writable-path defect family) before any publish path depends on it.
def _state_writer_resolvers() -> List[Any]:
    from agent.demand_os.a2a_bus import default_bus_path
    from agent.demand_os.agents.heartbeat import default_heartbeat_path
    from agent.demand_os.audit_log import default_audit_path
    from agent.demand_os.blog_pipeline import default_drafts_dir
    from agent.demand_os.connectors.anti_spam import default_engage_log_path
    from agent.demand_os.content_calendar import default_calendar_path
    from agent.demand_os.growth_events import default_events_path
    from agent.demand_os.memory import default_memory_path
    from agent.demand_os.validator import default_validator_log_path

    return [
        ("a2a_bus", default_bus_path),
        ("agents_heartbeat", default_heartbeat_path),
        ("audit_log", default_audit_path),
        ("blog_drafts", default_drafts_dir),
        ("engage_log", default_engage_log_path),
        ("content_calendar", default_calendar_path),
        ("growth_events", default_events_path),
        ("memory", default_memory_path),
        ("validator_log", default_validator_log_path),
    ]


def _state_writers_check() -> Dict[str, Any]:
    failures: List[str] = []
    resolved: List[str] = []
    for name, resolver in _state_writer_resolvers():
        try:
            path = resolver()
            parent = path if path.suffix == "" else path.parent
            parent.mkdir(parents=True, exist_ok=True)
            probe = parent / ".writers_probe"
            probe.write_text("", encoding="utf-8")
            probe.unlink(missing_ok=True)
            resolved.append(name)
        except Exception as exc:  # noqa: BLE001 — report every writer, not first
            failures.append(f"{name}: {str(exc)[:120]}")
    return {
        "check": "state_writers_resolvable",
        "ok": not failures,
        "detail": (
            f"{len(resolved)}/{len(_state_writer_resolvers())} writers resolvable+writable"
            if not failures
            else f"unwritable: {'; '.join(failures)}"
        ),
    }


# `_STALE_LIMITS_H` (imported above) is the alias for the mechanical contract
# test (keys == worker.CADENCE); the policy table lives in heartbeat.py as the
# single source of truth shared with heartbeat_view (desk chip) — S10/9-02.


def _heartbeat_staleness_check() -> Dict[str, Any]:
    """Heartbeat recency for cadence (worker-supervised) roles.

    ok=False signals "agent not running on cadence" — the exact failure mode the
    worker loop exists to prevent. Read-only: never writes the heartbeat file.
    Limits default to 2x worker CADENCE (drift margin), overridable via
    DEMAND_OS_HB_STALE_<ROLE> env (hours).
    """
    from agent.demand_os.agents.heartbeat import (
        heartbeat_age_days,
        load_heartbeats,
        stale_limit_hours,
    )
    from agent.demand_os.agents.worker import CADENCE

    beats = load_heartbeats()
    stale: List[str] = []
    for role in sorted(CADENCE):
        limit_h = stale_limit_hours(role, default_h=48.0)
        age = heartbeat_age_days(beats.get(role) or {})
        limit_d = limit_h / 24.0
        if age is None or age > limit_d:
            age_txt = "never" if age is None else f"{age * 24.0:.1f}h"
            stale.append(f"{role}({age_txt}>{limit_h:.0f}h)")
    return {
        "check": "heartbeat_staleness",
        "ok": not stale,
        "detail": (
            "all cadence roles fresh"
            if not stale
            else f"stale: {', '.join(stale)} — run: tools.demand_os_hub agents run-due --apply"
        ),
    }


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
