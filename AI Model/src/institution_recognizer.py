"""
Institution Recognition Module.

Identifies which university/college/board issued an academic document
by matching extracted text against the institution registry.

Design Pattern: Strategy (implements DocumentAnalyzer interface).
Algorithm:
  1. Extract text blocks from the image (via Gemini or raw_text).
  2. Normalize and tokenize.
  3. Score against each institution using multi-signal matching:
     a. Exact name match (high weight).
     b. Alias / abbreviation match.
     c. Keyword overlap.
     d. City/state context clue.
  4. Return the best match with confidence score.
"""
from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any

from PIL import Image

from src.interfaces import DocumentAnalyzer, InstitutionResult
from src.utils.cache import TTLCache

logger = logging.getLogger(__name__)

# ─── Registry path ───────────────────────────────────────────
_REGISTRY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data", "institution_registry.json",
)


@dataclass
class _MatchScore:
    """Internal scoring container for an institution match."""
    institution_id: str
    institution_name: str
    name_score: float = 0.0
    alias_score: float = 0.0
    keyword_score: float = 0.0
    context_score: float = 0.0
    aliases_matched: list[str] = field(default_factory=list)

    @property
    def weighted_score(self) -> float:
        """Weighted combination of match signals."""
        return (
            self.name_score * 0.40
            + self.alias_score * 0.30
            + self.keyword_score * 0.20
            + self.context_score * 0.10
        )


class InstitutionRecognizer(DocumentAnalyzer):
    """
    Identifies the issuing institution from document text.

    Loads institution registry once at init and caches lookup results.
    Follows the Open/Closed principle: new institutions are added by
    editing the JSON registry, not by modifying code.
    """

    def __init__(self, registry_path: str | None = None, cache: TTLCache | None = None):
        """
        Args:
            registry_path: Path to institution_registry.json.
            cache: Optional TTLCache for lookup results.
        """
        self._registry_path = registry_path or _REGISTRY_PATH
        self._cache = cache or TTLCache(max_size=200, ttl_seconds=600)
        self._institutions: list[dict[str, Any]] = []
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """Lazy-load the registry from disk."""
        if self._loaded:
            return

        try:
            with open(self._registry_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._institutions = data.get("institutions", [])
            self._loaded = True
            logger.info(
                f"InstitutionRecognizer: Loaded {len(self._institutions)} institutions "
                f"from {self._registry_path}"
            )
        except FileNotFoundError:
            logger.error(f"Institution registry not found: {self._registry_path}")
            self._institutions = []
            self._loaded = True
        except (json.JSONDecodeError, KeyError) as exc:
            logger.error(f"Invalid institution registry: {exc}")
            self._institutions = []
            self._loaded = True

    @property
    def analyzer_name(self) -> str:
        return "InstitutionRecognizer"

    def analyze(
        self,
        image: Image.Image,
        extracted_text: str = "",
        extracted_fields: dict[str, Any] | None = None,
    ) -> InstitutionResult:
        """
        Identify the issuing institution from the document.

        Args:
            image: PIL Image (used for future logo detection; currently unused).
            extracted_text: Raw OCR text from the document.
            extracted_fields: Parsed fields (may contain 'institution' key).

        Returns:
            InstitutionResult with university ID, name, and confidence.
        """
        self._ensure_loaded()

        # Build the text corpus to match against
        text_corpus = self._build_text_corpus(extracted_text, extracted_fields)

        if not text_corpus.strip():
            logger.warning("InstitutionRecognizer: No text available for matching")
            return InstitutionResult()

        # Check cache
        cache_key = f"inst:{hash(text_corpus)}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        # Score each institution
        scores: list[_MatchScore] = []
        for inst in self._institutions:
            score = self._score_institution(inst, text_corpus)
            scores.append(score)

        # Find best match
        scores.sort(key=lambda s: s.weighted_score, reverse=True)
        best = scores[0] if scores else None

        if best and best.weighted_score >= 0.15:
            # Normalize confidence to 0.0–1.0 range
            confidence = min(best.weighted_score * 1.5, 1.0)
            result = InstitutionResult(
                university_id=best.institution_id,
                university_name=best.institution_name,
                confidence_score=round(confidence, 4),
                aliases_matched=best.aliases_matched,
            )
        else:
            result = InstitutionResult()

        # Cache the result
        self._cache.set(cache_key, result)

        logger.info(
            f"InstitutionRecognizer: Best match = {result.university_name} "
            f"(confidence={result.confidence_score:.4f})"
        )
        return result

    def _build_text_corpus(self, raw_text: str, fields: dict[str, Any] | None) -> str:
        """Combine all available text sources into a single normalized corpus."""
        parts = [raw_text]

        if fields:
            # Add institution field if present (highest signal)
            inst_field = fields.get("institution", "")
            if inst_field:
                parts.append(str(inst_field))

            # Check nested schema
            student_info = fields.get("student_info", {})
            if isinstance(student_info, dict):
                for key in ("university", "institution", "college"):
                    val = student_info.get(key, "")
                    if val:
                        parts.append(str(val))

            verification = fields.get("verification_info", {})
            if isinstance(verification, dict):
                for val in verification.values():
                    if val:
                        parts.append(str(val))

        return self._normalize_text(" ".join(parts))

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Lowercase, strip extra whitespace, remove punctuation noise."""
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _score_institution(self, institution: dict[str, Any], corpus: str) -> _MatchScore:
        """Score a single institution against the text corpus."""
        inst_id = institution["id"]
        inst_name = institution["name"]
        aliases = institution.get("aliases", [])
        keywords = institution.get("keywords", [])
        city = institution.get("city", "").lower()
        state = institution.get("state", "").lower()

        score = _MatchScore(institution_id=inst_id, institution_name=inst_name)

        # 1. Full name match
        name_lower = inst_name.lower()
        if name_lower in corpus:
            score.name_score = 1.0
            score.aliases_matched.append(inst_name)
        else:
            # Partial name match (word overlap)
            name_words = set(name_lower.split())
            corpus_words = set(corpus.split())
            overlap = name_words & corpus_words
            # Remove common stop words from the overlap count
            stop_words = {"of", "the", "and", "in", "for", "at", "to", "a", "an", "is"}
            meaningful_overlap = overlap - stop_words
            meaningful_name = name_words - stop_words
            if meaningful_name:
                score.name_score = len(meaningful_overlap) / len(meaningful_name)

        # 2. Alias match
        best_alias_score = 0.0
        for alias in aliases:
            alias_lower = alias.lower()
            if alias_lower in corpus:
                best_alias_score = 1.0
                score.aliases_matched.append(alias)
                break
            else:
                # Partial alias match
                alias_words = set(alias_lower.split()) - {"of", "the", "and"}
                if alias_words:
                    corpus_words_set = set(corpus.split())
                    alias_overlap = alias_words & corpus_words_set
                    partial = len(alias_overlap) / len(alias_words)
                    if partial > best_alias_score:
                        best_alias_score = partial
        score.alias_score = best_alias_score

        # 3. Keyword match
        keyword_hits = 0
        for kw in keywords:
            if kw.lower() in corpus:
                keyword_hits += 1
        score.keyword_score = keyword_hits / max(len(keywords), 1)

        # 4. Context clues (city, state)
        context_hits = 0
        context_total = 0
        if city:
            context_total += 1
            if city in corpus:
                context_hits += 1
        if state:
            context_total += 1
            if state in corpus:
                context_hits += 1
        score.context_score = context_hits / max(context_total, 1)

        return score

    def get_institution_by_id(self, institution_id: str) -> dict[str, Any] | None:
        """Look up an institution by its ID."""
        self._ensure_loaded()
        for inst in self._institutions:
            if inst["id"] == institution_id:
                return inst
        return None

    @property
    def institution_count(self) -> int:
        """Number of institutions in the registry."""
        self._ensure_loaded()
        return len(self._institutions)
