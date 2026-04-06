"""
Structured logging configuration for the AI Model service.

Industry standard: structured JSON logging in production,
human-readable colored output in development.

Usage:
    from app.core.logging_config import configure_logging
    configure_logging(app_env="development")
"""
from __future__ import annotations

import logging
import os
import sys
from typing import Literal


def configure_logging(
    app_env: Literal["development", "production", "testing"] | None = None,
    log_level: str | None = None,
) -> None:
    """
    Configure application-wide logging.

    Args:
        app_env: Environment name. Auto-detected from APP_ENV env var if None.
        log_level: Override log level. Auto-selected by environment if None.
    """
    env = app_env or os.getenv("APP_ENV", "development")

    # Select log level
    if log_level:
        level = getattr(logging, log_level.upper(), logging.INFO)
    elif env == "production":
        level = logging.WARNING
    elif env == "testing":
        level = logging.ERROR
    else:
        level = logging.INFO

    # Select format
    if env == "production":
        # Structured format for log aggregation (ELK, CloudWatch, etc.)
        fmt = (
            '{"time":"%(asctime)s","level":"%(levelname)s",'
            '"logger":"%(name)s","message":"%(message)s"}'
        )
        datefmt = "%Y-%m-%dT%H:%M:%S%z"
    else:
        # Human-readable for development
        fmt = "%(asctime)s [%(levelname)-8s] %(name)-30s: %(message)s"
        datefmt = "%H:%M:%S"

    # Configure root logger
    logging.basicConfig(
        level=level,
        format=fmt,
        datefmt=datefmt,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,  # Override any previous basicConfig
    )

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        f"Logging configured: env={env}, level={logging.getLevelName(level)}"
    )
