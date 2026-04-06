"""
Custom exception hierarchy for the Document Validator AI pipeline.

Design: Single-responsibility exception classes grouped by subsystem.
Each exception carries structured context for logging and API responses.
"""
from __future__ import annotations

from typing import Any


class DocumentValidatorError(Exception):
    """Base exception for all AI pipeline errors."""

    def __init__(self, message: str, *, code: str = "INTERNAL_ERROR", details: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": self.code,
            "message": str(self),
            "details": self.details,
        }


# ────────────────────────────────────────────────────────────
# Image / Preprocessing Errors
# ────────────────────────────────────────────────────────────

class ImageProcessingError(DocumentValidatorError):
    """Raised when an image cannot be loaded, decoded, or preprocessed."""

    def __init__(self, message: str, *, path: str = "", details: dict[str, Any] | None = None):
        super().__init__(message, code="IMAGE_PROCESSING_ERROR", details={"path": path, **(details or {})})


class UnsupportedFileTypeError(DocumentValidatorError):
    """Raised when the uploaded file type is not supported."""

    def __init__(self, file_type: str):
        super().__init__(
            f"Unsupported file type: {file_type}",
            code="UNSUPPORTED_FILE_TYPE",
            details={"file_type": file_type, "supported": ["image/jpeg", "image/png", "application/pdf"]},
        )


# ────────────────────────────────────────────────────────────
# OCR / Extraction Errors
# ────────────────────────────────────────────────────────────

class ExtractionError(DocumentValidatorError):
    """Base class for all data extraction failures."""

    def __init__(self, message: str, *, code: str = "EXTRACTION_ERROR", details: dict[str, Any] | None = None):
        super().__init__(message, code=code, details=details)


class GeminiAPIError(ExtractionError):
    """Raised when the Gemini API returns an error or times out."""

    def __init__(self, message: str, *, status_code: int | None = None, retries_exhausted: bool = False):
        super().__init__(
            message,
            code="GEMINI_API_ERROR",
            details={"status_code": status_code, "retries_exhausted": retries_exhausted},
        )


class GeminiQuotaExceededError(GeminiAPIError):
    """Raised when the Gemini API rate limit / quota is exceeded."""

    def __init__(self):
        super().__init__(
            "Gemini API quota exceeded. Please check billing or try again later.",
            status_code=429,
            retries_exhausted=True,
        )


class ResponseParsingError(ExtractionError):
    """Raised when a Gemini response cannot be parsed into the expected schema."""

    def __init__(self, raw_response: str, reason: str = ""):
        super().__init__(
            f"Failed to parse AI response: {reason}",
            code="RESPONSE_PARSING_ERROR",
            details={"raw_response_preview": raw_response[:500]},
        )


class NonAcademicDocumentError(ExtractionError):
    """Raised when the uploaded document is not an academic document."""

    def __init__(self):
        super().__init__(
            "The uploaded image is not an academic document (marksheet, certificate, or ID).",
            code="NON_ACADEMIC_DOCUMENT",
        )


# ────────────────────────────────────────────────────────────
# Model / Inference Errors
# ────────────────────────────────────────────────────────────

class ModelNotFoundError(DocumentValidatorError):
    """Raised when a required ML model file is missing."""

    def __init__(self, model_path: str):
        super().__init__(
            f"Model file not found at: {model_path}",
            code="MODEL_NOT_FOUND",
            details={"model_path": model_path},
        )


class ModelInferenceError(DocumentValidatorError):
    """Raised when model inference fails at runtime."""

    def __init__(self, message: str, *, model_name: str = ""):
        super().__init__(
            message,
            code="MODEL_INFERENCE_ERROR",
            details={"model_name": model_name},
        )



# ────────────────────────────────────────────────────────────
# Infrastructure Errors
# ────────────────────────────────────────────────────────────

class CircuitBreakerOpenError(DocumentValidatorError):
    """Raised when a circuit breaker is in the OPEN state and calls are blocked."""

    def __init__(self, service_name: str, retry_after_seconds: float):
        super().__init__(
            f"Circuit breaker for '{service_name}' is OPEN. Retry after {retry_after_seconds:.0f}s.",
            code="CIRCUIT_BREAKER_OPEN",
            details={"service": service_name, "retry_after_seconds": retry_after_seconds},
        )


class RetryExhaustedError(DocumentValidatorError):
    """Raised when all retry attempts have been exhausted."""

    def __init__(self, operation: str, attempts: int, last_error: Exception | None = None):
        super().__init__(
            f"All {attempts} retry attempts exhausted for '{operation}'.",
            code="RETRY_EXHAUSTED",
            details={
                "operation": operation,
                "attempts": attempts,
                "last_error": str(last_error) if last_error else None,
            },
        )
