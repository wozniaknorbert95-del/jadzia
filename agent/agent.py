"""
agent.py – Główna logika agenta JADZIA

NAPRAWIONE:
- Obsługa stanu (state deadlock)
- Obsługa komend informacyjnych (listowanie plików)
- Poprawna interpretacja odpowiedzi użytkownika
- POZIOM 2: Model Selection (Haiku dla prostych zadań)
- 🆕 SESSION-SCOPED: Izolacja stanu per użytkownik/źródło
- 🆕 QUESTIONS FLOW: Obsługa odpowiedzi na pytania od plannera
"""

import os
import asyncio
import logging
from typing import Optional, Tuple, Dict, List
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

from .prompt import get_system_prompt
from .tools import async_with_retry

# ============================================================
# KONFIGURACJA
# ============================================================

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# POZIOM 2: Dwa modele
MODEL_SONNET = "claude-sonnet-4-20250514"  # Złożone zadania
MODEL_HAIKU = "claude-haiku-4-5-20251001"     # Proste zadania (80% taniej!)

MAX_TOKENS = 4096
TIMEOUT = 120

# OPTYMALIZACJA POZIOM 1
MAX_FILE_SIZE = 10000
ENABLE_PROMPT_CACHING = True
TOKEN_STATS = {"input": 0, "output": 0, "cached": 0, "cost": 0.0}


# ============================================================
# 🆕 SESSION SOURCE DETECTION
# ============================================================

def detect_session_source(chat_id: str) -> str:
    """
    Detect session source based on chat_id format.
    
    Args:
        chat_id: Session identifier
    
    Returns:
        'telegram' if chat_id starts with 'telegram_', else 'http'
    """
    if chat_id.startswith("telegram_"):
        return "telegram"
    return "http"


# ============================================================
# CLAUDE API CLIENT
# ============================================================

def get_claude_client():
    """Tworzy klienta Anthropic"""
    if not ANTHROPIC_API_KEY:
        raise ValueError("Brak ANTHROPIC_API_KEY w .env")

    from anthropic import Anthropic
    return Anthropic(api_key=ANTHROPIC_API_KEY)


# (classify_task_complexity: agent/nodes/generate.py)

# ============================================================
# FUNKCJA call_claude Z POZIOM 2
# ============================================================

async def call_claude(
    messages: List[Dict],
    system: Optional[str] = None,
    timeout: int = TIMEOUT,
    use_caching: bool = True,
    task_complexity: str = "complex"
) -> str:
    """
    Wywołuje Claude API z optymalizacjami POZIOM 1 + 2.
    
    POZIOM 1: Prompt caching
    POZIOM 2: Model selection based on task complexity
    """
    try:
        client = get_claude_client()
        loop = asyncio.get_event_loop()
        
        # POZIOM 2: Wybór modelu
        if task_complexity == "simple":
            model = MODEL_HAIKU
            logger.debug("[MODEL] Zadanie: simple -> Haiku (80%% taniej!)")
        else:
            model = MODEL_SONNET
            logger.debug("[MODEL] Zadanie: complex -> Sonnet")

        def _call():
            system_content = system or get_system_prompt()

            if ENABLE_PROMPT_CACHING and use_caching:
                system_param = [{
                    "type": "text",
                    "text": system_content,
                    "cache_control": {"type": "ephemeral"}
                }]
            else:
                system_param = system_content

            response = client.messages.create(
                model=model,
                max_tokens=MAX_TOKENS,
                system=system_param,
                messages=messages
            )

            # MONITORING
            usage = response.usage
            TOKEN_STATS["input"] += usage.input_tokens
            TOKEN_STATS["output"] += usage.output_tokens

            if hasattr(usage, 'cache_read_input_tokens'):
                TOKEN_STATS["cached"] += usage.cache_read_input_tokens

            # Koszt zależy od modelu
            if model == MODEL_HAIKU:
                input_cost = (usage.input_tokens / 1_000_000) * 0.30
                output_cost = (usage.output_tokens / 1_000_000) * 1.50
                cached_cost = 0
                if hasattr(usage, 'cache_read_input_tokens'):
                    cached_cost = (usage.cache_read_input_tokens / 1_000_000) * 0.03
            else:
                input_cost = (usage.input_tokens / 1_000_000) * 3.0
                output_cost = (usage.output_tokens / 1_000_000) * 15.0
                cached_cost = 0
                if hasattr(usage, 'cache_read_input_tokens'):
                    cached_cost = (usage.cache_read_input_tokens / 1_000_000) * 0.30

            call_cost = input_cost + output_cost + cached_cost
            TOKEN_STATS["cost"] += call_cost

            logger.debug("[COST] Wywołanie: $%.4f | Input: %s | Output: %s | Cached: %s",
                         call_cost, usage.input_tokens, usage.output_tokens,
                         getattr(usage, 'cache_read_input_tokens', 0))

            return response.content[0].text

        result = await asyncio.wait_for(
            loop.run_in_executor(None, _call),
            timeout=timeout
        )

        return result

    except asyncio.TimeoutError:
        raise RuntimeError(f"Claude nie odpowiedzial w ciagu {timeout} sekund")
    except Exception as e:
        raise RuntimeError(f"Blad Claude API: {e}")


# Claude API with automatic retry (used when passing to route_user_input)
call_claude_with_retry = async_with_retry(max_attempts=3, delay=2.0, exceptions=(Exception,))(call_claude)


def get_cost_stats() -> dict:
    """Zwraca statystyki użycia i kosztów."""
    return {
        "total_input_tokens": TOKEN_STATS["input"],
        "total_output_tokens": TOKEN_STATS["output"],
        "total_cached_tokens": TOKEN_STATS["cached"],
        "total_cost_usd": round(TOKEN_STATS["cost"], 4),
        "estimated_savings_from_cache": round(
            (TOKEN_STATS["cached"] / 1_000_000) * (3.0 - 0.30), 4
        ) if TOKEN_STATS["cached"] > 0 else 0
    }


def reset_cost_stats():
    """Resetuje statystyki (np. na początku dnia)."""
    TOKEN_STATS["input"] = 0
    TOKEN_STATS["output"] = 0
    TOKEN_STATS["cached"] = 0
    TOKEN_STATS["cost"] = 0.0


# ============================================================
# Re-exported from core.agent (A3-01 migration)
# ============================================================

from core.agent import process_message, handle_error
