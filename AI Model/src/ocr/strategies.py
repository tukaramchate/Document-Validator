"""
OCR Extraction Strategies (Strategy Pattern).

Provides swappable extraction backends:
  - GeminiExtractionStrategy: Primary — uses Google Gemini API.
  - RegexFallbackStrategy: Secondary — regex-based fallback.

Each strategy implements the ExtractionStrategy interface.
The pipeline selects the strategy at runtime (primary → fallback chain).
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

import google.generativeai as genai
from PIL import Image

from src.exceptions import (
    GeminiAPIError,
    GeminiQuotaExceededError,
    NonAcademicDocumentError,
    ResponseParsingError,
)
from src.interfaces import ExtractionResult, ExtractionStrategy
from src.utils.cache import TTLCache, compute_image_hash
from src.utils.circuit_breaker import CircuitBreaker
from src.utils.retry import retry_with_backoff

logger = logging.getLogger(__name__)


# ─── Enhanced extraction prompt for the full nested schema ──────────────────
ENHANCED_EXTRACTION_PROMPT = """You are an expert OCR and information extraction system for educational documents (marksheets, certificates, results, transcripts, ID cards).

**Step 1 — Document Check**
Is this image an academic/educational document? It must clearly show academic information such as student name, ID numbers, course details, grades/marks, or institutional affiliation.

If it is NOT an educational document (e.g., a personal photo, bill, receipt, random image), return ONLY this exact JSON:
{"error": "NOT_ACADEMIC_DOCUMENT"}

**Step 2 — Extraction**
If it IS an educational document, extract ALL available information into this exact JSON schema. Set any field to null if not found. Do NOT fabricate data.

{
  "student_info": {
    "name": "Full name of the student",
    "roll_number": "Roll number or registration number",
    "enrollment_number": "Enrollment number (if different from roll)",
    "father_name": "Father's or guardian's name",
    "mother_name": "Mother's name (if available)",
    "date_of_birth": "YYYY-MM-DD format (or null)",
    "course": "Degree/program name (e.g., B.Tech, M.Sc)",
    "branch": "Branch/specialization (e.g., Computer Science)",
    "semester": "Semester number (if applicable)",
    "year_of_study": "Year of study (if applicable)",
    "academic_year": "Academic year (e.g., 2023-24)"
  },
  "institution_info": {
    "name": "Full name of the university/college/board",
    "abbreviation": "Short form (e.g., IIT, NIT, CBSE)",
    "city": "City (if visible)",
    "state": "State (if visible)"
  },
  "grades": [
    {
      "subject_code": "Subject code (e.g., CS301)",
      "subject_name": "Full subject name",
      "credits": null,
      "marks_obtained": null,
      "max_marks": null,
      "grade": "Letter grade (e.g., A+, B)",
      "grade_point": null
    }
  ],
  "results": {
    "sgpa": null,
    "cgpa": null,
    "percentage": null,
    "total_marks_obtained": null,
    "total_max_marks": null,
    "result_status": "Pass/Fail/Distinction/etc.",
    "division": "First/Second/Third (if applicable)"
  },
  "verification_info": {
    "issue_date": "YYYY-MM-DD or original format",
    "certificate_number": "Certificate/document serial number",
    "qr_code_data": "Data from any QR code (if visible)",
    "examination_month_year": "Month and year of examination"
  }
}

**Rules:**
- Return ONLY valid JSON. No markdown fences, no explanation text, no commentary.
- For the 'grades' array: include ALL subjects visible, even if some fields are null.
- For marks, use integers. For GPA values, use floats with up to 2 decimal places.
- Dates should be in YYYY-MM-DD format when possible.
- If the document is in a regional language AND English, prefer extracting the English text.
- Do NOT guess or hallucinate values — use null for fields you cannot find.
"""


class GeminiExtractionStrategy(ExtractionStrategy):
    """
    Primary extraction strategy using Google Gemini API.

    Features:
      - Structured prompt for nested JSON extraction.
      - Retry with exponential backoff (3 attempts).
      - Circuit breaker to prevent cascade failures.
      - Response caching by image content hash.
      - Robust JSON parsing with markdown fence handling.
    """

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        cache: TTLCache | None = None,
        circuit_breaker: CircuitBreaker | None = None,
    ):
        """
        Args:
            model_name: Gemini model to use.
            cache: TTLCache for response caching.
            circuit_breaker: CircuitBreaker for API protection.
        """
        self._model_name = model_name
        self._cache = cache or TTLCache(max_size=50, ttl_seconds=600)
        self._circuit_breaker = circuit_breaker or CircuitBreaker(
            service_name="gemini_api",
            failure_threshold=5,
            recovery_timeout=60.0,
        )
        self._model: Any = None

    @property
    def strategy_name(self) -> str:
        return f"GeminiExtraction({self._model_name})"

    def _get_model(self) -> Any:
        """Lazy-init the Gemini model."""
        if self._model is None:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key or api_key == "your_gemini_api_key_here":
                raise GeminiAPIError("GEMINI_API_KEY not configured", status_code=None)
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel(self._model_name)
        return self._model

    def extract(self, image: Image.Image, context: dict[str, Any] | None = None) -> ExtractionResult:
        """
        Extract structured data from an image using Gemini API.

        Args:
            image: PIL Image to process.
            context: Optional context (unused currently, reserved for future prompt tuning).

        Returns:
            ExtractionResult with parsed fields.

        Raises:
            GeminiAPIError: On API failures after retries.
            NonAcademicDocumentError: If document is not academic.
        """
        # Check cache by image content hash
        import io
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=85)
        image_bytes = buf.getvalue()
        cache_key = f"gemini:{compute_image_hash(image_bytes)}"

        cached = self._cache.get(cache_key)
        if cached is not None:
            logger.info("GeminiExtraction: Cache HIT")
            return cached

        # Call Gemini API through circuit breaker + retry
        raw_text, parsed_fields = self._call_gemini_with_retry(image)

        # Check for non-academic document
        if parsed_fields.get("error") == "NOT_ACADEMIC_DOCUMENT":
            raise NonAcademicDocumentError()

        # Determine confidence
        confidence = self._calculate_confidence(parsed_fields)

        result = ExtractionResult(
            fields=parsed_fields,
            raw_text=raw_text,
            confidence=confidence,
            strategy_name=self.strategy_name,
            metadata={"model": self._model_name, "cached": False},
        )

        # Cache successful result
        self._cache.set(cache_key, result)

        return result

    def _call_gemini_with_retry(self, image: Image.Image) -> tuple[str, dict[str, Any]]:
        """Call Gemini API with retry logic and circuit breaker."""

        @retry_with_backoff(
            max_retries=3,
            base_delay=1.0,
            max_delay=30.0,
            retryable_exceptions=(Exception,),
        )
        def _inner_call() -> tuple[str, dict[str, Any]]:
            model = self._get_model()

            def _api_call():
                return model.generate_content([ENHANCED_EXTRACTION_PROMPT, image])

            response = self._circuit_breaker.call(_api_call)
            raw = response.text.strip()
            parsed = self._parse_response(raw)
            return raw, parsed

        try:
            return _inner_call()
        except Exception as exc:
            err_str = str(exc)
            if "429" in err_str or "quota" in err_str.lower():
                raise GeminiQuotaExceededError() from exc
            raise GeminiAPIError(
                f"Gemini API call failed: {err_str[:200]}",
                retries_exhausted=True,
            ) from exc

    @staticmethod
    def _parse_response(raw_text: str) -> dict[str, Any]:
        """
        Parse Gemini response text into a structured dict.

        Handles:
          - Clean JSON responses.
          - Responses wrapped in markdown code fences.
          - Partial JSON extraction via regex.
        """
        cleaned = raw_text

        # Strip markdown code fences
        if "```" in cleaned:
            cleaned = re.sub(r"```(?:json)?\s*", "", cleaned).strip()
            cleaned = cleaned.rstrip("`").strip()

        # Try direct JSON parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Try extracting the first JSON object
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        raise ResponseParsingError(raw_text, reason="No valid JSON found in response")

    @staticmethod
    def _calculate_confidence(fields: dict[str, Any]) -> float:
        """
        Estimate extraction confidence based on field completeness.

        Higher confidence when more fields have non-null values.
        """
        if "error" in fields:
            return 0.0

        filled = 0
        total = 0

        # Count top-level sections
        for key in ("student_info", "institution_info", "grades", "results", "verification_info"):
            value = fields.get(key)
            total += 1
            if value:
                if isinstance(value, dict):
                    non_null = sum(1 for v in value.values() if v is not None)
                    section_total = len(value)
                    if non_null > 0:
                        filled += non_null / max(section_total, 1)
                elif isinstance(value, list) and len(value) > 0:
                    filled += 1

        confidence = filled / max(total, 1)

        # Gemini extraction is generally reliable when it returns data
        # Minimum confidence of 0.7 if we got structured data at all
        if confidence > 0:
            confidence = max(confidence, 0.70)

        return round(min(confidence, 1.0), 4)


class RegexFallbackStrategy(ExtractionStrategy):
    """
    Fallback extraction strategy using regex patterns on raw text.

    Used when Gemini API is unavailable (circuit breaker OPEN, quota exceeded).
    Maps to the same nested schema format as GeminiExtractionStrategy.
    """

    @property
    def strategy_name(self) -> str:
        return "RegexFallback"

    def extract(self, image: Image.Image, context: dict[str, Any] | None = None) -> ExtractionResult:
        """
        Extract data from raw text using regex patterns.

        Note: This strategy requires raw_text in the context dict.
        It cannot perform OCR on its own — it only parses pre-extracted text.

        Args:
            image: PIL Image (unused — this strategy works on text only).
            context: Must contain 'raw_text' key.

        Returns:
            ExtractionResult with regex-parsed fields.
        """
        raw_text = (context or {}).get("raw_text", "")

        if not raw_text:
            return ExtractionResult(
                fields={"error": "No raw text available for fallback extraction"},
                raw_text="",
                confidence=0.0,
                strategy_name=self.strategy_name,
            )

        fields = self._parse_with_regex(raw_text)

        # Calculate confidence based on how many fields were extracted
        filled_count = self._count_filled_fields(fields)
        confidence = min(filled_count * 0.1, 0.75)  # Cap at 0.75 for regex

        return ExtractionResult(
            fields=fields,
            raw_text=raw_text,
            confidence=round(confidence, 4),
            strategy_name=self.strategy_name,
        )

    def _parse_with_regex(self, text: str) -> dict[str, Any]:
        """Parse raw text into the nested schema using regex patterns."""
        student_info = {
            "name": self._extract_pattern(text, [
                r"(?:Name|Student Name|Candidate Name)\s*[:\-]\s*(.+)",
            ]),
            "roll_number": self._extract_pattern(text, [
                r"(?:Roll No|Roll Number|Reg No|Registration No)\s*[:\-]\s*([\w/\-]+)",
            ]),
            "enrollment_number": self._extract_pattern(text, [
                r"(?:Enrollment No|Enroll(?:ment)? Number)\s*[:\-]\s*([\w/\-]+)",
            ]),
            "father_name": self._extract_pattern(text, [
                r"(?:Father'?s? Name|S/O|D/O)\s*[:\-]\s*(.+)",
            ]),
            "mother_name": self._extract_pattern(text, [
                r"(?:Mother'?s? Name)\s*[:\-]\s*(.+)",
            ]),
            "date_of_birth": self._extract_pattern(text, [
                r"(?:Date of Birth|DOB|D\.O\.B)\s*[:\-]\s*([\d/\-\.]+)",
            ]),
            "course": self._extract_pattern(text, [
                r"(?:Course|Program|Degree)\s*[:\-]\s*(.+)",
            ]),
            "branch": self._extract_pattern(text, [
                r"(?:Branch|Specialization|Discipline|Stream)\s*[:\-]\s*(.+)",
            ]),
            "semester": self._extract_pattern(text, [
                r"(?:Semester|Sem)\s*[:\-]?\s*(\d+)",
            ]),
            "year_of_study": self._extract_pattern(text, [
                r"(?:Year)\s*[:\-]?\s*(\d+)",
            ]),
            "academic_year": self._extract_pattern(text, [
                r"(\d{4}\s*[-–]\s*\d{2,4})",
            ]),
        }

        institution_info = {
            "name": self._extract_institution(text),
            "abbreviation": None,
            "city": None,
            "state": None,
        }

        results = {
            "sgpa": self._extract_float(text, [r"SGPA\s*[:\-=]\s*([\d.]+)"]),
            "cgpa": self._extract_float(text, [r"CGPA\s*[:\-=]\s*([\d.]+)"]),
            "percentage": self._extract_float(text, [r"(\d{1,3}\.\d+)\s*%"]),
            "total_marks_obtained": None,
            "total_max_marks": None,
            "result_status": self._extract_pattern(text, [
                r"(?:Result|Status)\s*[:\-]\s*(Pass|Fail|Passed|Failed|Distinction)",
            ]),
            "division": self._extract_pattern(text, [
                r"(?:Division|Class)\s*[:\-]\s*(First|Second|Third|Distinction)",
            ]),
        }

        verification_info = {
            "issue_date": self._extract_pattern(text, [
                r"(?:Date of Issue|Issue Date|Issued on|Date)\s*[:\-]\s*([\d/\-\.]+)",
            ]),
            "certificate_number": self._extract_pattern(text, [
                r"(?:Certificate (?:No|Number|ID)|Serial No|Ref No)\s*[:\-]\s*([\w/\-]+)",
            ]),
            "qr_code_data": None,
            "examination_month_year": self._extract_pattern(text, [
                r"(?:Examination held in|Exam Month)\s*[:\-]?\s*(\w+\s+\d{4})",
            ]),
        }

        return {
            "student_info": student_info,
            "institution_info": institution_info,
            "grades": [],  # Regex can't reliably parse grade tables
            "results": results,
            "verification_info": verification_info,
        }

    @staticmethod
    def _extract_pattern(text: str, patterns: list[str]) -> str | None:
        """Try each pattern and return the first match."""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        return None

    @staticmethod
    def _extract_float(text: str, patterns: list[str]) -> float | None:
        """Extract a float value using regex patterns."""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        return None

    @staticmethod
    def _extract_institution(text: str) -> str | None:
        """Try to extract institution name from text."""
        patterns = [
            r"([\w\s]+ (?:University|Institute of Technology|College|Board))",
            r"(?:Institution|University|College)\s*[:\-]\s*(.+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    @staticmethod
    def _count_filled_fields(fields: dict[str, Any], depth: int = 0) -> int:
        """Count non-null fields recursively."""
        if depth > 3:
            return 0
        count = 0
        for value in fields.values():
            if isinstance(value, dict):
                count += RegexFallbackStrategy._count_filled_fields(value, depth + 1)
            elif isinstance(value, list):
                count += len(value)
            elif value is not None:
                count += 1
        return count
