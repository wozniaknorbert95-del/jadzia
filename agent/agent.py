"""Backward-compatible shim — canonical implementations live in core/."""

from core.agent import handle_error, process_message
from core.llm import (
    MODEL_HAIKU,
    MODEL_SONNET,
    call_claude,
    call_claude_with_retry,
    detect_session_source,
    get_claude_client,
    get_cost_stats,
    reset_cost_stats,
)

__all__ = [
    "MODEL_HAIKU",
    "MODEL_SONNET",
    "call_claude",
    "call_claude_with_retry",
    "detect_session_source",
    "get_claude_client",
    "get_cost_stats",
    "handle_error",
    "process_message",
    "reset_cost_stats",
]
