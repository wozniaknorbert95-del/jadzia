"""Anthropic Claude client — model selection, caching, cost tracking."""

import asyncio
import logging
import os
from typing import Dict, List, Optional

from agent.prompt import get_system_prompt
from agent.tools import async_with_retry

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

MODEL_SONNET = "claude-sonnet-4-20250514"
MODEL_HAIKU = "claude-haiku-4-5-20251001"

MAX_TOKENS = 4096
TIMEOUT = 120

ENABLE_PROMPT_CACHING = True
TOKEN_STATS = {"input": 0, "output": 0, "cached": 0, "cost": 0.0}


def detect_session_source(chat_id: str) -> str:
    """Return 'telegram' if chat_id starts with 'telegram_', else 'http'."""
    if chat_id.startswith("telegram_"):
        return "telegram"
    return "http"


def get_claude_client():
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set in environment")
    from anthropic import Anthropic
    return Anthropic(api_key=ANTHROPIC_API_KEY)


async def call_claude(
    messages: List[Dict],
    system: Optional[str] = None,
    timeout: int = TIMEOUT,
    use_caching: bool = True,
    task_complexity: str = "complex",
) -> str:
    try:
        client = get_claude_client()
        loop = asyncio.get_event_loop()

        if task_complexity == "simple":
            model = MODEL_HAIKU
            logger.debug("[MODEL] task: simple -> Haiku")
        else:
            model = MODEL_SONNET
            logger.debug("[MODEL] task: complex -> Sonnet")

        def _call():
            system_content = system or get_system_prompt()

            if ENABLE_PROMPT_CACHING and use_caching:
                system_param = [{
                    "type": "text",
                    "text": system_content,
                    "cache_control": {"type": "ephemeral"},
                }]
            else:
                system_param = system_content

            response = client.messages.create(
                model=model,
                max_tokens=MAX_TOKENS,
                system=system_param,
                messages=messages,
            )

            usage = response.usage
            TOKEN_STATS["input"] += usage.input_tokens
            TOKEN_STATS["output"] += usage.output_tokens

            if hasattr(usage, "cache_read_input_tokens"):
                TOKEN_STATS["cached"] += usage.cache_read_input_tokens

            if model == MODEL_HAIKU:
                input_cost = (usage.input_tokens / 1_000_000) * 0.30
                output_cost = (usage.output_tokens / 1_000_000) * 1.50
                cached_cost = 0
                if hasattr(usage, "cache_read_input_tokens"):
                    cached_cost = (usage.cache_read_input_tokens / 1_000_000) * 0.03
            else:
                input_cost = (usage.input_tokens / 1_000_000) * 3.0
                output_cost = (usage.output_tokens / 1_000_000) * 15.0
                cached_cost = 0
                if hasattr(usage, "cache_read_input_tokens"):
                    cached_cost = (usage.cache_read_input_tokens / 1_000_000) * 0.30

            call_cost = input_cost + output_cost + cached_cost
            TOKEN_STATS["cost"] += call_cost

            logger.debug(
                "[COST] call: $%.4f | input=%s output=%s cached=%s",
                call_cost,
                usage.input_tokens,
                usage.output_tokens,
                getattr(usage, "cache_read_input_tokens", 0),
            )

            return response.content[0].text

        return await asyncio.wait_for(
            loop.run_in_executor(None, _call),
            timeout=timeout,
        )

    except asyncio.TimeoutError:
        raise RuntimeError(f"Claude did not respond within {timeout} seconds")
    except Exception as e:
        raise RuntimeError(f"Claude API error: {e}")


call_claude_with_retry = async_with_retry(
    max_attempts=3, delay=2.0, exceptions=(Exception,)
)(call_claude)


def get_cost_stats() -> dict:
    return {
        "total_input_tokens": TOKEN_STATS["input"],
        "total_output_tokens": TOKEN_STATS["output"],
        "total_cached_tokens": TOKEN_STATS["cached"],
        "total_cost_usd": round(TOKEN_STATS["cost"], 4),
        "estimated_savings_from_cache": round(
            (TOKEN_STATS["cached"] / 1_000_000) * (3.0 - 0.30), 4
        ) if TOKEN_STATS["cached"] > 0 else 0,
    }


def reset_cost_stats() -> None:
    TOKEN_STATS["input"] = 0
    TOKEN_STATS["output"] = 0
    TOKEN_STATS["cached"] = 0
    TOKEN_STATS["cost"] = 0.0


__all__ = [
    "ANTHROPIC_API_KEY",
    "MODEL_SONNET",
    "MODEL_HAIKU",
    "detect_session_source",
    "get_claude_client",
    "call_claude",
    "call_claude_with_retry",
    "get_cost_stats",
    "reset_cost_stats",
]
