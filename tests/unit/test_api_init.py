"""Unit tests for api/ package structure."""

from api import __version__ as api_version
from api.dependencies import (
    get_service_registry,
    get_claude_service,
    verify_jwt,
)
from api.routes.chat import router as chat_router
from api.routes.health import router as health_router
from api.routes.worker import router as worker_router
from api.routes.dashboard import router as dashboard_router
from api.routes.costs import router as costs_router
from api.routes.sessions import router as sessions_router


def test_api_version():
    assert api_version == "2.0.0"


def test_dependencies_importable():
    assert get_service_registry is not None
    assert get_claude_service is not None
    assert verify_jwt is not None


def test_routers_importable():
    assert chat_router is not None
    assert health_router is not None
    assert worker_router is not None
    assert dashboard_router is not None
    assert costs_router is not None
    assert sessions_router is not None


def test_router_tags():
    assert chat_router.tags == ["chat"]
    assert health_router.tags == ["health"]
    assert worker_router.prefix == "/worker"
    assert dashboard_router.prefix == "/worker"
    assert dashboard_router.tags == ["dashboard"]
    assert sessions_router.tags == ["sessions"]
    assert costs_router.tags == ["costs"]
