"""Unit tests for core/services.py — service abstractions and registry."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.services import (
    AnthropicClaudeService,
    ClaudeService,
    ClaudeResponse,
    CostStats,
    DefaultGeminiService,
    DiscordNotificationService,
    GeminiService,
    NotificationService,
    ServiceRegistry,
    WooCommerceService,
    get_registry,
    reset_registry,
    set_registry,
)


class TestClaudeResponse:
    def test_claude_response_defaults(self):
        r = ClaudeResponse(text="hello")
        assert r.text == "hello"
        assert r.model == ""
        assert r.input_tokens == 0
        assert r.cost == 0.0

    def test_claude_response_with_data(self):
        r = ClaudeResponse(
            text="response",
            model="sonnet",
            input_tokens=100,
            output_tokens=50,
            cost=0.001,
        )
        assert r.model == "sonnet"
        assert r.cost == 0.001


class TestCostStats:
    def test_cost_stats_defaults(self):
        c = CostStats()
        assert c.input_tokens == 0
        assert c.total_cost == 0.0


class TestAnthropicClaudeService:
    def test_init_defaults(self):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
            svc = AnthropicClaudeService()
            assert svc._api_key == "sk-test-key"

    def test_init_with_custom_key(self):
        svc = AnthropicClaudeService(api_key="sk-custom")
        assert svc._api_key == "sk-custom"

    def test_get_cost_stats_default(self):
        svc = AnthropicClaudeService(api_key="sk-test")
        stats = svc.get_cost_stats()
        assert stats.input_tokens == 0
        assert stats.total_cost == 0.0

    def test_reset_cost_stats(self):
        svc = AnthropicClaudeService(api_key="sk-test")
        svc._input_tokens = 100
        svc._total_cost = 0.5
        svc.reset_cost_stats()
        stats = svc.get_cost_stats()
        assert stats.input_tokens == 0
        assert stats.total_cost == 0.0

    @pytest.mark.asyncio
    async def test_call_no_api_key(self):
        svc = AnthropicClaudeService(api_key="")
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY not configured"):
            await svc.call([{"role": "user", "content": "hi"}])

    @pytest.mark.asyncio
    async def test_call_requires_api_key(self):
        svc = AnthropicClaudeService(api_key="")
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            await svc.call([{"role": "user", "content": "hi"}])


class TestDefaultGeminiService:
    def test_init_no_key(self):
        svc = DefaultGeminiService()
        assert svc._api_key == ""  # no env set

    def test_init_with_key(self):
        svc = DefaultGeminiService(api_key="test-key")
        assert svc._api_key == "test-key"

    @pytest.mark.asyncio
    async def test_research_no_key(self):
        svc = DefaultGeminiService(api_key="")
        with pytest.raises(RuntimeError, match="GOOGLE_API_KEY not configured"):
            await svc.research("test query")


class TestDiscordNotificationService:
    def test_init_defaults(self):
        svc = DiscordNotificationService()
        assert svc._webhook_url == ""

    def test_init_with_url(self):
        svc = DiscordNotificationService(webhook_url="https://discord.com/webhook/test")
        assert svc._webhook_url == "https://discord.com/webhook/test"


class TestServiceRegistry:
    def test_default_registry(self):
        reset_registry()
        reg = get_registry()
        assert isinstance(reg.claude, AnthropicClaudeService)
        assert isinstance(reg.gemini, DefaultGeminiService)
        assert isinstance(reg.notifications, DiscordNotificationService)

    def test_set_registry(self):
        class MockClaude(ClaudeService):
            async def call(self, messages, system=None, timeout=120, task_complexity="auto"):
                return ClaudeResponse(text="mock")
            def get_cost_stats(self):
                return CostStats()
            def reset_cost_stats(self):
                pass

        mock = MockClaude()
        reg = ServiceRegistry(claude=mock)
        set_registry(reg)
        assert get_registry().claude is mock
        reset_registry()

    def test_registry_is_singleton(self):
        reset_registry()
        reg1 = get_registry()
        reg2 = get_registry()
        assert reg1 is reg2

    def test_reset_registry(self):
        reset_registry()
        reg1 = get_registry()
        reset_registry()
        reg3 = get_registry()
        assert reg1 is not reg3


class TestAnthropicClaudeServiceCall:
    def test_model_selection_complex(self):
        svc = AnthropicClaudeService(api_key="sk-test")
        assert svc._select_model("complex") == svc._model_sonnet
        assert svc._select_model("auto") == svc._model_haiku
        assert svc._select_model("simple") == svc._model_haiku

    def test_api_key_from_env(self):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-env-key"}, clear=True):
            svc = AnthropicClaudeService()
            assert svc._api_key == "sk-env-key"

    @pytest.mark.asyncio
    async def test_call_timeout_error(self):
        """Simulate the internal call timing out."""
        svc = AnthropicClaudeService(api_key="sk-test")

        class SlowMessages:
            @staticmethod
            def create(*args, **kwargs):
                import time
                time.sleep(10)
                return type('R', (), {'content': [type('C', (), {'text': ''})]})()

        class SlowClient:
            messages = SlowMessages()

        with patch.object(svc, '_get_client', return_value=SlowClient()):
            with pytest.raises(RuntimeError, match="Claude did not respond"):
                await svc.call(
                    [{"role": "user", "content": "hi"}],
                    timeout=0.001,
                )

    @pytest.mark.asyncio
    async def test_call_api_error(self):
        """Simulate an API error during call."""
        svc = AnthropicClaudeService(api_key="sk-test")

        class ErrorMessages:
            @staticmethod
            def create(*args, **kwargs):
                raise Exception("API failure")

        class ErrorClient:
            messages = ErrorMessages()

        with patch.object(svc, '_get_client', return_value=ErrorClient()):
            with pytest.raises(RuntimeError, match="Claude API error"):
                await svc.call([{"role": "user", "content": "hi"}])

    @pytest.mark.asyncio
    async def test_cost_accumulation(self):
        """Verify cost tracking accumulates across calls."""
        svc = AnthropicClaudeService(api_key="sk-test")

        class MockUsage:
            input_tokens = 100
            output_tokens = 50

        class MockResponse:
            class Content:
                text = "response text"
            content = [Content()]
            usage = MockUsage()

        class MockMessages:
            @staticmethod
            def create(*args, **kwargs):
                return MockResponse()

        class MockClient:
            messages = MockMessages()

        with patch.object(svc, '_get_client', return_value=MockClient()):
            result = await svc.call([{"role": "user", "content": "hi"}])
            assert "response text" in result.text
            stats = svc.get_cost_stats()
            assert stats.input_tokens == 100
            assert stats.output_tokens == 50
            assert stats.total_cost > 0


class TestServiceInterfaceContracts:
    """Verify that all abstract methods are defined."""

    def test_claude_service_interface(self):
        methods = ["call", "get_cost_stats", "reset_cost_stats"]
        for m in methods:
            assert hasattr(ClaudeService, m)

    def test_gemini_service_interface(self):
        assert hasattr(GeminiService, "research")

    def test_woocommerce_service_interface(self):
        methods = [
            "health_check",
            "read_file",
            "write_file",
            "list_directory",
            "deploy",
            "rollback",
            "test_ssh",
        ]
        for m in methods:
            assert hasattr(WooCommerceService, m)

    def test_notification_service_interface(self):
        assert hasattr(NotificationService, "send_alert")
