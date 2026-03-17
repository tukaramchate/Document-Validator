# main.py — Gemini OCR FastAPI Service
import base64
import json
import re
import os
import io
import pathlib
import logging

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

# ---------- Logging ----------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ---------- Load .env from the directory this file lives in ----------
_BASE_DIR = pathlib.Path(__file__).parent
load_dotenv(dotenv_path=_BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError(
        f"GEMINI_API_KEY not found. "
        f"Create a .env file at {_BASE_DIR / '.env'} with: GEMINI_API_KEY=your_key"
    )

genai.configure(api_key=GEMINI_API_KEY)
logger.info("Gemini API configured successfully.")

# ---------- FastAPI App ----------
app = FastAPI(
    title="Gemini OCR API",
    description="Extract educational certificate info from images using Gemini AI",
    version="1.2",
)

# ---------- CORS ----------
# IMPORTANT: allow_credentials must be False when allow_origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ---------- Prompt ----------
EXTRACTION_PROMPT = """
You are an expert OCR and information extraction system for educational certificates and marksheets.

First check: Is this image an educational certificate or marksheet?
(It must clearly show academic info: name, roll number, course, branch, grades, etc.)

If it is NOT an educational certificate/marksheet (e.g. a photo, ID card, bill, receipt),
return ONLY this exact JSON, nothing else:
{"error": "Please upload an educational certificate or marksheet."}

If it IS an educational certificate/marksheet, extract these fields:
- Name
- Roll Number
- Course
- Branch
- Year
- CGPA
- SGPA
- Certificate Id
- Institution
- Issue Date

Return ONLY a valid JSON object with exactly those keys.
If a field is not found, set its value to null.
Do NOT include markdown, code fences, or any explanation text.
Return raw JSON only.
"""


# ---------- Core Extraction ----------
import sys
import pathlib
_BASE_DIR = pathlib.Path(__file__).parent.parent
sys.path.append(str(_BASE_DIR))
from ocr.text_extractor import extract_text

def extract_with_gemini(image_path: str) -> dict:
    """Send image to Gemini 1.5 Flash via text_extractor and return extracted JSON data."""
    result = extract_text(image_path)
    if "error" in result["fields"]:
        return result["fields"] # Pass the error down
    return result["fields"]


# ---------- Health Check ----------
@app.get("/health")
async def health():
    return {"status": "ok", "service": "Gemini OCR API v1.2"}


# ---------- Main OCR Endpoint ----------
@app.post("/extract/")
async def extract_certificate(file: UploadFile = File(...)):
    """
    Upload an image (JPG, PNG, WEBP) of an educational certificate.
    Returns extracted structured data as JSON.
    """
    if not file.content_type or not (file.content_type.startswith("image/") or file.content_type == "application/pdf"):
        raise HTTPException(
            status_code=400,
            detail=f"Only image and PDF files are supported. Received: {file.content_type}",
        )

    image_bytes = await file.read()
    logger.info(f"Received: {file.filename!r} ({file.content_type}, {len(image_bytes)} bytes)")

    # Save to tempfile so extract_text (which expects a path) can read it cleanly
    import tempfile
    suffix = pathlib.Path(file.filename).suffix if file.filename else ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(image_bytes)
        temp_path = temp_file.name
        
    try:
        result = extract_with_gemini(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    logger.info(f"Returning result keys: {list(result.keys())}")
    return JSONResponse(content=result)
