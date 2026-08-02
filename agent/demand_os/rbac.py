"""Demand OS RBAC — OS §G (read vs act). Aligns with commander ROLE_SCOPES."""

from __future__ import annotations

from typing import Any, Dict, Optional

SCOPE_READ = "demand_os:read"
SCOPE_ACT = "demand_os:act"

# Mutate-class hub actions (CLI / API)
ACT_ACTIONS = frozenset(
    {
        "sync-db",
        "sync-leads",
        "sync-paid",
        "ingest",
        "a2a-emit",
        "a2a-ack",
        "memory-icp",
        "memory-sync",
        "ledger-ensure",
        "engage-dry",
        "design-check",
        "audit-write",
    }
)


def scopes_for_role(role: str) -> list[str]:
    from agent.commander.constants import ROLE_SCOPES

    return list(ROLE_SCOPES.get((role or "").lower(), ROLE_SCOPES["viewer"]))


def can_read(auth: Optional[Dict[str, Any]] = None) -> bool:
    from agent.commander.authz import has_scope

    return has_scope(auth, SCOPE_READ) or has_scope(auth, "commander:read")


def can_act(auth: Optional[Dict[str, Any]] = None) -> bool:
    from agent.commander.authz import has_scope

    return has_scope(auth, SCOPE_ACT)


def require_act(auth: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if can_act(auth):
        return {"ok": True, "scope": SCOPE_ACT}
    return {
        "ok": False,
        "error": f"missing scope {SCOPE_ACT}",
        "scope": SCOPE_ACT,
    }


def classify_hub_cmd(cmd: str) -> str:
    """Return 'read' or 'act' for hub subcommand name."""
    c = (cmd or "").strip().lower()
    if c in ACT_ACTIONS or c.startswith("sync") or c in ("ingest",):
        return "act"
    return "read"
