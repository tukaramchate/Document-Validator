"""
Application-level middleware for the Document Validator AI API.

Provides:
  - Request ID injection (X-Request-ID header).
  - Request timing (X-Response-Time header).
  - Structured request/response logging.
  - Rate limiting placeholder hooks.
"""
from __future__ import annotations

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("app.middleware")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Injects a unique request ID and measures response time.

    Every request gets:
      - X-Request-ID header (UUID4, generated or forwarded).
      - X-Response-Time header (milliseconds).

    Logs method, path, status, and duration for observability.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Extract or generate request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.monotonic()

        try:
            response = await call_next(request)
        except Exception:
            # Let FastAPI's exception handlers deal with it;
            # we just ensure timing is logged.
            duration_ms = (time.monotonic() - start_time) * 1000
            logger.error(
                f"{request.method} {request.url.path} -> 500 "
                f"({duration_ms:.1f}ms) [rid={request_id}]"
            )
            raise

        duration_ms = (time.monotonic() - start_time) * 1000

        # Attach headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"

        # Log — skip noisy health checks
        if request.url.path != "/health":
            logger.info(
                f"{request.method} {request.url.path} -> {response.status_code} "
                f"({duration_ms:.1f}ms) [rid={request_id}]"
            )

        return response
