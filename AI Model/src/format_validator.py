"""
5-Dimensional Format Validation Engine.

Validates document authenticity by scoring across 5 independent dimensions:
  1. Layout Similarity   (30%): Text block arrangement, field positions.
  2. Field Presence      (25%): Required fields exist in the document.
  3. Typography Match    (15%): Font heuristics, text formatting cues.
  4. Security Features   (20%): Watermarks, seals, QR codes.
  5. Data Format         (10%): Regex validation of dates, IDs, grades.

Each dimension returns a score in [0.0, 1.0]; the weighted combination
gives the overall confidence. Documents scoring ≥ 0.95 pass validation.

Design Pattern: Strategy (implements DocumentAnalyzer interface).
"""
from __future__ import annotations

import logging
import re
from typing import Any

from PIL import Image

from src.interfaces import (
    DocumentAnalyzer,
    DocumentType,
    FormatValidationResult,
    ValidationDimension,
)
from src.utils.cache import TTLCache
from src.utils.image_utils import detect_qr_codes, detect_seal_stamp, detect_watermark

logger = logging.getLogger(__name__)


# ─── Required fields per document type (Open/Closed: extend here) ────────────
_REQUIRED_FIELDS: dict[DocumentType, list[str]] = {
    DocumentType.MARKSHEET: [
        "name", "roll_number", "enrollment_number", "subject",
        "marks", "grade", "sgpa", "cgpa", "result",
    ],
    DocumentType.SEMESTER_RESULT: [
        "name", "roll_number", "sgpa", "cgpa", "result_status",
        "semester", "examination",
    ],
    DocumentType.PROVISIONAL_CERTIFICATE: [
        "name", "roll_number", "degree", "date", "institution",
    ],
    DocumentType.DEGREE_CERTIFICATE: [
        "name", "degree", "date", "institution", "convocation",
    ],
    DocumentType.ID_CARD: [
        "name", "photo", "id_number", "valid",
    ],
    DocumentType.TRANSCRIPT: [
        "name", "id_number", "course", "grades", "credits",
    ],
    DocumentType.MIGRATION_CERTIFICATE: [
        "name", "institution", "date", "migration",
    ],
    DocumentType.UNKNOWN: [
        "name", "id_number",
    ],
}

# ─── Date format patterns ────────────────────────────────────
_DATE_PATTERNS = [
    r"\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}",       # DD/MM/YYYY or MM/DD/YYYY
    r"\d{4}[/\-.]\d{1,2}[/\-.]\d{1,2}",           # YYYY-MM-DD
    r"\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{4}",  # 15 January 2024
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2},?\s+\d{4}",  # January 15, 2024
]

# ─── ID pattern templates ────────────────────────────────────
_ID_PATTERNS = [
    r"[A-Z]{2,5}[-/]?\d{4,12}",               # e.g. EN/20190001
    r"\d{4}[A-Z]{2,4}\d{3,6}",                # e.g. 2019BCS0045
    r"\d{2,4}[-/]\d{2,4}[-/]\d{2,6}",         # e.g. 19/EC/045
    r"\d{6,15}",                                # Pure numeric roll
]


class FormatValidator(DocumentAnalyzer):
    """
    Multi-dimensional format validation engine.

    Scores document authenticity across 5 orthogonal dimensions
    and returns a weighted overall confidence.
    """

    # Dimension weights (must sum to 1.0)
    LAYOUT_WEIGHT = 0.30
    FIELD_WEIGHT = 0.25
    TYPOGRAPHY_WEIGHT = 0.15
    SECURITY_WEIGHT = 0.20
    DATA_FORMAT_WEIGHT = 0.10

    def __init__(self, confidence_threshold: float = 0.95, cache: TTLCache | None = None):
        """
        Args:
            confidence_threshold: Minimum overall score to mark as authentic.
            cache: Optional TTLCache for validation results.
        """
        self.confidence_threshold = confidence_threshold
        self._cache = cache or TTLCache(max_size=100, ttl_seconds=300)

    @property
    def analyzer_name(self) -> str:
        return "FormatValidator"

    def analyze(
        self,
        image: Image.Image,
        extracted_text: str = "",
        extracted_fields: dict[str, Any] | None = None,
    ) -> FormatValidationResult:
        """
        Run 5-dimensional format validation.

        Args:
            image: PIL Image of the document.
            extracted_text: Raw OCR text.
            extracted_fields: Parsed structured fields (including doc_type info).

        Returns:
            FormatValidationResult with per-dimension scores.
        """
        fields = extracted_fields or {}
        doc_type = self._infer_doc_type(fields)
        text_lower = extracted_text.lower()

        # Run each dimension
        layout_dim = self._validate_layout(image, text_lower)
        field_dim = self._validate_field_presence(text_lower, fields, doc_type)
        typo_dim = self._validate_typography(text_lower)
        security_dim = self._validate_security_features(image)
        data_dim = self._validate_data_format(text_lower, fields)

        dimensions = [layout_dim, field_dim, typo_dim, security_dim, data_dim]

        # Calculate weighted overall score
        overall = sum(d.score * d.weight for d in dimensions)
        is_authentic = overall >= self.confidence_threshold

        result = FormatValidationResult(
            is_authentic=is_authentic,
            overall_confidence=round(overall, 4),
            dimensions=dimensions,
        )

        logger.info(
            f"FormatValidator: overall={overall:.4f}, authentic={is_authentic}, "
            f"scores={result.validation_scores}"
        )
        return result

    # ────────────────────────────────────────────────────────
    # Dimension 1: Layout Similarity (30%)
    # ────────────────────────────────────────────────────────

    def _validate_layout(self, image: Image.Image, text: str) -> ValidationDimension:
        """
        Analyze document layout structure.

        Checks:
          - Image aspect ratio is reasonable for a document.
          - Text density (documents have substantial text).
          - Presence of tabular structure (rows/columns).
          - Header/footer regions (institution names at top).
        """
        score = 0.0
        details_parts = []

        # Check aspect ratio (academic docs are typically portrait A4-ish)
        w, h = image.size
        aspect = w / max(h, 1)
        if 0.5 <= aspect <= 1.5:
            score += 0.25
            details_parts.append(f"aspect_ratio={aspect:.2f} (valid)")
        elif 0.3 <= aspect <= 2.0:
            score += 0.15
            details_parts.append(f"aspect_ratio={aspect:.2f} (borderline)")
        else:
            details_parts.append(f"aspect_ratio={aspect:.2f} (unusual)")

        # Text density: documents should have reasonable text
        word_count = len(text.split())
        if word_count >= 100:
            score += 0.25
            details_parts.append(f"word_count={word_count} (rich)")
        elif word_count >= 30:
            score += 0.15
            details_parts.append(f"word_count={word_count} (moderate)")
        else:
            score += 0.05
            details_parts.append(f"word_count={word_count} (sparse)")

        # Tabular structure detection (rows with aligned numbers/delimiters)
        table_pattern = re.findall(r"\d+\s+\d+\s+\d+", text)
        if len(table_pattern) >= 3:
            score += 0.25
            details_parts.append(f"table_rows={len(table_pattern)}")
        elif len(table_pattern) >= 1:
            score += 0.10
            details_parts.append(f"table_rows={len(table_pattern)} (partial)")

        # Header presence (first 200 chars should contain institution-like text)
        header = text[:200]
        header_keywords = ["university", "institute", "college", "board", "academy", "school"]
        if any(kw in header for kw in header_keywords):
            score += 0.25
            details_parts.append("header_institution=detected")
        else:
            score += 0.05
            details_parts.append("header_institution=not_found")

        return ValidationDimension(
            name="layout_similarity",
            score=round(min(score, 1.0), 4),
            weight=self.LAYOUT_WEIGHT,
            details="; ".join(details_parts),
        )

    # ────────────────────────────────────────────────────────
    # Dimension 2: Field Presence (25%)
    # ────────────────────────────────────────────────────────

    def _validate_field_presence(
        self, text: str, fields: dict[str, Any], doc_type: DocumentType
    ) -> ValidationDimension:
        """
        Check if required fields for the document type are present.
        """
        required = _REQUIRED_FIELDS.get(doc_type, _REQUIRED_FIELDS[DocumentType.UNKNOWN])

        found = 0
        missing: list[str] = []

        for field_name in required:
            # Check in both extracted_fields and raw text
            field_found = False

            # Check extracted fields (flatten nested structures)
            if self._field_exists_in_dict(fields, field_name):
                field_found = True
            elif field_name.lower() in text:
                field_found = True

            if field_found:
                found += 1
            else:
                missing.append(field_name)

        total = max(len(required), 1)
        score = found / total

        details = f"found={found}/{total}"
        if missing:
            details += f"; missing=[{', '.join(missing[:5])}]"

        return ValidationDimension(
            name="field_presence",
            score=round(score, 4),
            weight=self.FIELD_WEIGHT,
            details=details,
        )

    # ────────────────────────────────────────────────────────
    # Dimension 3: Typography Match (15%)
    # ────────────────────────────────────────────────────────

    def _validate_typography(self, text: str) -> ValidationDimension:
        """
        Analyze typography signals in the text.

        Heuristics (from OCR text features):
          - Title case headers (institution names).
          - Consistent formatting (all-caps for headers, mixed for body).
          - Numeric consistency in marks/grades.
        """
        score = 0.0
        details_parts = []

        # Check for all-caps headers (common in Indian academic docs)
        lines = text.split("\n") if "\n" in text else text.split("  ")
        uppercase_lines = sum(1 for line in lines if line.strip().isupper() and len(line.strip()) > 5)
        if uppercase_lines >= 2:
            score += 0.35
            details_parts.append(f"uppercase_headers={uppercase_lines}")
        elif uppercase_lines >= 1:
            score += 0.20
            details_parts.append(f"uppercase_headers={uppercase_lines}")

        # Check for consistent number formatting (marks columns)
        number_patterns = re.findall(r"\b\d{1,3}\b", text)
        if len(number_patterns) >= 10:
            score += 0.30
            details_parts.append(f"numeric_fields={len(number_patterns)}")
        elif len(number_patterns) >= 5:
            score += 0.15
            details_parts.append(f"numeric_fields={len(number_patterns)}")

        # Check for grade patterns (A+, B, O, etc.)
        grade_patterns = re.findall(r"\b[A-O][+\-]?\b", text)
        if len(grade_patterns) >= 3:
            score += 0.20
            details_parts.append(f"grade_patterns={len(grade_patterns)}")

        # Check for structured delimiters (colons, pipes, dashes used as separators)
        delimiter_count = text.count(":") + text.count("|") + text.count("─")
        if delimiter_count >= 5:
            score += 0.15
            details_parts.append(f"delimiters={delimiter_count}")

        return ValidationDimension(
            name="typography_match",
            score=round(min(score, 1.0), 4),
            weight=self.TYPOGRAPHY_WEIGHT,
            details="; ".join(details_parts) if details_parts else "insufficient_data",
        )

    # ────────────────────────────────────────────────────────
    # Dimension 4: Security Features (20%)
    # ────────────────────────────────────────────────────────

    def _validate_security_features(self, image: Image.Image) -> ValidationDimension:
        """
        Detect security features: watermarks, seals/stamps, QR codes.
        """
        score = 0.0
        details_parts = []

        # Watermark detection
        watermark = detect_watermark(image)
        if watermark["detected"]:
            score += 0.35
            details_parts.append(f"watermark=detected({watermark['confidence']:.2f})")
        else:
            score += 0.10  # Some score even without watermark (not all docs have one)
            details_parts.append("watermark=not_detected")

        # Seal/stamp detection
        seal = detect_seal_stamp(image)
        if seal["detected"]:
            score += 0.35
            details_parts.append(f"seal=detected(count={seal['count']})")
        else:
            score += 0.05
            details_parts.append("seal=not_detected")

        # QR code detection
        qr_codes = detect_qr_codes(image)
        if qr_codes:
            score += 0.30
            details_parts.append(f"qr_codes={len(qr_codes)}")
        else:
            score += 0.05
            details_parts.append("qr_codes=none")

        return ValidationDimension(
            name="security_features",
            score=round(min(score, 1.0), 4),
            weight=self.SECURITY_WEIGHT,
            details="; ".join(details_parts),
        )

    # ────────────────────────────────────────────────────────
    # Dimension 5: Data Format Validation (10%)
    # ────────────────────────────────────────────────────────

    def _validate_data_format(self, text: str, fields: dict[str, Any]) -> ValidationDimension:
        """
        Validate data formats using regex patterns.

        Checks:
          - Dates match known formats.
          - Roll/enrollment numbers match known patterns.
          - GPA values are in valid ranges.
          - Marks are numeric and within range.
        """
        checks_passed = 0
        checks_total = 0
        details_parts = []

        # Date validation
        checks_total += 1
        date_found = any(re.search(pat, text, re.IGNORECASE) for pat in _DATE_PATTERNS)
        if date_found:
            checks_passed += 1
            details_parts.append("date_format=valid")
        else:
            details_parts.append("date_format=not_found")

        # ID/Roll number validation
        checks_total += 1
        id_found = any(re.search(pat, text) for pat in _ID_PATTERNS)
        if id_found:
            checks_passed += 1
            details_parts.append("id_format=valid")
        else:
            details_parts.append("id_format=not_found")

        # GPA validation (SGPA/CGPA should be 0.0–10.0)
        gpa_match = re.findall(r"[sc]gpa\s*[:=]?\s*(\d+\.?\d*)", text)
        if gpa_match:
            checks_total += 1
            valid_gpas = all(0 <= float(g) <= 10.0 for g in gpa_match)
            if valid_gpas:
                checks_passed += 1
                details_parts.append(f"gpa_range=valid({','.join(gpa_match)})")
            else:
                details_parts.append(f"gpa_range=INVALID({','.join(gpa_match)})")

        # Marks validation (should be numeric, 0–100 or 0–1000)
        marks_matches = re.findall(r"\b(\d{1,3})\s*/\s*(\d{2,3})\b", text)
        if marks_matches:
            checks_total += 1
            valid_marks = all(
                0 <= int(obtained) <= int(total)
                for obtained, total in marks_matches
            )
            if valid_marks:
                checks_passed += 1
                details_parts.append(f"marks_range=valid({len(marks_matches)} subjects)")
            else:
                details_parts.append("marks_range=INVALID")

        # Percentage validation
        pct_matches = re.findall(r"(\d{1,3}\.\d+)\s*%", text)
        if pct_matches:
            checks_total += 1
            valid_pct = all(0 <= float(p) <= 100 for p in pct_matches)
            if valid_pct:
                checks_passed += 1
                details_parts.append(f"percentage=valid({','.join(pct_matches)})")
            else:
                details_parts.append(f"percentage=INVALID({','.join(pct_matches)})")

        score = checks_passed / max(checks_total, 1)

        return ValidationDimension(
            name="data_format",
            score=round(score, 4),
            weight=self.DATA_FORMAT_WEIGHT,
            details="; ".join(details_parts),
        )

    # ────────────────────────────────────────────────────────
    # Helpers
    # ────────────────────────────────────────────────────────

    @staticmethod
    def _infer_doc_type(fields: dict[str, Any]) -> DocumentType:
        """Infer document type from classification data in fields."""
        doc_type_str = fields.get("_doc_type", "")
        if isinstance(doc_type_str, str):
            try:
                return DocumentType(doc_type_str)
            except ValueError:
                pass
        return DocumentType.UNKNOWN

    @staticmethod
    def _field_exists_in_dict(d: dict[str, Any], field_name: str) -> bool:
        """Recursively check if a field name exists with a non-empty value."""
        for key, value in d.items():
            if field_name in key.lower():
                if value is not None and value != "" and value != []:
                    return True
            if isinstance(value, dict):
                if FormatValidator._field_exists_in_dict(value, field_name):
                    return True
            if isinstance(value, list) and len(value) > 0:
                return True
        return False
