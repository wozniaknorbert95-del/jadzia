"""Demand OS agent registry — single source of truth for wave1-3 role shells (OS §J).

Replaces three divergent entrypoints with one declarative registry + unified dispatch.
Honesty contract:
- these are orchestration shells over hub tools, not autonomous workers
- live-gated roles never claim live capability while marketing is PARKED
- unknown role / disallowed action → ok=False with explicit error (never silent)
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from agent.demand_os.marketing_mode import is_marketing_parked, resolve_marketing_mode

from agent.demand_os.agents import wave1, wave2, wave3

Runner = Callable[..., Dict[str, Any]]

AGENT_REGISTRY: Dict[str, Dict[str, Any]] = {
    "growth_lead": {
        "wave": 1,
        "label": "Growth Lead",
        "kpi": "starts_utm + paid WoW",
        "actions": ["status", "money_check", "weekly", "doctor", "sync_starts"],
        "mutating_actions": ["sync_starts"],
        "live_gated": False,
        "runner": wave1.run_agent,
    },
    "icp_brain": {
        "wave": 1,
        "label": "ICP Brain",
        "kpi": "ICP fit → starts",
        "actions": ["show", "set", "sync_memory"],
        "mutating_actions": ["set", "sync_memory"],
        "live_gated": False,
        "runner": wave1.run_agent,
    },
    "tt": {
        "wave": 1,
        "label": "TikTok (measure only)",
        "kpi": "starts tiktok",
        "actions": ["queue"],
        "mutating_actions": [],
        "live_gated": True,
        "runner": wave1.run_agent,
    },
    "sales": {
        "wave": 1,
        "label": "Sales / Hot Leads",
        "kpi": "hot→Wizard median (STL)",
        "actions": ["list_hot", "sync_hot"],
        "mutating_actions": ["sync_hot"],
        "live_gated": False,
        "runner": wave1.run_agent,
    },
    "validator": {
        "wave": 1,
        "label": "Validator",
        "kpi": "FAIL rate down · zero bypass",
        "actions": ["compliance"],
        "mutating_actions": [],
        "live_gated": False,
        "runner": wave1.run_agent,
    },
    "cf": {
        "wave": 2,
        "label": "Content Factory",
        "kpi": "assets 1 CTA · proof≥1",
        "actions": ["status", "brief", "assets", "proof"],
        "mutating_actions": [],
        "live_gated": True,
        "runner": wave2.run_wave2,
    },
    "fb": {
        "wave": 2,
        "label": "Facebook Engage",
        "kpi": "starts facebook + qualified comments/day",
        "actions": ["allowlist"],
        "mutating_actions": [],
        "live_gated": True,
        "runner": wave2.run_wave2,
    },
    "blog": {
        "wave": 3,
        "label": "Blog ICP",
        "kpi": "organic→starts",
        "actions": ["status", "pipeline"],
        "mutating_actions": ["pipeline"],
        "live_gated": True,
        "runner": wave3.run_wave3,
    },
    "cre": {
        "wave": 3,
        "label": "CRE Wizard",
        "kpi": "Wizard starts from hot",
        "actions": ["status"],
        "mutating_actions": [],
        "live_gated": False,
        "runner": wave3.run_wave3,
    },
}


def all_roles() -> List[str]:
    return sorted(AGENT_REGISTRY)


def get_agent(role: str) -> Dict[str, Any] | None:
    return AGENT_REGISTRY.get((role or "").strip().lower())


def _live_allowed(spec: Dict[str, Any], mode: str) -> bool:
    return not (spec["live_gated"] and is_marketing_parked(marketing=mode))


def list_agents(*, with_heartbeat: bool = True) -> List[Dict[str, Any]]:
    """Registry projection for hub/CLI (and future desk tile). Honest shell marker."""
    from agent.demand_os.agents.heartbeat import heartbeat_view

    mode = resolve_marketing_mode()
    out: List[Dict[str, Any]] = []
    for role in all_roles():
        spec = AGENT_REGISTRY[role]
        allowed = _live_allowed(spec, mode)
        row = {
            "role": role,
            "wave": spec["wave"],
            "label": spec["label"],
            "kpi": spec["kpi"],
            "actions": list(spec["actions"]),
            "mutating_actions": list(spec["mutating_actions"]),
            "live_gated": spec["live_gated"],
            "live_allowed": allowed,
            "blocked_reason": (
                "" if allowed else "live gated until Dowódca unlock (marketing PARKED)"
            ),
            "shell": True,
            "marketing": mode,
        }
        if with_heartbeat:
            row["heartbeat"] = heartbeat_view(role)
        out.append(row)
    return out


def _record_run_heartbeat(role: str, action: str) -> None:
    """Best-effort auto-heartbeat after a successful dispatch.

    A manual-only heartbeat would be a dead mechanism — no one runs it. Failed
    writes (read-only prod paths) are logged and never break the dispatch.
    """
    try:
        from agent.demand_os.agents.heartbeat import record_heartbeat

        record_heartbeat(role, action=action)
    except Exception as exc:  # noqa: BLE001 — observability must not break the run
        import logging

        logging.getLogger(__name__).warning(
            "auto-heartbeat failed role=%s err=%s", role, exc
        )


def dispatch(
    role: str, *, action: str = "status", probe: bool = False, **kwargs: Any
) -> Dict[str, Any]:
    """Unified envelope over wave shells. Never raises for bad input.

    `probe=True` marks observability calls (wave-check role probes, status
    pings): they must NOT record a heartbeat — otherwise the staleness check
    measures its own measurement and can never go red (D9-01). Heartbeat means
    "agent did work" (worker run-due, manual run), not "someone looked".
    """
    mode = resolve_marketing_mode()
    r = (role or "").strip().lower()
    spec = AGENT_REGISTRY.get(r)
    if spec is None:
        return {
            "ok": False,
            "role": r or None,
            "wave": None,
            "action": action,
            "result": None,
            "error": f"unknown role {role!r}; expected one of {all_roles()}",
            "marketing": mode,
        }
    act = (action or "status").strip().lower()
    if act not in spec["actions"]:
        return {
            "ok": False,
            "role": r,
            "wave": spec["wave"],
            "action": act,
            "result": None,
            "error": f"action {act!r} not allowed for {r}; allowed: {spec['actions']}",
            "marketing": mode,
        }
    allowed = _live_allowed(spec, mode)
    try:
        out = spec["runner"](r, action=act, **kwargs)
    except Exception as exc:  # noqa: BLE001 — shells must never crash the plane
        return {
            "ok": False,
            "role": r,
            "wave": spec["wave"],
            "action": act,
            "result": None,
            "error": str(exc)[:300],
            "marketing": mode,
            "live_allowed": allowed,
        }
    if not probe:
        _record_run_heartbeat(r, act)
    return {
        "ok": True,
        "role": r,
        "wave": spec["wave"],
        "action": act,
        "result": out.get("result", out),
        "raw": out,
        "marketing": out.get("marketing") or mode,
        "live_allowed": allowed,
        "blocked_reason": (
            "" if allowed else "live gated until Dowódca unlock (marketing PARKED)"
        ),
    }
