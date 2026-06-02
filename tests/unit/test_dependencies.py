"""Unit tests for api/dependencies.py — FastAPI DI wiring."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi import HTTPException

from api.dependencies import (
    get_service_registry,
    get_claude_service,
    get_gemini_service,
    get_woocommerce_service,
    get_notification_service,
    verify_jwt,
    JWT_SECRET,
)
from core.services import (
    AnthropicClaudeService,
    DefaultGeminiService,
    DiscordNotificationService,
    ServiceRegistry,
    reset_registry,
    set_registry,
)


class TestServiceDependencies:
    @pytest.mark.asyncio
    async def test_get_service_registry(self):
        reset_registry()
        async for reg in get_service_registry():
            assert isinstance(reg, ServiceRegistry)

    @pytest.mark.asyncio
    async def test_get_claude_service(self):
        reset_registry()
        async for reg in get_service_registry():
            svc = await get_claude_service(registry=reg)
            assert isinstance(svc, AnthropicClaudeService)

    @pytest.mark.asyncio
    async def test_get_gemini_service(self):
        reset_registry()
        async for reg in get_service_registry():
            svc = await get_gemini_service(registry=reg)
            assert isinstance(svc, DefaultGeminiService)

    @pytest.mark.asyncio
    async def test_get_notification_service(self):
        reset_registry()
        async for reg in get_service_registry():
            svc = await get_notification_service(registry=reg)
            assert isinstance(svc, DiscordNotificationService)

    @pytest.mark.asyncio
    async def test_custom_registry_used(self):
        """Verify custom registry propagates through dependencies."""
        from core.services import ClaudeService, ClaudeResponse, CostStats

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

        async for reg_iter in get_service_registry():
            svc = await get_claude_service(registry=reg_iter)
            assert svc is mock

        reset_registry()


class TestJWTAuth:
    def test_jwt_disabled_when_no_secret(self):
        with patch("api.dependencies.JWT_SECRET", None):
            import jwt
            from fastapi.security import HTTPAuthorizationCredentials

            # When JWT_SECRET is None, verify_jwt should return None without token
            import asyncio
            result = asyncio.run(verify_jwt(credentials=None))
            assert result is None

    def test_jwt_requires_token_when_secret_set(self):
        with patch("api.dependencies.JWT_SECRET", "test-secret"):
            with pytest.raises(HTTPException) as exc:
                import asyncio
                asyncio.run(verify_jwt(credentials=None))
            assert exc.value.status_code == 401
