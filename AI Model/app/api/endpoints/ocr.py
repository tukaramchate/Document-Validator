from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
import logging
import os
import tempfile
import pathlib

from src.ocr.text_extractor import extract_text

router = APIRouter()
logger = logging.getLogger(__name__)


def _extract_sync(image_path: str) -> dict:
    """Synchronous OCR extraction — runs in a thread pool."""
    result = extract_text(image_path)
    return result.get("fields", {})


@router.post("/extract/")
async def extract_certificate(file: UploadFile = File(...)):
    if not file.content_type or not (
        file.content_type.startswith("image/") or file.content_type == "application/pdf"
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Only image and PDF files are supported. Received: {file.content_type}",
        )

    image_bytes = await file.read()
    suffix = pathlib.Path(file.filename).suffix if file.filename else ".jpg"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(image_bytes)
        temp_path = temp_file.name

    try:
        # Fix P0: run synchronous Gemini call in thread pool to avoid blocking event loop
        result = await run_in_threadpool(_extract_sync, temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return JSONResponse(content=result)
