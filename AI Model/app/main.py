"""
FastAPI application entry point for the Document Validator AI Service.

Industry-standard structure:
  - Lifespan-managed startup/shutdown (CNN model, Gemini config).
  - Middleware stack: CORS, request context (ID + timing).
  - Structured logging (JSON in production, readable in dev).
  - Global exception handler for custom exceptions.
  - Pydantic-validated health check with component status.
  - Dependency injection via FastAPI Depends().
  - Auto-generated OpenAPI 3.0 spec at /docs.
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.endpoints import forge, ocr, pipeline
from app.core.config import setup_services
from app.core.logging_config import configure_logging
from app.middleware.request_context import RequestContextMiddleware
from app.schemas.responses import ErrorResponse, HealthResponse
from src.exceptions import DocumentValidatorError
from src.pipeline import DocumentValidator


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Startup:
      1. Configure structured logging.
      2. Configure Gemini API credentials.
      3. Create DocumentValidator and load CNN model.
      4. Store validator in app.state for endpoint DI.

    Shutdown:
      - Log shutdown event for observability.
    """
    configure_logging()
    setup_services()
    logger = logging.getLogger(__name__)

    # Initialize the enhanced pipeline
    validator = DocumentValidator()
    validator.load_model()

    app.state.validator = validator
    logger.info(
        f"DocumentValidator loaded and ready. "
        f"Institutions: {validator._institution_recognizer.institution_count}"
    )

    yield

    logger.info("AI Model API shutting down.")


app = FastAPI(
    title="Document Validator AI API",
    description=(
        "Production-grade API for academic document processing:\n\n"
        "- **CNN Forgery Detection** — ResNet18 binary classifier\n"
        "- **OCR Extraction** — Google Gemini structured extraction\n"
        "- **Institution Recognition** — 100+ university registry matching\n"
        "- **Document Classification** — 7 types, 6 sub-types\n"
        "- **Format Validation** — 5-dimensional scoring engine\n\n"
        "Design patterns: Factory, Strategy, Observer, Circuit Breaker."
    ),
    version="3.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ─── Middleware Stack (order matters: bottom runs first) ────
# 1. Request context — must run first to inject request_id
app.add_middleware(RequestContextMiddleware)

# 2. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ─── Global Exception Handler ──────────────────────────────
@app.exception_handler(DocumentValidatorError)
async def document_validator_error_handler(request, exc: DocumentValidatorError):
    """Convert custom exceptions to structured JSON error responses."""
    return JSONResponse(
        status_code=500,
        content=exc.to_dict(),
    )


# ─── API Routers ────────────────────────────────────────────
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])
app.include_router(forge.router, prefix="/api/forge", tags=["Forge Detection"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["Pipeline"])


# ─── Health Check ───────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    """
    Health check endpoint with component status.

    Returns service version, CNN model state, Gemini API status,
    institution registry count, and Format Classifier status.
    """
    components = {
        "cnn_model":    "loaded" if hasattr(app.state, "validator") else "not_loaded",
        "gemini_api":   "configured" if os.getenv("GEMINI_API_KEY") else "not_configured",
        "format_model": "not_loaded",
    }

    if hasattr(app.state, "validator"):
        validator = app.state.validator
        components["cnn_mock_mode"]         = str(validator._cnn_is_mock)
        components["institutions_loaded"]   = str(validator._institution_recognizer.institution_count)
        # Format classifier
        fc = validator._format_factory
        if fc.is_loaded:
            components["format_model"]    = "loaded"
            components["format_classes"]  = ", ".join(fc.classes)
        else:
            components["format_model"]    = "not_loaded"

    return HealthResponse(
        status="ok",
        service="Document Validator AI API v3.0",
        components=components,
    )

