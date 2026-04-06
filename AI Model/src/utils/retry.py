"""
Retry decorator with exponential backoff and jitter.

Implements a configurable retry mechanism for transient failures
(network timeouts, rate limits, temporary API errors).

Features:
  - Exponential backoff: delay doubles each retry.
  - Full jitter: randomized delay prevents thundering herd.
  - Selective retry: only retries on specified exception types.
  - Callback: optional on_retry hook for logging / metrics.
"""
from __future__ import annotations

import functools
import logging
import random
import time
from typing import Any, Callable, Sequence, Type, TypeVar

from src.exceptions import RetryExhaustedError

logger = logging.getLogger(__name__)
T = TypeVar("T")


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Sequence[Type[Exception]] = (Exception,),
    on_retry: Callable[[int, Exception, float], None] | None = None,
) -> Callable:
    """
    Decorator that retries a function on transient failures.

    Args:
        max_retries: Maximum number of retry attempts (0 = no retries).
        base_delay: Initial delay in seconds before first retry.
        max_delay: Maximum delay cap in seconds.
        exponential_base: Multiplier for exponential backoff.
        jitter: If True, adds randomized jitter to prevent thundering herd.
        retryable_exceptions: Tuple of exception types that trigger a retry.
        on_retry: Optional callback(attempt, exception, delay) called before each retry.

    Returns:
        Decorated function with retry logic.

    Raises:
        RetryExhaustedError: When all attempts are exhausted.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Exception | None = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except tuple(retryable_exceptions) as exc:
                    last_exception = exc

                    if attempt >= max_retries:
                        break

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)

                    # Add full jitter: uniform random between 0 and calculated delay
                    if jitter:
                        delay = random.uniform(0, delay)

                    if on_retry:
                        on_retry(attempt + 1, exc, delay)
                    else:
                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for {func.__qualname__} "
                            f"after {delay:.2f}s. Error: {exc!r}"
                        )

                    time.sleep(delay)

            raise RetryExhaustedError(
                operation=func.__qualname__,
                attempts=max_retries + 1,
                last_error=last_exception,
            )

        return wrapper


    return decorator

