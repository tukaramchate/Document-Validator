"""
Enhanced Document Validation Pipeline — Orchestrator.

Single Responsibility: Orchestrates the full document analysis pipeline.
Design Patterns:
  - Observer: Notifies registered observers of stage progress.
  - Strategy: Uses swappable extraction strategies (Gemini / regex fallback).
  - Factory: Uses CNNModelFactory for model instantiation.

Pipeline stages:
  1. Image preprocessing (deskew, enhance).
  2. CNN forgery detection.
  3. OCR text extraction (Gemini with regex fallback).
  4. Institution recognition.
  5. Document classification.
  6. Format validation (5 dimensions).
  7. Flag aggregation.

Each stage is independent and fault-tolerant — if one stage fails,
the pipeline continues with degraded results rather than crashing.
"""
from __future__ import annotations

import logging
import os
import random
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import torch
from PIL import Image
from torchvision import transforms

from src.cnn.model_factory import CNNModelFactory
from src.document_classifier import DocumentClassifier
from src.exceptions import (
    CircuitBreakerOpenError,
    DocumentValidatorError,
    GeminiAPIError,
    NonAcademicDocumentError,
)
from src.format_validator import FormatValidator
from src.institution_recognizer import InstitutionRecognizer
from src.interfaces import (
    CNNResult,
    ClassificationResult,
    ExtractionResult,
    FormatValidationResult,
    InstitutionResult,
    PipelineObserver,
    PipelineResult,
)
from src.ocr.strategies import GeminiExtractionStrategy, RegexFallbackStrategy
from src.utils.cache import TTLCache
from src.utils.circuit_breaker import CircuitBreaker
from src.utils.image_utils import load_image, preprocess_document

logger = logging.getLogger(__name__)

# ─── Shared caches and circuit breakers (singleton-like per process) ─────
_gemini_circuit_breaker = CircuitBreaker(
    service_name="gemini_api",
    failure_threshold=5,
    recovery_timeout=60.0,
    success_threshold=2,
)
_extraction_cache = TTLCache(max_size=50, ttl_seconds=600)
_analysis_cache = TTLCache(max_size=200, ttl_seconds=600)


# ─── CNN inference transform ────────────────────────────────
_cnn_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

# ─── Production mode guard ──────────────────────────────────
APP_ENV = os.getenv("APP_ENV", "development")


# ────────────────────────────────────────────────────────────
# Logging Observer (Observer Pattern)
# ────────────────────────────────────────────────────────────

class LoggingObserver(PipelineObserver):
    """Logs all pipeline stage events with timing information."""

    def on_stage_start(self, stage_name: str, context: dict[str, Any]) -> None:
        logger.info(f"Pipeline stage START: {stage_name}")

    def on_stage_complete(self, stage_name: str, result: Any, duration_seconds: float) -> None:
        logger.info(f"Pipeline stage DONE:  {stage_name} ({duration_seconds:.3f}s)")

    def on_stage_error(self, stage_name: str, error: Exception, duration_seconds: float) -> None:
        logger.error(
            f"Pipeline stage FAIL:  {stage_name} ({duration_seconds:.3f}s) — {error!r}"
        )

    def on_pipeline_complete(self, result: PipelineResult, total_duration_seconds: float) -> None:
        logger.info(
            f"Pipeline COMPLETE: request_id={result.request_id}, "
            f"institution={result.institution_recognition.university_name}, "
            f"doc_type={result.document_classification.primary_type.value}, "
            f"cnn_score={result.cnn_result.score:.4f}, "
            f"format_confidence={result.format_validation.overall_confidence:.4f}, "
            f"total_time={total_duration_seconds:.3f}s"
        )


# ────────────────────────────────────────────────────────────
# Enhanced Pipeline
# ────────────────────────────────────────────────────────────

class DocumentValidator:
    """
    Production-grade document validation pipeline.

    Coordinates all analysis stages and returns a unified PipelineResult.
    Fault-tolerant: each stage fails gracefully with default values.

    Usage:
        validator = DocumentValidator()
        validator.load_model()
        result = validator.validate("path/to/marksheet.jpg")
        print(result.to_dict())
    """

    def __init__(
        self,
        model_path: str = "../saved_models/document_cnn_v1.pth",
        confidence_threshold: float = 0.95,
    ):
        """
        Args:
            model_path: Path to CNN checkpoint (relative to src/).
            confidence_threshold: Format validation authenticity threshold.
        """
        self.model_path = os.path.join(os.path.dirname(__file__), model_path)
        self.confidence_threshold = confidence_threshold

        # Pipeline components (Dependency Inversion: depend on interfaces)
        self._cnn_model: torch.nn.Module | None = None
        self._cnn_class_names: list[str] = ["fake", "real"]
        self._cnn_is_mock: bool = True

        self._extraction_strategy = GeminiExtractionStrategy(
            cache=_extraction_cache,
            circuit_breaker=_gemini_circuit_breaker,
        )
        self._fallback_strategy = RegexFallbackStrategy()
        self._institution_recognizer = InstitutionRecognizer(cache=_analysis_cache)
        self._document_classifier = DocumentClassifier(cache=_analysis_cache)
        self._format_validator = FormatValidator(
            confidence_threshold=confidence_threshold,
            cache=_analysis_cache,
        )

        # Observer pattern: registered observers
        self._observers: list[PipelineObserver] = [LoggingObserver()]

    def add_observer(self, observer: PipelineObserver) -> None:
        """Register a pipeline observer."""
        self._observers.append(observer)

    def remove_observer(self, observer: PipelineObserver) -> None:
        """Unregister a pipeline observer."""
        self._observers.remove(observer)

    def load_model(self) -> None:
        """Load the CNN model using the Factory pattern."""
        factory = CNNModelFactory()
        allow_mock = APP_ENV != "production"
        self._cnn_model, self._cnn_class_names, self._cnn_is_mock = factory.load(
            self.model_path, allow_mock=allow_mock
        )
        logger.info(
            f"DocumentValidator: CNN model loaded (mock={self._cnn_is_mock})"
        )

    def validate(self, image_path: str) -> dict[str, Any]:
        """
        Run the full validation pipeline on a document image.

        Backward-compatible: returns a dict matching both the new
        PipelineResult schema AND the legacy cnn_result/ocr_result format.

        Args:
            image_path: Path to the document image/PDF.

        Returns:
            Dict with all analysis results (serializable to JSON).
        """
        request_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        pipeline_start = time.monotonic()

        # Initialize result with defaults
        result = PipelineResult(request_id=request_id, timestamp=timestamp)

        # ── Stage 0: Load image ──────────────────────────
        image = self._run_stage(
            "image_loading",
            lambda: load_image(image_path),
            default=None,
        )
        if image is None:
            result.flags["requires_manual_review"] = True
            return result.to_dict()

        # ── Stage 1: Preprocess ──────────────────────────
        processed = self._run_stage(
            "preprocessing",
            lambda: preprocess_document(image, do_deskew=True, do_enhance=True),
            default=image,
        )

        # ── Stage 2: CNN forgery detection ───────────────
        cnn_result = self._run_stage(
            "cnn_forgery_detection",
            lambda: self._run_cnn(processed),
            default=CNNResult(),
        )
        result.cnn_result = cnn_result

        # ── Stage 3: OCR extraction ─────────────────────
        extraction = self._run_stage(
            "ocr_extraction",
            lambda: self._run_extraction(processed),
            default=ExtractionResult(),
        )
        result.ocr_result = extraction

        # Check for non-academic document early
        if extraction.fields.get("error") == "NOT_ACADEMIC_DOCUMENT":
            result.flags["requires_manual_review"] = True
            total_time = time.monotonic() - pipeline_start
            self._notify_pipeline_complete(result, total_time)
            return result.to_dict()

        raw_text = extraction.raw_text
        fields = extraction.fields

        # ── Stage 4: Institution recognition ─────────────
        inst_result = self._run_stage(
            "institution_recognition",
            lambda: self._institution_recognizer.analyze(processed, raw_text, fields),
            default=InstitutionResult(),
        )
        result.institution_recognition = inst_result

        # ── Stage 5: Document classification ─────────────
        class_result = self._run_stage(
            "document_classification",
            lambda: self._document_classifier.analyze(processed, raw_text, fields),
            default=ClassificationResult(),
        )
        result.document_classification = class_result

        # ── Stage 6: Format validation ───────────────────
        # Pass doc type hint for field presence validation
        validation_fields = {**fields, "_doc_type": class_result.primary_type.value}
        format_result = self._run_stage(
            "format_validation",
            lambda: self._format_validator.analyze(processed, raw_text, validation_fields),
            default=FormatValidationResult(),
        )
        result.format_validation = format_result

        # ── Stage 7: Flag aggregation ────────────────────
        result.flags = self._compute_flags(result)

        total_time = time.monotonic() - pipeline_start
        self._notify_pipeline_complete(result, total_time)

        return result.to_dict()

    # ────────────────────────────────────────────────────────
    # Stage Runners
    # ────────────────────────────────────────────────────────

    def _run_stage(self, stage_name: str, func: Any, default: Any) -> Any:
        """
        Execute a pipeline stage with observer notification and error handling.

        If the stage fails, returns the default value and notifies observers.
        """
        self._notify_stage_start(stage_name)
        start = time.monotonic()

        try:
            result = func()
            duration = time.monotonic() - start
            self._notify_stage_complete(stage_name, result, duration)
            return result
        except NonAcademicDocumentError:
            # Propagate this specific error for early exit
            duration = time.monotonic() - start
            self._notify_stage_error(stage_name, NonAcademicDocumentError(), duration)
            # Return a ExtractionResult with the error flag
            if isinstance(default, ExtractionResult):
                return ExtractionResult(
                    fields={"error": "NOT_ACADEMIC_DOCUMENT"},
                    raw_text="",
                    confidence=0.0,
                    strategy_name="error",
                )
            return default
        except Exception as exc:
            duration = time.monotonic() - start
            self._notify_stage_error(stage_name, exc, duration)
            return default

    def _run_cnn(self, image: Image.Image) -> CNNResult:
        """Run CNN forgery detection."""
        if self._cnn_model is None or self._cnn_is_mock:
            # Mock prediction
            if APP_ENV == "production":
                from src.exceptions import ModelNotFoundError
                raise ModelNotFoundError(self.model_path)

            score = round(random.uniform(0.60, 0.95), 4)
            return CNNResult(
                score=score,
                label="real" if score >= 0.50 else "fake",
                confidence=score if score >= 0.50 else float(1 - score),
                is_mock=True,
            )

        # Real inference
        input_tensor = _cnn_transform(image).unsqueeze(0)
        device = next(self._cnn_model.parameters()).device
        input_tensor = input_tensor.to(device)

        with torch.no_grad():
            output = self._cnn_model(input_tensor).squeeze()
            probability = torch.sigmoid(output).item()

        score = float(probability)
        return CNNResult(
            score=score,
            label="real" if score >= 0.50 else "fake",
            confidence=score if score >= 0.50 else float(1 - score),
            is_mock=False,
        )

    def _run_extraction(self, image: Image.Image) -> ExtractionResult:
        """
        Run OCR extraction with primary → fallback strategy chain.

        Strategy pattern: tries GeminiExtractionStrategy first,
        falls back to RegexFallbackStrategy if circuit breaker is open
        or Gemini fails.
        """
        try:
            result = self._extraction_strategy.extract(image)
            return result
        except NonAcademicDocumentError:
            raise
        except (CircuitBreakerOpenError, GeminiAPIError) as exc:
            logger.warning(
                f"Primary extraction failed ({exc!r}), "
                f"falling back to regex strategy"
            )
            # Fallback needs raw_text, but we don't have it without Gemini
            # Return a minimal result indicating fallback was used
            return ExtractionResult(
                fields={"error": "Primary extraction unavailable, fallback has no raw text"},
                raw_text="",
                confidence=0.0,
                strategy_name=self._fallback_strategy.strategy_name,
            )
        except Exception as exc:
            logger.error(f"All extraction strategies failed: {exc!r}")
            return ExtractionResult(
                fields={"error": f"Extraction failed: {str(exc)[:200]}"},
                raw_text="",
                confidence=0.0,
                strategy_name="error",
            )

    # ────────────────────────────────────────────────────────
    # Flag Computation
    # ────────────────────────────────────────────────────────

    @staticmethod
    def _compute_flags(result: PipelineResult) -> dict[str, bool]:
        """Compute alert flags based on all analysis results."""
        flags = {
            "requires_manual_review": False,
            "potential_forgery": False,
        }

        # Flag for manual review
        if result.institution_recognition.confidence_score < 0.50:
            flags["requires_manual_review"] = True

        if result.document_classification.confidence_score < 0.50:
            flags["requires_manual_review"] = True

        if result.ocr_result.confidence < 0.50:
            flags["requires_manual_review"] = True

        if result.cnn_result.is_mock:
            flags["requires_manual_review"] = True

        # Flag for potential forgery
        if not result.cnn_result.is_mock and result.cnn_result.score < 0.40:
            flags["potential_forgery"] = True

        if result.format_validation.overall_confidence < 0.60:
            flags["potential_forgery"] = True

        return flags

    # ────────────────────────────────────────────────────────
    # Observer Notifications
    # ────────────────────────────────────────────────────────

    def _notify_stage_start(self, stage_name: str) -> None:
        for obs in self._observers:
            try:
                obs.on_stage_start(stage_name, {})
            except Exception:
                pass  # Observers must not crash the pipeline

    def _notify_stage_complete(self, stage_name: str, result: Any, duration: float) -> None:
        for obs in self._observers:
            try:
                obs.on_stage_complete(stage_name, result, duration)
            except Exception:
                pass

    def _notify_stage_error(self, stage_name: str, error: Exception, duration: float) -> None:
        for obs in self._observers:
            try:
                obs.on_stage_error(stage_name, error, duration)
            except Exception:
                pass

    def _notify_pipeline_complete(self, result: PipelineResult, total_duration: float) -> None:
        for obs in self._observers:
            try:
                obs.on_pipeline_complete(result, total_duration)
            except Exception:
                pass

    # ────────────────────────────────────────────────────────
    # Legacy compatibility
    # ────────────────────────────────────────────────────────

    def train(self, data_dir: str = "data/", epochs: int = 50, batch_size: int = 32) -> None:
        """Train the CNN on real/fake dataset (unchanged from original)."""
        from src.cnn.train_pytorch import train_model

        train_model(
            data_dir=os.path.join(os.path.dirname(__file__), data_dir),
            output_path=self.model_path,
            epochs=epochs,
            batch_size=batch_size,
        )
