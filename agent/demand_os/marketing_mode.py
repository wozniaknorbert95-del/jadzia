"""Marketing HITL mode — single switch for GO MARKETING HITL (env-only, default PARKED)."""

from __future__ import annotations

import os

PARKED = "PARKED_LAST"
LIVE = "HITL_LIVE"

_GO_VALUES = frozenset({"GO", "LIVE", "1", "TRUE", "YES"})


def resolve_marketing_mode() -> str:
    """Return PARKED_LAST unless DEMAND_OS_MARKETING_HITL signals Founder GO."""
    raw = (os.environ.get("DEMAND_OS_MARKETING_HITL") or "").strip().upper()
    if raw in _GO_VALUES:
        return LIVE
    return PARKED


def marketing_hitl_gate(*, marketing: str | None = None) -> str:
    mode = marketing if marketing is not None else resolve_marketing_mode()
    return "BLOCKED" if (mode or "").upper().startswith("PARKED") else "READY"


def is_marketing_parked(*, marketing: str | None = None) -> bool:
    mode = marketing if marketing is not None else resolve_marketing_mode()
    return (mode or "").upper().startswith("PARKED")
