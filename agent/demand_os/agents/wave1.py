"""Wave1 agent shells (OS §H / §J) — thin orchestration, marketing PARKED_LAST.

Roles: growth_lead · icp_brain · tt · sales · validator
No live TT/FB publish. No Ads.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from agent.demand_os.commander_status import build_demand_os_status
from agent.demand_os.db_utm import sync_wizard_starts_from_ops_bus
from agent.demand_os.doctor import run_doctor
from agent.demand_os.memory import load_memory, set_semantic_icp, sync_episodic_from_ledger
from agent.demand_os.observability import money_check
from agent.demand_os.weekly_tune import weekly_success_report
from agent.demand_os.widget_leads import list_hot_leads, sync_hot_leads_to_a2a

WAVE1_ROLES = frozenset(
    {"growth_lead", "icp_brain", "tt", "sales", "validator"}
)


def run_agent(role: str, *, action: str = "status", **kwargs: Any) -> Dict[str, Any]:
    r = (role or "").strip().lower()
    if r not in WAVE1_ROLES:
        raise ValueError(f"role must be one of {sorted(WAVE1_ROLES)}")
    act = (action or "status").strip().lower()

    if r == "growth_lead":
        return _growth_lead(act, **kwargs)
    if r == "icp_brain":
        return _icp(act, **kwargs)
    if r == "tt":
        return _tt(act, **kwargs)
    if r == "sales":
        return _sales(act, **kwargs)
    return _validator(act, **kwargs)


def _growth_lead(action: str, **kwargs: Any) -> Dict[str, Any]:
    if action == "money_check":
        return {"role": "growth_lead", "action": action, "result": money_check()}
    if action == "weekly":
        return {"role": "growth_lead", "action": action, "result": weekly_success_report()}
    if action == "doctor":
        return {"role": "growth_lead", "action": action, "result": run_doctor().to_dict()}
    if action == "sync_starts":
        return {
            "role": "growth_lead",
            "action": action,
            "result": sync_wizard_starts_from_ops_bus(
                dry_run=bool(kwargs.get("dry_run", True))
            ),
        }
    # default status
    return {
        "role": "growth_lead",
        "action": "status",
        "result": build_demand_os_status(),
        "marketing": "PARKED_LAST",
        "kpi": "starts_utm + paid WoW",
    }


def _icp(action: str, **kwargs: Any) -> Dict[str, Any]:
    if action == "set":
        role = kwargs.get("icp_role") or "installateur"
        hook = kwargs.get("hook") or "witte bus · opdrachtgever ziet je niet"
        store = set_semantic_icp(role, hook)
        return {"role": "icp_brain", "action": action, "result": store}
    if action == "sync_memory":
        return {
            "role": "icp_brain",
            "action": action,
            "result": sync_episodic_from_ledger(
                weekly_improvement=kwargs.get("improvement") or ""
            ),
        }
    return {"role": "icp_brain", "action": "show", "result": load_memory()}


def _tt(action: str, **kwargs: Any) -> Dict[str, Any]:
    """TT shell: calendar/hitl queue only — no live publish."""
    status = build_demand_os_status()
    queue = (status.get("screen") or {}).get("hitl_queue") or []
    tt_slots = [q for q in queue if q.get("channel") == "tiktok"]
    return {
        "role": "tt",
        "action": action or "queue",
        "result": {
            "hitl_queue_tiktok": tt_slots,
            "live_publish": False,
            "note": "PARKED_LAST — Founder GO MARKETING HITL required to publish",
            "kpi": "starts tiktok (measure only)",
        },
        "marketing": "PARKED_LAST",
    }


def _sales(action: str, **kwargs: Any) -> Dict[str, Any]:
    if action == "sync_hot":
        return {
            "role": "sales",
            "action": action,
            "result": sync_hot_leads_to_a2a(
                dry_run=bool(kwargs.get("dry_run", True)),
                limit=int(kwargs.get("limit") or 10),
            ),
        }
    return {
        "role": "sales",
        "action": "list_hot",
        "result": list_hot_leads(limit=int(kwargs.get("limit") or 20)),
        "kpi": "hot→Wizard median time (STL)",
        "marketing": "PARKED_LAST",
    }


def _validator(action: str, **kwargs: Any) -> Dict[str, Any]:
    mc = money_check()
    return {
        "role": "validator",
        "action": action or "compliance",
        "result": {
            "validator_pass": mc.get("validator_pass"),
            "validator_fail": mc.get("validator_fail"),
            "sniper_compliance": mc.get("sniper_compliance"),
            "gate": "use tools/demand_os_f2.py validate|gate",
            "bypass": 0,
        },
        "kpi": "FAIL rate down · zero bypass",
    }
