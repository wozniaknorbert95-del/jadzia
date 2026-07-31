"""Operations Bus typed catalog — allowlists only (no free-form chat)."""

from __future__ import annotations

from typing import Final, FrozenSet

EVENT_TYPES: Final[FrozenSet[str]] = frozenset(
    {
        "lead_qualified",
        "wizard_started",
        "order_created",
        "approval_needed",
    }
)

APPROVAL_LEVELS: Final[FrozenSet[str]] = frozenset({"L0", "L1", "L2", "L3", "L4"})

APPROVAL_STATES: Final[FrozenSet[str]] = frozenset(
    {"none", "pending", "approved", "rejected"}
)

# Rooms that may appear on MVP cash spine / hooks
ROOM_IDS: Final[FrozenSet[str]] = frozenset(
    {
        "sales-room",
        "wizard-quote",
        "order-desk",
        "mission-control",
        "approval-vault",
        "reception",
    }
)

# Ingest from Commander UI may only create these types
INGEST_ALLOWED_TYPES: Final[FrozenSet[str]] = frozenset({"wizard_started"})

AUDIT_ACTIONS: Final[dict[str, str]] = {
    "lead_qualified": "ops_bus.lead_qualified",
    "wizard_started": "ops_bus.wizard_started",
    "order_created": "ops_bus.order_created",
    "approval_needed": "ops_bus.approval_needed",
}

EVIDENCE_BY_TYPE: Final[dict[str, str]] = {
    "lead_qualified": "EV-W5-001",
    "wizard_started": "EV-W5-002",
    "order_created": "EV-W5-003",
    "approval_needed": "EV-W5-005",
}

# Forbidden payload keys (chat / free-form workflow)
FORBIDDEN_PAYLOAD_KEYS: Final[FrozenSet[str]] = frozenset(
    {
        "message",
        "chat",
        "messages",
        "agent_dialogue",
        "dialogue",
        "free_text",
        "prompt",
    }
)

MAX_PAYLOAD_BYTES: Final[int] = 4096
