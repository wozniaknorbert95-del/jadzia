"""Demand OS agent shells — orchestrate Hub tools, never live-publish.

`run_agent` kept for wave1 back-compat. New code should use the registry:
`from agent.demand_os.agents.registry import AGENT_REGISTRY, dispatch, list_agents`.
"""

from agent.demand_os.agents.registry import (
    AGENT_REGISTRY,
    all_roles,
    dispatch,
    get_agent,
    list_agents,
)
from agent.demand_os.agents.wave1 import run_agent
from agent.demand_os.agents.worker import CADENCE, due_actions, run_due

__all__ = [
    "AGENT_REGISTRY",
    "all_roles",
    "dispatch",
    "get_agent",
    "list_agents",
    "run_agent",
    "CADENCE",
    "due_actions",
    "run_due",
]
