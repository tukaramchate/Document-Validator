"""
Document Classification Module.

Classifies academic documents into types (marksheet, certificate, ID, etc.)
and sub-types (semester-wise, consolidated, etc.) using keyword analysis
and structural pattern matching.

Design Pattern: Strategy (implements DocumentAnalyzer interface).
Algorithm:
  1. Analyze extracted text for document-type keywords.
  2. Check structural signals (table presence, grade patterns, photo presence).
  3. Score each document type using weighted keyword frequency.
  4. Return classification with confidence.
"""
from __future__ import annotations

import logging
import re
from typing import Any

from PIL import Image

from src.interfaces import (
    ClassificationResult,
    DocumentAnalyzer,
    DocumentSubType,
    DocumentType,
)
from src.utils.cache import TTLCache

logger = logging.getLogger(__name__)


# ─── Keyword dictionaries for classification (Open/Closed: add new types here) ──
_TYPE_KEYWORDS: dict[DocumentType, list[str]] = {
    DocumentType.MARKSHEET: [
        "marksheet", "marks sheet", "statement of marks", "grade sheet",
        "grade card", "marks obtained", "max marks", "total marks",
        "subject code", "internal marks", "external marks",
        "marks statement", "result cum marksheet",
    ],
    DocumentType.SEMESTER_RESULT: [
        "semester result", "result declaration", "examination result",
        "result notification", "sgpa", "cgpa", "grade point average",
        "semester examination", "examination held in", "result of",
    ],
    DocumentType.PROVISIONAL_CERTIFICATE: [
        "provisional certificate", "provisional degree",
        "provisionally passed", "eligible for the degree",
        "hereby certified that", "has passed the",
        "provisional", "this is to certify",
    ],
    DocumentType.DEGREE_CERTIFICATE: [
        "degree certificate", "convocation", "conferred upon",
        "bachelor of", "master of", "doctor of",
        "has been awarded", "awarded the degree",
        "diploma in", "post graduate", "under graduate",
    ],
    DocumentType.MIGRATION_CERTIFICATE: [
        "migration certificate", "migration", "no objection",
        "hereby permitted", "migrate", "transfer certificate",
    ],
    DocumentType.ID_CARD: [
        "identity card", "student id", "id card", "enrollment card",
        "library card", "photo identity", "valid upto", "valid till",
        "blood group",
    ],
    DocumentType.TRANSCRIPT: [
        "transcript", "academic transcript", "official transcript",
        "record of courses", "cumulative record",
        "credit hours", "semester-wise",
    ],
}

_SUBTYPE_KEYWORDS: dict[DocumentSubType, list[str]] = {
    DocumentSubType.SEMESTER_WISE: [
        "semester", "sem", "first semester", "second semester",
        "odd semester", "even semester", "semester examination",
    ],
    DocumentSubType.YEARLY: [
        "annual", "yearly", "year examination", "first year",
        "second year", "third year", "fourth year", "final year",
    ],
    DocumentSubType.CONSOLIDATED: [
        "consolidated", "cumulative", "all semesters",
        "overall", "aggregate",
    ],
    DocumentSubType.SUPPLEMENTARY: [
        "supplementary", "reappear", "re-examination",
        "back paper", "improvement", "compartment",
    ],
    DocumentSubType.DUPLICATE: [
        "duplicate", "second copy", "reissue", "re-issue",
    ],
    DocumentSubType.ORIGINAL: [
        "original",
    ],
}


class DocumentClassifier(DocumentAnalyzer):
    """
    Classifies academic documents by type and sub-type.

    Uses weighted keyword frequency analysis with structural signals.
    Follows the Single Responsibility Principle: only performs classification.
    """

    def __init__(self, cache: TTLCache | None = None):
        """
        Args:
            cache: Optional TTLCache for classification results.
        """
        self._cache = cache or TTLCache(max_size=200, ttl_seconds=600)

    @property
    def analyzer_name(self) -> str:
        return "DocumentClassifier"

    def analyze(
        self,
        image: Image.Image,
        extracted_text: str = "",
        extracted_fields: dict[str, Any] | None = None,
    ) -> ClassificationResult:
        """
        Classify the document type and sub-type.

        Args:
            image: PIL Image of the document.
            extracted_text: Raw OCR text.
            extracted_fields: Previously extracted fields.

        Returns:
            ClassificationResult with type, sub-type, and confidence.
        """
        text_corpus = self._build_corpus(extracted_text, extracted_fields)

        if not text_corpus.strip():
            logger.warning("DocumentClassifier: No text available for classification")
            return ClassificationResult()

        # Check cache
        cache_key = f"cls:{hash(text_corpus)}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        # Score each document type
        type_scores = self._score_types(text_corpus)
        subtype_scores = self._score_subtypes(text_corpus)

        # Add structural signals
        structural_hints = self._analyze_structure(text_corpus, extracted_fields)
        for doc_type, bonus in structural_hints.items():
            if doc_type in type_scores:
                type_scores[doc_type] += bonus

        # Find best type
        best_type = DocumentType.UNKNOWN
        best_type_score = 0.0
        for doc_type, score in type_scores.items():
            if score > best_type_score:
                best_type = doc_type
                best_type_score = score

        # Find best sub-type
        best_subtype = DocumentSubType.UNKNOWN
        best_subtype_score = 0.0
        for sub_type, score in subtype_scores.items():
            if score > best_subtype_score:
                best_subtype = sub_type
                best_subtype_score = score

        # Calculate confidence (normalize to 0–1)
        total_keywords_checked = sum(len(kws) for kws in _TYPE_KEYWORDS.values())
        confidence = min(best_type_score / max(total_keywords_checked * 0.1, 1), 1.0)

        # Boost confidence if type is clearly detected
        if best_type_score >= 3:
            confidence = max(confidence, 0.85)
        if best_type_score >= 5:
            confidence = max(confidence, 0.95)

        # Build reasoning
        reasoning_parts = [f"Type '{best_type.value}' matched {best_type_score:.0f} keyword signals"]
        if best_subtype != DocumentSubType.UNKNOWN:
            reasoning_parts.append(f"Sub-type '{best_subtype.value}' matched {best_subtype_score:.0f} signals")

        result = ClassificationResult(
            primary_type=best_type,
            sub_type=best_subtype,
            confidence_score=round(confidence, 4),
            reasoning="; ".join(reasoning_parts),
        )

        self._cache.set(cache_key, result)

        logger.info(
            f"DocumentClassifier: {result.primary_type.value}/{result.sub_type.value} "
            f"(confidence={result.confidence_score:.4f})"
        )
        return result

    def _build_corpus(self, raw_text: str, fields: dict[str, Any] | None) -> str:
        """Combine available text, normalize for matching."""
        parts = [raw_text]
        if fields:
            for key, value in fields.items():
                if isinstance(value, str):
                    parts.append(value)
                elif isinstance(value, dict):
                    for v in value.values():
                        if isinstance(v, str):
                            parts.append(v)
        text = " ".join(parts).lower()
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _score_types(corpus: str) -> dict[DocumentType, float]:
        """Score each document type based on keyword frequency."""
        scores: dict[DocumentType, float] = {}
        for doc_type, keywords in _TYPE_KEYWORDS.items():
            score = 0.0
            for kw in keywords:
                if kw in corpus:
                    # Exact phrase match is worth more than individual words
                    score += 1.0
                    # Bonus for multiple occurrences
                    count = corpus.count(kw)
                    if count > 1:
                        score += 0.3 * (count - 1)
            scores[doc_type] = score
        return scores

    @staticmethod
    def _score_subtypes(corpus: str) -> dict[DocumentSubType, float]:
        """Score each sub-type based on keyword frequency."""
        scores: dict[DocumentSubType, float] = {}
        for sub_type, keywords in _SUBTYPE_KEYWORDS.items():
            score = 0.0
            for kw in keywords:
                if kw in corpus:
                    score += 1.0
            scores[sub_type] = score
        return scores

    @staticmethod
    def _analyze_structure(corpus: str, fields: dict[str, Any] | None) -> dict[DocumentType, float]:
        """
        Analyze structural patterns that hint at document type.

        Returns bonus scores for each type.
        """
        hints: dict[DocumentType, float] = {}

        # Marksheet indicators: grades table, marks columns
        has_marks = bool(re.search(r"\b\d{1,3}\s*/\s*\d{2,3}\b", corpus))  # e.g. "85/100"
        if has_marks:
            hints[DocumentType.MARKSHEET] = 2.0

        # SGPA/CGPA patterns → marksheet or result
        has_gpa = bool(re.search(r"\b[sc]gpa\s*[:=]?\s*\d+\.?\d*\b", corpus))
        if has_gpa:
            hints[DocumentType.MARKSHEET] = hints.get(DocumentType.MARKSHEET, 0) + 1.5
            hints[DocumentType.SEMESTER_RESULT] = hints.get(DocumentType.SEMESTER_RESULT, 0) + 1.0

        # Percentage pattern
        has_percentage = bool(re.search(r"\b\d{1,3}\.\d+\s*%\b", corpus))
        if has_percentage:
            hints[DocumentType.MARKSHEET] = hints.get(DocumentType.MARKSHEET, 0) + 0.5

        # Grade table (rows of subject-grade pairs)
        if fields:
            grades = fields.get("grades", [])
            if isinstance(grades, list) and len(grades) > 0:
                hints[DocumentType.MARKSHEET] = hints.get(DocumentType.MARKSHEET, 0) + 3.0

        # ID card indicators: photo, blood group, valid date
        has_blood_group = bool(re.search(r"blood\s*group", corpus))
        has_valid_date = bool(re.search(r"valid\s*(upto|till|from)", corpus))
        if has_blood_group or has_valid_date:
            hints[DocumentType.ID_CARD] = hints.get(DocumentType.ID_CARD, 0) + 2.0

        return hints
