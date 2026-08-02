"""Demand OS F3 — social connectors (allowlist + anti-spam + engage)."""

from agent.demand_os.connectors.allowlist import (
    AllowlistError,
    get_target,
    list_active_targets,
    load_allowlist,
    require_engage_target,
)
from agent.demand_os.connectors.engage import comment_on_target, read_target

__all__ = [
    "AllowlistError",
    "comment_on_target",
    "get_target",
    "list_active_targets",
    "load_allowlist",
    "read_target",
    "require_engage_target",
]
