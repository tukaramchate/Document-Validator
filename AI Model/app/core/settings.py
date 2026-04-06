"""
Application settings with environment-based configuration.

Uses Pydantic BaseSettings for type-safe configuration loading
from environment variables and .env files.

Follows the 12-factor app methodology: configuration via environment.
"""
from __future__ import annotations

import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables take precedence over .env file values.
    Prefix: none (direct env var names for backward compatibility).
    """

    # ─── General ─────────────────────────────────────────
    app_env: str = Field("development", alias="APP_ENV")
    app_name: str = "Document Validator AI API"
    app_version: str = "3.0"
    debug: bool = False

    # ─── Gemini API ──────────────────────────────────────
    gemini_api_key: str = Field("", alias="GEMINI_API_KEY")
    gemini_model: str = Field("gemini-2.5-flash", alias="GEMINI_MODEL")
    gemini_timeout: int = Field(60, alias="GEMINI_TIMEOUT_SECONDS")

    # ─── CNN Model ───────────────────────────────────────
    cnn_model_path: str = Field(
        "saved_models/document_cnn_v1.pth",
        alias="CNN_MODEL_PATH",
    )

    # ─── Poppler (PDF conversion) ────────────────────────
    poppler_path: str = Field("poppler/Library/bin", alias="POPPLER_PATH")

    # ─── Server ──────────────────────────────────────────
    host: str = Field("0.0.0.0", alias="HOST")
    port: int = Field(8001, alias="PORT")

    # ─── Resilience ──────────────────────────────────────
    circuit_breaker_threshold: int = Field(5, alias="CB_FAILURE_THRESHOLD")
    circuit_breaker_timeout: float = Field(60.0, alias="CB_RECOVERY_TIMEOUT")
    retry_max_attempts: int = Field(3, alias="RETRY_MAX_ATTEMPTS")
    retry_base_delay: float = Field(1.0, alias="RETRY_BASE_DELAY")

    # ─── Cache ───────────────────────────────────────────
    cache_max_size: int = Field(100, alias="CACHE_MAX_SIZE")
    cache_ttl_seconds: float = Field(600.0, alias="CACHE_TTL_SECONDS")

    # ─── Validation ──────────────────────────────────────
    format_confidence_threshold: float = Field(
        0.95, alias="FORMAT_CONFIDENCE_THRESHOLD",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_testing(self) -> bool:
        return self.app_env == "testing"


@lru_cache()
def get_settings() -> AppSettings:
    """
    Cached settings singleton.

    Returns the same AppSettings instance for the lifetime of the process.
    """
    return AppSettings()
