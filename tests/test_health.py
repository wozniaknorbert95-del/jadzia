"""Tests for health monitoring."""

import pytest
from httpx import ASGITransport, AsyncClient

from interfaces.api import app


@pytest.mark.asyncio
async def test_health_endpoint_returns_200():
    """GET /worker/health should return 200."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/worker/health")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint_structure():
    """Health endpoint should return required fields."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/worker/health")
        data = response.json()

        assert "status" in data
        assert "active_sessions" in data
        assert "active_tasks" in data
        assert "queue_length" in data
        assert "ssh_connection" in data
        assert "errors_last_hour" in data

        assert data["status"] in ["healthy", "degraded", "unhealthy"]


@pytest.mark.asyncio
async def test_health_shows_ssh_status():
    """Health should test SSH connection."""
    from unittest.mock import patch

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("interfaces.api.test_ssh_connection", return_value=(True, "OK")):
            response = await client.get("/worker/health")
            data = response.json()

            assert data["ssh_connection"] == "ok"
