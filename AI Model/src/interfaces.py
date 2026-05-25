"""
Abstract interfaces for the Document Validator AI pipeline.

Design Patterns:
  - Strategy: ExtractionStrategy allows swappable OCR backends (Gemini, regex, etc.)
  - Observer: PipelineObserver enables decoupled logging, metrics, and alerting.
  - Template Method: DocumentAnalyzer defines the analysis contract.

SOLID Principles:
  - Interface Segregation: Small, focused interfaces.
  - Dependency Inversion: Pipeline depends on abstractions, not concretions.
  - Open/Closed: New strategies/observers can be added without modifying pipeline.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from PIL import Image


# ────────────────────────────────────────────────────────────
# Data Transfer Objects
# ────────────────────────────────────────────────────────────

class DocumentType(str, Enum):
    """Enumeration of recognized academic document types."""
    MARKSHEET = "marksheet"
    SEMESTER_RESULT = "semester_result"
    PROVISIONAL_CERTIFICATE = "provisional_certificate"
    DEGREE_CERTIFICATE = "degree_certificate"
    MIGRATION_CERTIFICATE = "migration_certificate"
    ID_CARD = "id_card"
    TRANSCRIPT = "transcript"
    UNKNOWN = "unknown"


class DocumentSubType(str, Enum):
    """Sub-classification for documents."""
    SEMESTER_WISE = "semester_wise"
    YEARLY = "yearly"
    CONSOLIDATED = "consolidated"
    SUPPLEMENTARY = "supplementary"
    ORIGINAL = "original"
    DUPLICATE = "duplicate"
    UNKNOWN = "unknown"


@dataclass
class ExtractionResult:
    """Output of an extraction strategy."""
    fields: dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""
    confidence: float = 0.0
    strategy_name: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ClassificationResult:
    """Output of document classification."""
    primary_type: DocumentType = DocumentType.UNKNOWN
    sub_type: DocumentSubType = DocumentSubType.UNKNOWN
    confidence_score: float = 0.0
    reasoning: str = ""


@dataclass
class InstitutionResult:
    """Output of institution recognition."""
    university_id: str = "UNKNOWN"
    university_name: str = "Unknown Institution"
    confidence_score: float = 0.0
    aliases_matched: list[str] = field(default_factory=list)


@dataclass
class ValidationDimension:
    """A single dimension of format validation."""
    name: str
    score: float
    weight: float
    details: str = ""


@dataclass
class FormatValidationResult:
    """Output of 5-dimensional format validation."""
    is_authentic: bool = False
    overall_confidence: float = 0.0
    dimensions: list[ValidationDimension] = field(default_factory=list)

    @property
    def validation_scores(self) -> dict[str, float]:
        """Return per-dimension scores as a flat dict."""
        return {dim.name: dim.score for dim in self.dimensions}


@dataclass
class CNNResult:
    """Output of CNN forgery detection."""
    score: float = 0.0
    label: str = "unknown"
    confidence: float = 0.0
    is_mock: bool = True


@dataclass
class PipelineResult:
    """Aggregated result from the full pipeline."""
    request_id: str = ""
    timestamp: str = ""
    cnn_result: CNNResult = field(default_factory=CNNResult)
    institution_recognition: InstitutionResult = field(default_factory=InstitutionResult)
    document_classification: ClassificationResult = field(default_factory=ClassificationResult)
    format_validation: FormatValidationResult = field(default_factory=FormatValidationResult)
    ocr_result: ExtractionResult = field(default_factory=ExtractionResult)
    format_prediction: dict = field(default_factory=lambda: {
        "institution": None,
        "confidence": 0.0,
        "scores": {},
        "is_available": False,
    })
    flags: dict[str, bool] = field(default_factory=lambda: {
        "requires_manual_review": False,
        "potential_forgery": False,
        "format_mismatch": False,
    })

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict matching the target API schema."""
        return {
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "cnn_result": {
                "score": self.cnn_result.score,
                "label": self.cnn_result.label,
                "confidence": self.cnn_result.confidence,
                "is_mock": self.cnn_result.is_mock,
            },
            "format_prediction": self.format_prediction,
            "institution_recognition": {
                "university_id": self.institution_recognition.university_id,
                "university_name": self.institution_recognition.university_name,
                "confidence_score": self.institution_recognition.confidence_score,
            },
            "document_classification": {
                "primary_type": self.document_classification.primary_type.value,
                "sub_type": self.document_classification.sub_type.value,
                "confidence_score": self.document_classification.confidence_score,
            },
            "format_validation": {
                "is_authentic": self.format_validation.is_authentic,
                "overall_confidence": self.format_validation.overall_confidence,
                "validation_scores": self.format_validation.validation_scores,
            },
            "ocr_result": {
                "confidence": self.ocr_result.confidence,
                "fields": self.ocr_result.fields,
            },
            "flags": self.flags,
        }


# ────────────────────────────────────────────────────────────
# Strategy Interface — OCR Extraction
# ────────────────────────────────────────────────────────────

class ExtractionStrategy(ABC):
    """
    Strategy interface for document data extraction.

    Implementations:
      - GeminiExtractionStrategy: Uses Google Gemini API.
      - RegexFallbackStrategy: Uses regex patterns on raw text.
    """

    @abstractmethod
    def extract(self, image: Image.Image, context: dict[str, Any] | None = None) -> ExtractionResult:
        """
        Extract structured data from an image.

        Args:
            image: PIL Image to process.
            context: Optional context (e.g., institution hint, document type).

        Returns:
            ExtractionResult with parsed fields.
        """
        ...

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Human-readable name for this strategy."""
        ...


# ────────────────────────────────────────────────────────────
# Analyzer Interface — Institution / Classification / Validation
# ────────────────────────────────────────────────────────────

class DocumentAnalyzer(ABC):
    """
    Template Method interface for document analysis stages.

    Implementations:
      - InstitutionRecognizer
      - DocumentClassifier
      - FormatValidator
    """

    @abstractmethod
    def analyze(self, image: Image.Image, extracted_text: str = "",
                extracted_fields: dict[str, Any] | None = None) -> Any:
        """
        Analyze a document image and return structured results.

        Args:
            image: PIL Image of the document.
            extracted_text: Raw OCR text (if available).
            extracted_fields: Previously extracted fields (if available).

        Returns:
            Analysis-specific result dataclass.
        """
        ...

    @property
    @abstractmethod
    def analyzer_name(self) -> str:
        """Human-readable name for this analyzer."""
        ...


# ────────────────────────────────────────────────────────────
# Observer Interface — Pipeline Events
# ────────────────────────────────────────────────────────────

class PipelineObserver(ABC):
    """
    Observer interface for monitoring pipeline execution.

    Implementations:
      - LoggingObserver: Logs stage durations and results.
      - MetricsObserver: Collects Prometheus-style metrics (future).
    """

    @abstractmethod
    def on_stage_start(self, stage_name: str, context: dict[str, Any]) -> None:
        """Called when a pipeline stage begins."""
        ...

    @abstractmethod
    def on_stage_complete(self, stage_name: str, result: Any, duration_seconds: float) -> None:
        """Called when a pipeline stage completes successfully."""
        ...

    @abstractmethod
    def on_stage_error(self, stage_name: str, error: Exception, duration_seconds: float) -> None:
        """Called when a pipeline stage fails."""
        ...

    @abstractmethod
    def on_pipeline_complete(self, result: PipelineResult, total_duration_seconds: float) -> None:
        """Called when the full pipeline finishes."""
        ...
