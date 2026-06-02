"""Unit tests for core/ package structure."""

from core import __version__ as core_version


def test_core_version():
    assert core_version == "2.0.0"


def test_core_models_importable():
    from core.models import (
        ChatRequest,
        ChatResponse,
        WorkerTaskRequest,
        StatusResponse,
        TelegramUpdate,
        HealthMetrics,
        OperationState,
        SessionState,
    )
    assert ChatRequest is not None
    assert WorkerTaskRequest is not None
    assert TelegramUpdate is not None
    assert OperationState is not None


def test_core_services_importable():
    from core.services import (
        ClaudeService,
        GeminiService,
        WooCommerceService,
        NotificationService,
        ServiceRegistry,
        AnthropicClaudeService,
        DefaultGeminiService,
        get_registry,
        reset_registry,
    )
    assert ClaudeService is not None
    assert ServiceRegistry is not None
    assert AnthropicClaudeService is not None
