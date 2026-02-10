"""
Tests for Phase 2: Circuit Breaker & Per-Store Isolation.

Covers:
- CircuitBreaker state machine (CLOSED → OPEN → HALF_OPEN → CLOSED)
- Failure threshold triggers OPEN
- Recovery timeout triggers HALF_OPEN
- Probe success in HALF_OPEN closes the circuit
- Probe failure in HALF_OPEN re-opens the circuit
- Registry: get_breaker, get_all_breakers, reset_breaker
- SSH orchestrator integration (CircuitOpenError on read_file/write_file)
- REST health check integration
- /worker/health exposes circuit breaker state
"""

import time
import pytest
from unittest.mock import patch, MagicMock

from agent.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    CircuitOpenError,
    get_breaker,
    get_all_breakers,
    reset_breaker,
    _breakers,
    _registry_lock,
)


# ================================================================
# 1. CircuitBreaker State Machine
# ================================================================


class TestCircuitBreakerStateMachine:

    def _make_breaker(self, threshold=3, timeout=1.0):
        return CircuitBreaker(failure_threshold=threshold, recovery_timeout=timeout)

    def test_initial_state_is_closed(self):
        cb = self._make_breaker()
        assert cb.state == CircuitState.CLOSED

    def test_call_permitted_when_closed(self):
        cb = self._make_breaker()
        assert cb.is_call_permitted() is True

    def test_stays_closed_under_threshold(self):
        cb = self._make_breaker(threshold=3)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        assert cb.is_call_permitted() is True

    def test_opens_at_threshold(self):
        cb = self._make_breaker(threshold=3)
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.is_call_permitted() is False

    def test_success_resets_failure_count(self):
        cb = self._make_breaker(threshold=3)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        assert cb.failure_count == 0
        assert cb.state == CircuitState.CLOSED

    def test_open_rejects_calls(self):
        cb = self._make_breaker(threshold=1)
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.is_call_permitted() is False

    def test_open_transitions_to_half_open_after_timeout(self):
        cb = self._make_breaker(threshold=1, timeout=0.1)
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        time.sleep(0.15)
        assert cb.state == CircuitState.HALF_OPEN

    def test_half_open_allows_one_probe(self):
        cb = self._make_breaker(threshold=1, timeout=0.1)
        cb.record_failure()
        time.sleep(0.15)
        assert cb.state == CircuitState.HALF_OPEN
        assert cb.is_call_permitted() is True
        # Second call should be rejected (only 1 probe allowed)
        assert cb.is_call_permitted() is False

    def test_half_open_success_closes_circuit(self):
        cb = self._make_breaker(threshold=1, timeout=0.1)
        cb.record_failure()
        time.sleep(0.15)
        assert cb.state == CircuitState.HALF_OPEN
        cb.is_call_permitted()  # consume probe slot
        cb.record_success()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_half_open_failure_reopens_circuit(self):
        cb = self._make_breaker(threshold=1, timeout=0.1)
        cb.record_failure()
        time.sleep(0.15)
        assert cb.state == CircuitState.HALF_OPEN
        cb.is_call_permitted()  # consume probe slot
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_manual_reset(self):
        cb = self._make_breaker(threshold=1)
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        cb.reset()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_to_dict_snapshot(self):
        cb = self._make_breaker(threshold=3, timeout=120.0)
        info = cb.to_dict()
        assert info["state"] == "closed"
        assert info["failure_count"] == 0
        assert info["failure_threshold"] == 3
        assert info["recovery_timeout"] == 120.0

    def test_to_dict_open_shows_remaining_time(self):
        cb = self._make_breaker(threshold=1, timeout=60.0)
        cb.record_failure()
        info = cb.to_dict()
        assert info["state"] == "open"
        assert info["seconds_until_half_open"] > 0


# ================================================================
# 2. Registry Functions
# ================================================================


class TestRegistry:

    def setup_method(self):
        """Clear registry before each test."""
        with _registry_lock:
            _breakers.clear()

    def test_get_breaker_creates_new(self):
        cb = get_breaker("test_key")
        assert isinstance(cb, CircuitBreaker)
        assert cb.state == CircuitState.CLOSED

    def test_get_breaker_returns_same_instance(self):
        cb1 = get_breaker("same_key")
        cb2 = get_breaker("same_key")
        assert cb1 is cb2

    def test_get_all_breakers(self):
        get_breaker("a")
        get_breaker("b")
        all_b = get_all_breakers()
        assert "a" in all_b
        assert "b" in all_b
        assert all_b["a"]["state"] == "closed"

    def test_reset_breaker_existing(self):
        cb = get_breaker("reset_me")
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert reset_breaker("reset_me") is True
        assert cb.state == CircuitState.CLOSED

    def test_reset_breaker_nonexistent(self):
        assert reset_breaker("does_not_exist") is False


# ================================================================
# 3. CircuitOpenError
# ================================================================


class TestCircuitOpenError:

    def test_error_contains_key(self):
        cb = CircuitBreaker(failure_threshold=1)
        cb.record_failure()
        err = CircuitOpenError("ssh", cb)
        assert "ssh" in str(err)
        assert "OPEN" in str(err)

    def test_error_attributes(self):
        cb = CircuitBreaker(failure_threshold=1)
        cb.record_failure()
        err = CircuitOpenError("ssh", cb)
        assert err.key == "ssh"
        assert err.breaker is cb


# ================================================================
# 4. SSH Orchestrator Integration
# ================================================================


class TestSSHOrchestratorCircuitBreaker:
    """Verify read_file and write_file honor the SSH circuit breaker."""

    def setup_method(self):
        with _registry_lock:
            _breakers.clear()

    def test_read_file_raises_circuit_open(self):
        """When SSH circuit is open, read_file should raise CircuitOpenError immediately."""
        from agent.tools import ssh_orchestrator

        # Trip the breaker
        cb = get_breaker("ssh")
        for _ in range(cb.failure_threshold):
            cb.record_failure()
        assert cb.state == CircuitState.OPEN

        with patch.object(ssh_orchestrator, "read_file_ssh") as mock_ssh:
            with pytest.raises(CircuitOpenError):
                ssh_orchestrator.read_file("style.css")
            mock_ssh.assert_not_called()

    def test_write_file_raises_circuit_open(self):
        """When SSH circuit is open, write_file should raise CircuitOpenError immediately."""
        from agent.tools import ssh_orchestrator

        cb = get_breaker("ssh")
        for _ in range(cb.failure_threshold):
            cb.record_failure()

        with patch.object(ssh_orchestrator, "write_file_ssh") as mock_ssh:
            with pytest.raises(CircuitOpenError):
                ssh_orchestrator.write_file("style.css", "body{}", operation_id="op1", chat_id="c1")
            mock_ssh.assert_not_called()

    def test_read_file_records_success_on_good_read(self):
        """Successful read should record success on the breaker."""
        from agent.tools import ssh_orchestrator

        with _registry_lock:
            _breakers.clear()

        with patch.object(ssh_orchestrator, "validate_operation", return_value=(True, "", False)):
            with patch.object(ssh_orchestrator, "get_path_type_ssh", return_value="file"):
                with patch.object(ssh_orchestrator, "read_file_ssh", return_value="content"):
                    with patch.object(ssh_orchestrator, "log_event"):
                        result = ssh_orchestrator.read_file("style.css")

        assert result == "content"
        cb = get_breaker("ssh")
        assert cb.failure_count == 0

    def test_read_file_records_failure_on_ssh_error(self):
        """SSH errors during read should increment the breaker failure count."""
        from agent.tools import ssh_orchestrator

        with _registry_lock:
            _breakers.clear()

        with patch.object(ssh_orchestrator, "validate_operation", return_value=(True, "", False)):
            with patch.object(ssh_orchestrator, "get_path_type_ssh", side_effect=OSError("connection refused")):
                with pytest.raises(OSError):
                    ssh_orchestrator.read_file("style.css")

        cb = get_breaker("ssh")
        assert cb.failure_count >= 1


# ================================================================
# 5. REST Health Check Integration
# ================================================================


class TestHealthCheckCircuitBreaker:

    def setup_method(self):
        with _registry_lock:
            _breakers.clear()

    @pytest.mark.asyncio
    async def test_health_check_wordpress_records_success(self):
        """Successful health check should record success on the breaker."""
        import httpx
        from unittest.mock import AsyncMock
        from agent.tools.rest import health_check_wordpress

        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_async_client
        mock_async_client.get.return_value = mock_response

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await health_check_wordpress("https://example.com", timeout=5)

        assert result["healthy"] is True
        cb = get_breaker("http:https://example.com")
        assert cb.failure_count == 0

    @pytest.mark.asyncio
    async def test_health_check_wordpress_records_failure(self):
        """Failed health check should increment breaker failure count."""
        import httpx
        from unittest.mock import AsyncMock
        from agent.tools.rest import health_check_wordpress

        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value = mock_async_client
        mock_async_client.get.side_effect = httpx.ConnectError("refused")

        with patch("httpx.AsyncClient", return_value=mock_async_client):
            result = await health_check_wordpress("https://down.example.com", timeout=5)

        assert result["healthy"] is False
        cb = get_breaker("http:https://down.example.com")
        assert cb.failure_count == 1

    @pytest.mark.asyncio
    async def test_health_check_circuit_open_fast_rejects(self):
        """When HTTP circuit is open, health check should return immediately."""
        from agent.tools.rest import health_check_wordpress

        # Trip the breaker
        cb = get_breaker("http:https://tripped.example.com")
        for _ in range(cb.failure_threshold):
            cb.record_failure()

        with patch("httpx.AsyncClient") as mock_client_class:
            result = await health_check_wordpress("https://tripped.example.com", timeout=5)
            mock_client_class.assert_not_called()

        assert result["healthy"] is False
        assert "Circuit breaker" in result["error"]


# ================================================================
# 6. /worker/health Endpoint
# ================================================================


class TestWorkerHealthCircuitBreakers:

    def setup_method(self):
        with _registry_lock:
            _breakers.clear()

    @pytest.mark.asyncio
    async def test_worker_health_includes_circuit_breakers(self):
        from interfaces.api import app
        from httpx import AsyncClient, ASGITransport

        # Create a breaker so the response has something to show
        get_breaker("ssh")

        with patch("interfaces.api.test_ssh_connection", return_value=(True, "OK")):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                resp = await client.get("/worker/health")

        assert resp.status_code == 200
        data = resp.json()
        assert "circuit_breakers" in data
        assert "ssh" in data["circuit_breakers"]
        assert data["circuit_breakers"]["ssh"]["state"] == "closed"

    @pytest.mark.asyncio
    async def test_worker_health_degraded_when_circuit_open(self):
        from interfaces.api import app
        from httpx import AsyncClient, ASGITransport

        cb = get_breaker("ssh")
        for _ in range(cb.failure_threshold):
            cb.record_failure()

        with patch("interfaces.api.test_ssh_connection", return_value=(True, "OK")):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                resp = await client.get("/worker/health")

        data = resp.json()
        assert data["status"] == "degraded"
        assert data["circuit_breakers"]["ssh"]["state"] == "open"
