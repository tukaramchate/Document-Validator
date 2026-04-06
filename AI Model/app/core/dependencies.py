"""
Dependency Injection container for FastAPI endpoints.

Provides reusable dependencies following the Dependency Inversion principle.
Endpoints declare what they need via `Depends(...)` — the DI container
supplies concrete instances without tight coupling.

Usage in endpoints:
    @router.post("/full/")
    async def validate(validator: DocumentValidator = Depends(get_validator)):
        ...
"""
from __future__ import annotations

from fastapi import Request

from src.pipeline import DocumentValidator


def get_validator(request: Request) -> DocumentValidator:
    """
    Dependency: returns the shared DocumentValidator from app state.

    Loaded once at startup in the lifespan manager.
    Thread-safe because DocumentValidator instances are read-only after init.

    Raises:
        RuntimeError: If the validator was not loaded at startup.
    """
    validator = getattr(request.app.state, "validator", None)
    if validator is None:
        raise RuntimeError(
            "DocumentValidator is not available. "
            "This usually means the application startup failed."
        )
    return validator


def get_request_id(request: Request) -> str:
    """
    Dependency: returns the current request ID.

    Injected by RequestContextMiddleware into request.state.
    Falls back to 'unknown' if middleware is not configured.
    """
    return getattr(request.state, "request_id", "unknown")
