"""JWT role and scope enforcement (N7)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from agent.commander.constants import ROLE_SCOPES


def resolve_role(payload: Optional[Dict[str, Any]]) -> str:
    if not payload:
        return "dowodca"
    user_id = payload.get("sub") or payload.get("user_id")
    if user_id:
        from agent.commander.settings import get_role_for_user

        mapped = get_role_for_user(str(user_id))
        if mapped:
            return mapped
    role = (payload.get("role") or "dowodca").lower()
    if role not in ROLE_SCOPES:
        return "dowodca"
    return role


def resolve_scopes(payload: Optional[Dict[str, Any]]) -> List[str]:
    if not payload:
        return ROLE_SCOPES["dowodca"]
    explicit = payload.get("scopes")
    if isinstance(explicit, list) and explicit:
        return [str(s) for s in explicit]
    return ROLE_SCOPES.get(resolve_role(payload), ROLE_SCOPES["dowodca"])


def has_scope(payload: Optional[Dict[str, Any]], required: str) -> bool:
    scopes = resolve_scopes(payload)
    if "*" in scopes:
        return True
    if required in scopes:
        return True
    if required.endswith(":read"):
        return "*:read" in scopes
    prefix = required.split(":")[0]
    return f"{prefix}:*" in scopes


def actor_from_payload(payload: Optional[Dict[str, Any]]) -> tuple[str, str]:
    if not payload:
        return "system", "dowodca"
    actor_id = str(payload.get("sub") or payload.get("user_id") or "unknown")
    return actor_id, resolve_role(payload)
