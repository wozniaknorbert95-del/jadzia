"""Service abstractions and implementations for external dependencies.

Provides injectable interfaces for:
- ClaudeService  (primary LLM — Anthropic Claude)
- GeminiService  (secondary LLM — Google Gemini)
- WooCommerceService  (shop management via SSH + HTTP)
- NotificationService  (alerts — Discord / Telegram)
"""

from __future__ import annotations

import abc
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv

load_dotenv()


# ──────────────────────────────────────────────
# Domain value objects
# ──────────────────────────────────────────────

@dataclass
class ClaudeResponse:
    text: str
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    cost: float = 0.0


@dataclass
class CostStats:
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    total_cost: float = 0.0


# ──────────────────────────────────────────────
# Abstract service interfaces
# ──────────────────────────────────────────────

class ClaudeService(abc.ABC):
    """Interface for LLM (Anthropic Claude) interactions."""

    @abc.abstractmethod
    async def call(
        self,
        messages: List[Dict[str, Any]],
        system: Optional[str] = None,
        timeout: int = 120,
        task_complexity: str = "auto",
    ) -> ClaudeResponse:
        ...

    @abc.abstractmethod
    def get_cost_stats(self) -> CostStats:
        ...

    @abc.abstractmethod
    def reset_cost_stats(self) -> None:
        ...


class GeminiService(abc.ABC):
    """Interface for Gemini research queries."""

    @abc.abstractmethod
    async def research(self, query: str) -> str:
        ...


class WooCommerceService(abc.ABC):
    """Interface for WooCommerce / WordPress operations."""

    @abc.abstractmethod
    async def health_check(self) -> dict:
        ...

    @abc.abstractmethod
    async def read_file(self, path: str) -> Optional[str]:
        ...

    @abc.abstractmethod
    async def write_file(self, path: str, content: str, operation_id: str) -> bool:
        ...

    @abc.abstractmethod
    async def list_directory(self, path: str, recursive: bool = False) -> Tuple[bool, List[str], Optional[str]]:
        ...

    @abc.abstractmethod
    async def deploy(self, operation_id: str) -> dict:
        ...

    @abc.abstractmethod
    async def rollback(self) -> dict:
        ...

    @abc.abstractmethod
    async def test_ssh(self) -> Tuple[bool, str]:
        ...


class NotificationService(abc.ABC):
    """Interface for sending alerts (Discord, Telegram)."""

    @abc.abstractmethod
    def send_alert(self, alert_type: str, task_id: Optional[str], details: str) -> None:
        ...


# ──────────────────────────────────────────────
# Concrete implementations
# ──────────────────────────────────────────────

class AnthropicClaudeService(ClaudeService):
    """Claude service backed by the anthropic SDK."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_sonnet: str = "claude-sonnet-4-20250514",
        model_haiku: str = "claude-haiku-4-5-20251001",
        max_tokens: int = 4096,
    ):
        self._api_key = api_key if api_key is not None else os.getenv("ANTHROPIC_API_KEY", "")
        self._model_sonnet = model_sonnet
        self._model_haiku = model_haiku
        self._max_tokens = max_tokens
        self._input_tokens = 0
        self._output_tokens = 0
        self._cached_tokens = 0
        self._total_cost = 0.0

    def _get_client(self):
        if not self._api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        from anthropic import Anthropic
        return Anthropic(api_key=self._api_key)

    def _select_model(self, task_complexity: str) -> str:
        if task_complexity == "complex":
            return self._model_sonnet
        return self._model_haiku

    async def call(
        self,
        messages: List[Dict[str, Any]],
        system: Optional[str] = None,
        timeout: int = 120,
        task_complexity: str = "auto",
    ) -> ClaudeResponse:
        import asyncio

        model = self._select_model(task_complexity)
        client = self._get_client()
        loop = asyncio.get_event_loop()

        def _call():
            return client.messages.create(
                model=model,
                max_tokens=self._max_tokens,
                system=system or "",
                messages=messages,
            )

        try:
            response = await asyncio.wait_for(
                loop.run_in_executor(None, _call),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            raise RuntimeError(f"Claude did not respond within {timeout}s")
        except Exception as e:
            raise RuntimeError(f"Claude API error: {e}")

        text = response.content[0].text
        inp = getattr(response, "usage", None)
        input_tok = inp.input_tokens if inp else 0
        output_tok = inp.output_tokens if inp else 0
        cache_tok = getattr(inp, "cache_read_input_tokens", 0) if inp else 0

        cost = (input_tok * 3 + output_tok * 15 + cache_tok * 0.3) / 1_000_000

        self._input_tokens += input_tok
        self._output_tokens += output_tok
        self._cached_tokens += cache_tok
        self._total_cost += cost

        return ClaudeResponse(
            text=text,
            model=model,
            input_tokens=input_tok,
            output_tokens=output_tok,
            cached_tokens=cache_tok,
            cost=cost,
        )

    def get_cost_stats(self) -> CostStats:
        return CostStats(
            input_tokens=self._input_tokens,
            output_tokens=self._output_tokens,
            cached_tokens=self._cached_tokens,
            total_cost=self._total_cost,
        )

    def reset_cost_stats(self) -> None:
        self._input_tokens = 0
        self._output_tokens = 0
        self._cached_tokens = 0
        self._total_cost = 0.0


class DefaultGeminiService(GeminiService):
    """Gemini service backed by google-generativeai."""

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key if api_key is not None else os.getenv("GOOGLE_API_KEY", "")

    async def research(self, query: str) -> str:
        if not self._api_key:
            raise RuntimeError("GOOGLE_API_KEY not configured")
        try:
            import google.generativeai as genai

            genai.configure(api_key=self._api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = await model.generate_content_async(query)
            return response.text
        except ImportError:
            return "Gemini SDK not installed. Run: pip install google-generativeai"
        except Exception as e:
            return f"Gemini research error: {e}"


class SshWooCommerceService(WooCommerceService):
    """WooCommerce service backed by SSH + HTTP operations."""

    def __init__(self):
        self._ssh_host = os.getenv("SSH_HOST") or os.getenv("CYBERFOLKS_HOST", "")
        self._ssh_port = int(os.getenv("SSH_PORT", "22"))
        self._ssh_user = os.getenv("SSH_USER", "root")
        self._ssh_password = os.getenv("SSH_PASSWORD", "")
        self._ssh_key_path = os.getenv("SSH_KEY_PATH", "")
        self._shop_url = os.getenv("SHOP_URL", "")

    def _get_orchestrator(self):
        from agent.tools.ssh_orchestrator import SSHOrchestrator

        return SSHOrchestrator(
            host=self._ssh_host,
            port=self._ssh_port,
            username=self._ssh_user,
            password=self._ssh_password or None,
            key_path=self._ssh_key_path or None,
        )

    async def health_check(self) -> dict:
        from agent.tools.rest import health_check

        return health_check()

    async def read_file(self, path: str) -> Optional[str]:
        orch = self._get_orchestrator()
        return orch.read_file(path)

    async def write_file(self, path: str, content: str, operation_id: str) -> bool:
        orch = self._get_orchestrator()
        return orch.write_file(path, content, operation_id)

    async def list_directory(self, path: str, recursive: bool = False) -> Tuple[bool, List[str], Optional[str]]:
        from agent.tools.ssh_orchestrator import list_directory

        return list_directory(path, recursive=recursive)

    async def deploy(self, operation_id: str) -> dict:
        from agent.tools.rest import deploy

        return deploy(operation_id)

    async def rollback(self) -> dict:
        from agent.tools.rest import rollback

        return rollback()

    async def test_ssh(self) -> Tuple[bool, str]:
        from agent.tools.rest import test_ssh_connection

        return test_ssh_connection()


class DiscordNotificationService(NotificationService):
    """Notification service backed by Discord webhook."""

    def __init__(self, webhook_url: Optional[str] = None):
        self._webhook_url = webhook_url if webhook_url is not None else os.getenv("DISCORD_WEBHOOK_URL", "")

    def send_alert(self, alert_type: str, task_id: Optional[str], details: str) -> None:
        from agent.alerts import send_alert

        send_alert(alert_type, task_id, details)


# ──────────────────────────────────────────────
# Factory / registry for easy dependency wiring
# ──────────────────────────────────────────────

@dataclass
class ServiceRegistry:
    """Holds all service instances for DI wiring."""
    claude: ClaudeService = field(default_factory=AnthropicClaudeService)
    gemini: GeminiService = field(default_factory=DefaultGeminiService)
    woocommerce: WooCommerceService = field(default_factory=SshWooCommerceService)
    notifications: NotificationService = field(default_factory=DiscordNotificationService)


_registry: Optional[ServiceRegistry] = None


def get_registry() -> ServiceRegistry:
    """Get the global service registry (singleton)."""
    global _registry
    if _registry is None:
        _registry = ServiceRegistry()
    return _registry


def set_registry(registry: ServiceRegistry) -> None:
    """Override the global registry (useful for testing)."""
    global _registry
    _registry = registry


def reset_registry() -> None:
    """Reset registry (for test isolation)."""
    global _registry
    _registry = None
