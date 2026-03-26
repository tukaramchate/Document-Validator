import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import ocr, forge, pipeline
from app.core.config import setup_services
from src.pipeline import DocumentValidator


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the CNN model once at startup and share via app.state."""
    setup_services()
    validator = DocumentValidator()
    validator.load_model()
    app.state.validator = validator
    logging.getLogger(__name__).info("DocumentValidator loaded and ready.")
    yield
    # Cleanup (if needed) goes here
    logging.getLogger(__name__).info("AI Model API shutting down.")


app = FastAPI(
    title="Document Validator API",
    description="Unified API for OCR text extraction and visual forgery detection",
    version="2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])
app.include_router(forge.router, prefix="/api/forge", tags=["Forge Detection"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["Pipeline"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Document Validator API v2.0"}
