import os
import json
import re
import logging
from PIL import Image
import google.generativeai as genai

logger = logging.getLogger(__name__)

# ─── Poppler path from environment (P2 fix) ──────────────────────
_DEFAULT_POPPLER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "poppler", "Library", "bin"
)
POPPLER_PATH = os.getenv("POPPLER_PATH", _DEFAULT_POPPLER)

# The specific prompt defined in the architecture plan
EXTRACTION_PROMPT = """
You are an expert OCR and information extraction system for educational certificates and marksheets.
First check: Is this image an educational certificate or marksheet?
(It must clearly show academic info: name, id number, course, branch, grades, etc.)

If it is NOT an educational certificate/marksheet (e.g. a photo, ID card, bill, receipt),
return ONLY this exact JSON, nothing else:
{"error": "Please upload an educational certificate or marksheet."}

If it IS an educational certificate/marksheet, extract these fields:
- name
- id_number (Roll Number / Reg No)
- course
- branch
- year
- cgpa
- sgpa
- certificate_id
- institution
- date

Return ONLY a valid JSON object with exactly those keys (in lowercase).
If a field is not found, set its value to null.
Do NOT include markdown, code fences, or any explanation text.
Return raw JSON only.
"""


def get_genai_model():
    """Initialize and return the Gemini model."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your_gemini_api_key_here':
        logger.warning("Gemini API key not configured. OCR extraction will fail.")
        return None

    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')


def extract_text(image_path):
    """
    Extracts text and structured fields from an image using Gemini.
    Return shape:
    {
        "raw_text": str,
        "fields": dict,
        "confidence": float
    }
    """
    model = get_genai_model()
    if not model:
        return {
            "raw_text": "",
            "fields": {"error": "API Key missing"},
            "confidence": 0.0
        }

    try:
        if image_path.lower().endswith('.pdf'):
            try:
                from pdf2image import convert_from_path
                # P2 fix: use env-based POPPLER_PATH
                pages = convert_from_path(image_path, poppler_path=POPPLER_PATH)
                if not pages:
                    raise ValueError("No pages found in PDF")
                img = pages[0].convert('RGB')
            except ImportError:
                return {
                    "raw_text": "",
                    "fields": {"error": "pdf2image package missing. Cannot process PDFs."},
                    "confidence": 0.0
                }
        else:
            img = Image.open(image_path)
    except Exception as e:
        logger.error(f"Cannot open image/PDF: {e}")
        return {"raw_text": "", "fields": {"error": f"Invalid file: {e}"}, "confidence": 0.0}

    logger.info(f"Sending image ({img.size}, {img.mode}) to Gemini OCR...")

    try:
        response = model.generate_content([EXTRACTION_PROMPT, img])
    except Exception as e:
        err_str = str(e)
        logger.error(f"Gemini API error: {err_str[:200]}")
        if "429" in err_str or "quota" in err_str.lower():
            return {
                "raw_text": "",
                "fields": {"error": "Gemini API quota exceeded. Please check billing or try again later."},
                "confidence": 0.0
            }
        return {"raw_text": "", "fields": {"error": f"API error: {err_str[:200]}"}, "confidence": 0.0}

    raw = response.text.strip()

    # Parse the JSON response
    parsed_fields = {}

    # Clean up markdown code fences if present
    cleaned_raw = raw
    if "```" in cleaned_raw:
        cleaned_raw = re.sub(r"```(?:json)?\s*", "", cleaned_raw).strip()
        cleaned_raw = cleaned_raw.rstrip("`").strip()

    try:
        parsed_fields = json.loads(cleaned_raw)
    except json.JSONDecodeError:
        # Fallback regex extraction
        match = re.search(r"\{.*\}", cleaned_raw, re.DOTALL)
        if match:
            try:
                parsed_fields = json.loads(match.group())
            except json.JSONDecodeError:
                pass

        if not parsed_fields:
            logger.error(f"Failed to parse JSON from Gemini response:\n{raw}")
            parsed_fields = {"error": "Could not parse AI response."}

    # Gemini OCR usually implies high confidence if parsing succeeds
    confidence = 0.95 if "error" not in parsed_fields else 0.0

    # Check if Gemini returned our specific error JSON
    if parsed_fields.get("error") == "Please upload an educational certificate or marksheet.":
        confidence = 0.0

    return {
        "raw_text": raw,
        "fields": parsed_fields,
        "confidence": confidence
    }
