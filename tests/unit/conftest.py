"""Shared fixtures for unit tests."""

import pytest

from core.services import reset_registry


@pytest.fixture(autouse=True)
def reset_service_registry():
    """Reset the global service registry before each test for isolation."""
    reset_registry()
    yield
    reset_registry()
