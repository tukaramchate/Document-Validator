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
def extract_with_gemini(image_bytes: bytes) -> dict:
    """Send image to Gemini 1.5 Flash using PIL and return extracted JSON data."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        logger.error(f"Cannot open image: {e}")
        return {"error": f"Invalid image file: {e}"}

    model = genai.GenerativeModel("gemini-2.5-flash")
    logger.info(f"Sending image ({img.size}, {img.mode}) to Gemini...")

    try:
        response = model.generate_content([EXTRACTION_PROMPT, img])
    except Exception as e:
        err_str = str(e)
        logger.error(f"Gemini API error: {err_str[:200]}")
        if "429" in err_str or "quota" in err_str.lower():
            return {
                "error": "Gemini API quota exceeded. Please enable billing on your Google AI Studio account at https://aistudio.google.com, or wait and try again later."
            }
        return {"error": f"Gemini API error: {err_str[:200]}"}

    raw = response.text.strip()
    logger.info(f"Gemini raw response (first 200 chars): {raw[:200]}")

    # Strip markdown fences if present (Gemini sometimes adds them)
    if "```" in raw:
        raw = re.sub(r"```(?:json)?\s*", "", raw).strip()
        raw = raw.rstrip("`").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try to find a JSON object anywhere in the response
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        logger.error(f"Failed to parse JSON from Gemini response:\n{raw}")
        return {"error": "Could not parse AI response. Please try again."}


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
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Only image files are supported. Received: {file.content_type}",
        )

    image_bytes = await file.read()
    logger.info(f"Received: {file.filename!r} ({file.content_type}, {len(image_bytes)} bytes)")

    result = extract_with_gemini(image_bytes)
    logger.info(f"Returning result keys: {list(result.keys())}")
    return JSONResponse(content=result)
