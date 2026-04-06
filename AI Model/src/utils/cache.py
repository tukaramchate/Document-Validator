"""
TTL-based in-memory cache for expensive computations.

Features:
  - Time-to-live (TTL) expiration for each entry.
  - Max-size eviction (oldest entries first).
  - Thread-safe via threading.Lock.
  - Content-hash based keys for image caching.

Use cases:
  - Cache Gemini API responses for identical images.
  - Cache institution registry lookups.
  - Cache CNN inference results for the same input.
"""
from __future__ import annotations

import hashlib
import logging
import threading
import time
from collections import OrderedDict
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)
T = TypeVar("T")


class TTLCache:
    """
    Thread-safe TTL cache with ordered eviction.

    Usage:
        cache = TTLCache(max_size=100, ttl_seconds=300)
        cache.set("key", value)
        result = cache.get("key")  # Returns None if expired or missing.
    """

    def __init__(self, max_size: int = 100, ttl_seconds: float = 300.0):
        """
        Args:
            max_size: Maximum number of cached entries.
            ttl_seconds: Time-to-live for each entry in seconds.
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        """
        Retrieve a cached value if it exists and has not expired.

        Args:
            key: Cache key.

        Returns:
            Cached value, or None if missing/expired.
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            value, timestamp = self._cache[key]

            if time.monotonic() - timestamp > self.ttl_seconds:
                # Entry has expired — remove it
                del self._cache[key]
                self._misses += 1
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return value

    def set(self, key: str, value: Any) -> None:
        """
        Store a value in the cache.

        Args:
            key: Cache key.
            value: Value to cache.
        """
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = (value, time.monotonic())

            # Evict oldest entries if over capacity
            while len(self._cache) > self.max_size:
                evicted_key, _ = self._cache.popitem(last=False)
                logger.debug(f"Cache evicted key: {evicted_key[:32]}...")

    def invalidate(self, key: str) -> bool:
        """Remove a specific key from the cache. Returns True if key existed."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    @property
    def stats(self) -> dict[str, Any]:
        """Return cache hit/miss statistics."""
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total, 4) if total > 0 else 0.0,
        }

    def __repr__(self) -> str:
        return f"TTLCache(size={len(self._cache)}/{self.max_size}, ttl={self.ttl_seconds}s)"


def compute_image_hash(image_bytes: bytes) -> str:
    """
    Compute a SHA-256 hash of image bytes for cache keying.

    Args:
        image_bytes: Raw bytes of the image.

    Returns:
        Hex digest string.
    """
    return hashlib.sha256(image_bytes).hexdigest()


