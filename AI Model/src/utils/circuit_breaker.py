"""
Circuit Breaker implementation for external API calls (Gemini, etc.).

Pattern: Circuit Breaker — prevents cascading failures by short-circuiting
calls to a failing service after a configurable threshold.

States:
  CLOSED  → Normal operation; failures are counted.
  OPEN    → All calls are blocked; returns fast with CircuitBreakerOpenError.
  HALF_OPEN → A single probe call is allowed to test recovery.

Thread-safe via threading.Lock.
"""
from __future__ import annotations

import logging
import threading
import time
from enum import Enum
from typing import Any, Callable, TypeVar

from src.exceptions import CircuitBreakerOpenError

logger = logging.getLogger(__name__)
T = TypeVar("T")


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """
    Thread-safe circuit breaker for protecting external service calls.

    Usage:
        breaker = CircuitBreaker("gemini_api", failure_threshold=3, recovery_timeout=30.0)

        try:
            result = breaker.call(lambda: gemini_model.generate_content(prompt))
        except CircuitBreakerOpenError:
            # Service is down; use fallback
            result = fallback_extraction()
    """

    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        success_threshold: int = 2,
    ):
        """
        Args:
            service_name: Human-readable name for logging.
            failure_threshold: Consecutive failures before opening the circuit.
            recovery_timeout: Seconds to wait before allowing a probe call.
            success_threshold: Consecutive successes in HALF_OPEN before closing.
        """
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float = 0.0
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        with self._lock:
            if self._state == CircuitState.OPEN:
                elapsed = time.monotonic() - self._last_failure_time
                if elapsed >= self.recovery_timeout:
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
                    logger.info(
                        f"CircuitBreaker [{self.service_name}]: "
                        f"OPEN → HALF_OPEN after {elapsed:.1f}s"
                    )
            return self._state

    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Execute a function through the circuit breaker.

        Args:
            func: The callable to protect.
            *args, **kwargs: Arguments forwarded to func.

        Returns:
            The return value of func.

        Raises:
            CircuitBreakerOpenError: If the circuit is OPEN.
            Any exception raised by func (after recording the failure).
        """
        current_state = self.state

        if current_state == CircuitState.OPEN:
            retry_after = self.recovery_timeout - (time.monotonic() - self._last_failure_time)
            raise CircuitBreakerOpenError(self.service_name, max(0, retry_after))

        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as exc:
            self._record_failure(exc)
            raise

    def _record_success(self) -> None:
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    logger.info(
                        f"CircuitBreaker [{self.service_name}]: "
                        f"HALF_OPEN → CLOSED (recovered)"
                    )
            else:
                # Reset on any success in CLOSED state
                self._failure_count = 0

    def _record_failure(self, exc: Exception) -> None:
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()

            if self._state == CircuitState.HALF_OPEN:
                # Single failure in HALF_OPEN → back to OPEN
                self._state = CircuitState.OPEN
                logger.warning(
                    f"CircuitBreaker [{self.service_name}]: "
                    f"HALF_OPEN → OPEN (probe failed: {exc!r})"
                )
            elif self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN
                logger.error(
                    f"CircuitBreaker [{self.service_name}]: "
                    f"CLOSED → OPEN after {self._failure_count} failures. "
                    f"Last error: {exc!r}"
                )

    def reset(self) -> None:
        """Manually reset the circuit breaker to CLOSED state."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = 0.0
            logger.info(f"CircuitBreaker [{self.service_name}]: Manually reset to CLOSED")

    def __repr__(self) -> str:
        return (
            f"CircuitBreaker(service={self.service_name!r}, state={self._state.value}, "
            f"failures={self._failure_count}/{self.failure_threshold})"
        )
