"""
Circuit Breaker for per-store fault isolation.

Prevents a single failing store (SSH down, WordPress unreachable) from
consuming worker capacity.  Each store (identified by ``chat_id``) gets its
own breaker.  When the failure threshold is exceeded, the circuit opens and
all requests are fast-rejected until the recovery timeout expires.

States:
    CLOSED   — Normal operation.  Failures are counted.
    OPEN     — Fast-reject.  No operations attempted.  After ``recovery_timeout``
               seconds the circuit transitions to HALF_OPEN.
    HALF_OPEN — One probe request is allowed through.  On success → CLOSED.
                On failure → back to OPEN with a fresh timeout.

Thread Safety:
    All state mutations are protected by a per-breaker ``threading.Lock`` so the
    module is safe to call from both the async worker loop (via to_thread) and
    synchronous SSH retry decorators.
"""

import logging
import threading
import time
from enum import Enum
from typing import Dict, Optional

_log = logging.getLogger("agent.circuit_breaker")


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Per-key circuit breaker with configurable thresholds."""

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: float = 120.0,
        half_open_max_calls: int = 1,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float = 0.0
        self._half_open_calls = 0
        self._lock = threading.Lock()

    # ── Public API ──────────────────────────────────────────────

    @property
    def state(self) -> CircuitState:
        """Current state (auto-transitions OPEN→HALF_OPEN when timeout expires)."""
        with self._lock:
            self._maybe_transition_to_half_open()
            return self._state

    @property
    def failure_count(self) -> int:
        return self._failure_count

    def is_call_permitted(self) -> bool:
        """Check if a call should be attempted.

        Returns True if the circuit is CLOSED or HALF_OPEN (under limit).
        Returns False if OPEN (fast-reject).
        """
        with self._lock:
            self._maybe_transition_to_half_open()
            if self._state == CircuitState.CLOSED:
                return True
            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls < self.half_open_max_calls:
                    self._half_open_calls += 1
                    return True
                return False
            # OPEN
            return False

    def record_success(self) -> None:
        """Record a successful call.  Resets failure count; closes circuit if HALF_OPEN."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                _log.info("[CIRCUIT] %s: HALF_OPEN → CLOSED (probe succeeded)", id(self))
                self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count += 1
            self._half_open_calls = 0

    def record_failure(self) -> None:
        """Record a failed call.  Opens circuit if threshold exceeded."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()
            if self._state == CircuitState.HALF_OPEN:
                _log.warning(
                    "[CIRCUIT] %s: HALF_OPEN → OPEN (probe failed, count=%d)",
                    id(self), self._failure_count,
                )
                self._state = CircuitState.OPEN
                self._half_open_calls = 0
            elif self._failure_count >= self.failure_threshold:
                if self._state != CircuitState.OPEN:
                    _log.warning(
                        "[CIRCUIT] %s: CLOSED → OPEN (failures=%d >= threshold=%d)",
                        id(self), self._failure_count, self.failure_threshold,
                    )
                self._state = CircuitState.OPEN
                self._half_open_calls = 0

    def reset(self) -> None:
        """Manually reset to CLOSED (e.g. operator intervention)."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._half_open_calls = 0
            self._success_count = 0

    def to_dict(self) -> dict:
        """Snapshot for telemetry / health endpoints."""
        with self._lock:
            self._maybe_transition_to_half_open()
            remaining = 0.0
            if self._state == CircuitState.OPEN and self._last_failure_time:
                elapsed = time.monotonic() - self._last_failure_time
                remaining = max(0.0, self.recovery_timeout - elapsed)
            return {
                "state": self._state.value,
                "failure_count": self._failure_count,
                "failure_threshold": self.failure_threshold,
                "recovery_timeout": self.recovery_timeout,
                "seconds_until_half_open": round(remaining, 1),
            }

    # ── Internal ────────────────────────────────────────────────

    def _maybe_transition_to_half_open(self) -> None:
        """Must be called with self._lock held."""
        if self._state == CircuitState.OPEN and self._last_failure_time:
            elapsed = time.monotonic() - self._last_failure_time
            if elapsed >= self.recovery_timeout:
                _log.info(
                    "[CIRCUIT] %s: OPEN → HALF_OPEN (recovery timeout %.1fs elapsed)",
                    id(self), elapsed,
                )
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0


# ═══════════════════════════════════════════════════════════════
# Registry: per-key breakers for SSH and HTTP health checks
# ═══════════════════════════════════════════════════════════════

_breakers: Dict[str, CircuitBreaker] = {}
_registry_lock = threading.Lock()

# Default thresholds (configurable via env)
import os

_DEFAULT_FAILURE_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "3"))
_DEFAULT_RECOVERY_TIMEOUT = float(os.getenv("CIRCUIT_BREAKER_RECOVERY_TIMEOUT", "120"))


def get_breaker(key: str) -> CircuitBreaker:
    """Get or create a circuit breaker for the given key (e.g. 'ssh', 'http:shop_url')."""
    with _registry_lock:
        if key not in _breakers:
            _breakers[key] = CircuitBreaker(
                failure_threshold=_DEFAULT_FAILURE_THRESHOLD,
                recovery_timeout=_DEFAULT_RECOVERY_TIMEOUT,
            )
        return _breakers[key]


def get_all_breakers() -> Dict[str, dict]:
    """Snapshot of all breakers for health/telemetry endpoints."""
    with _registry_lock:
        return {key: breaker.to_dict() for key, breaker in _breakers.items()}


def reset_breaker(key: str) -> bool:
    """Manually reset a breaker. Returns True if breaker existed."""
    with _registry_lock:
        if key in _breakers:
            _breakers[key].reset()
            return True
        return False


class CircuitOpenError(Exception):
    """Raised when a call is rejected because the circuit is open."""

    def __init__(self, key: str, breaker: CircuitBreaker):
        self.key = key
        self.breaker = breaker
        super().__init__(
            f"Circuit breaker '{key}' is OPEN "
            f"(failures={breaker.failure_count}, "
            f"recovery_timeout={breaker.recovery_timeout}s)"
        )
