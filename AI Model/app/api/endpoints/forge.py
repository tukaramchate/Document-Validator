from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
import os
import tempfile
import pathlib
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def _detect_sync(validator, image_path: str) -> dict:
    """Synchronous forge detection — runs in a thread pool."""
    result = validator.validate(image_path)
    return result.get("cnn_result", {})


@router.post("/detect/")
async def detect_forgery(request: Request, file: UploadFile = File(...)):
    if not file.content_type or not (
        file.content_type.startswith("image/") or file.content_type == "application/pdf"
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Only image and PDF files are supported. Received: {file.content_type}",
        )

    suffix = pathlib.Path(file.filename).suffix if file.filename else ".jpg"
    content = await file.read()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(content)
        temp_path = temp_file.name

    # Retrieve shared validator from app state (loaded once at startup)
    validator = request.app.state.validator

    try:
        # Fix P0: run synchronous CNN inference in thread pool
        cnn_result = await run_in_threadpool(_detect_sync, validator, temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return JSONResponse(content=cnn_result)
