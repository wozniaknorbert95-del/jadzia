"""Agents worker loop — due-dispatcher over the registry (design doc 8-04).

One systemd timer calls `run_due`; the cadence map decides which (role, action)
is due based on heartbeat recency. Tool-only forever: live_gated roles are
never dispatched here, even after marketing unlock (live cadence = HITL).
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.demand_os.agents.heartbeat import heartbeat_age_days, load_heartbeats
from agent.demand_os.agents.registry import AGENT_REGISTRY, dispatch

# role -> {action: cadence_hours}. Read/upsert actions only — idempotent by
# design; mutating publish/engage never enters this map.
CADENCE: Dict[str, Dict[str, float]] = {
    "growth_lead": {"sync_starts": 24.0, "money_check": 24.0},
    "sales": {"sync_hot": 6.0, "list_hot": 6.0},
    "validator": {"compliance": 24.0},
    "icp_brain": {"sync_memory": 24.0},
    "cre": {"status": 24.0},
}

# Mutating registry actions get dry_run=False only on --apply.
_MUTATING = {"sync_starts", "sync_hot", "sync_memory"}


def due_actions(*, path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Cadence entries whose heartbeat is older than cadence or missing.

    live_gated roles are excluded by contract (worker is tool-only).
    """
    beats = load_heartbeats(path=path)
    due: List[Dict[str, Any]] = []
    for role in sorted(CADENCE):
        spec = AGENT_REGISTRY.get(role) or {}
        if spec.get("live_gated"):
            continue
        rec = beats.get(role) or {}
        age = heartbeat_age_days(rec)
        age_h = None if age is None else age * 24.0
        for action, cadence_h in sorted(CADENCE[role].items()):
            if action not in spec.get("actions", []):
                continue
            if age_h is None or age_h >= cadence_h:
                due.append(
                    {
                        "role": role,
                        "action": action,
                        "cadence_hours": cadence_h,
                        "heartbeat_age_hours": age_h,
                        "reason": "never_ran" if age_h is None else "overdue",
                    }
                )
    return due


def run_due(
    *,
    dry_run: bool = True,
    path: Optional[Path] = None,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Dispatch all due actions. Honest envelope; never raises."""
    _ = now or datetime.now(timezone.utc)  # explicit clock for future tests
    due = due_actions(path=path)
    runs: List[Dict[str, Any]] = []
    for item in due:
        kwargs: Dict[str, Any] = {}
        if item["action"] in _MUTATING:
            kwargs["dry_run"] = dry_run
        if dry_run:
            runs.append(
                {
                    "role": item["role"],
                    "action": item["action"],
                    "status": "dry_run",
                    "reason": item["reason"],
                }
            )
            continue
        out = dispatch(item["role"], action=item["action"], **kwargs)
        runs.append(
            {
                "role": item["role"],
                "action": item["action"],
                "status": "dispatched" if out.get("ok") else "error",
                "ok": out.get("ok"),
                "error": out.get("error") or "",
            }
        )
    return {
        "ok": True,
        "mode": "dry_run" if dry_run else "apply",
        "due": due,
        "runs": runs,
        "dispatched": sum(1 for r in runs if r["status"] == "dispatched"),
        "errors": sum(1 for r in runs if r["status"] == "error"),
        "cadence_roles": sorted(CADENCE),
        "note": "tool-only loop — live_gated roles never dispatched here",
    }
