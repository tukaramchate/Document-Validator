"""
Unit tests for the Institution Recognizer module.

Tests:
  - Registry loading.
  - Exact name matching.
  - Alias matching.
  - Keyword matching.
  - Unknown institution handling.
  - Cache behavior.
"""
import pytest
from src.institution_recognizer import InstitutionRecognizer
from src.interfaces import InstitutionResult


class TestInstitutionRecognizer:
    """Tests for InstitutionRecognizer."""

    @pytest.fixture
    def recognizer(self):
        return InstitutionRecognizer()

    def test_loads_registry(self, recognizer):
        """Should load 100+ institutions from the JSON registry."""
        assert recognizer.institution_count >= 100

    def test_recognizes_iit_bombay_by_name(self, recognizer, fake_image_pil):
        """Should recognize IIT Bombay from full name text."""
        result = recognizer.analyze(
            fake_image_pil,
            extracted_text="Indian Institute of Technology Bombay",
        )
        assert isinstance(result, InstitutionResult)
        assert result.university_id == "IIT_BOMBAY"
        assert result.confidence_score >= 0.5

    def test_recognizes_iit_delhi_by_alias(self, recognizer, fake_image_pil):
        """Should recognize IIT Delhi from alias 'IITD'."""
        result = recognizer.analyze(
            fake_image_pil,
            extracted_text="IITD Semester Result for Hauz Khas campus",
        )
        assert result.university_id == "IIT_DELHI"
        assert result.confidence_score > 0

    def test_recognizes_from_extracted_fields(self, recognizer, fake_image_pil):
        """Should use institution field from extracted data."""
        result = recognizer.analyze(
            fake_image_pil,
            extracted_text="",
            extracted_fields={"institution": "Vellore Institute of Technology"},
        )
        assert result.university_id == "VIT"

    def test_returns_unknown_for_garbage_text(self, recognizer, fake_image_pil):
        """Should return UNKNOWN for unrecognizable text."""
        result = recognizer.analyze(
            fake_image_pil,
            extracted_text="lorem ipsum dolor sit amet",
        )
        assert result.university_id == "UNKNOWN"
        assert result.confidence_score == 0.0

    def test_returns_unknown_for_empty_text(self, recognizer, fake_image_pil):
        """Should handle empty input gracefully."""
        result = recognizer.analyze(fake_image_pil, extracted_text="")
        assert result.university_id == "UNKNOWN"

    def test_lookup_by_id(self, recognizer):
        """Should look up institution details by ID."""
        inst = recognizer.get_institution_by_id("BITS_PILANI")
        assert inst is not None
        assert "Birla" in inst["name"]

    def test_lookup_by_id_not_found(self, recognizer):
        """Should return None for nonexistent ID."""
        assert recognizer.get_institution_by_id("FAKE_UNIVERSITY") is None


class TestDocumentClassifier:
    """Tests for DocumentClassifier."""

    @pytest.fixture
    def classifier(self):
        from src.document_classifier import DocumentClassifier
        return DocumentClassifier()

    def test_classifies_marksheet(self, classifier, fake_image_pil, sample_extracted_text):
        """Should classify text with marks/grades as marksheet."""
        result = classifier.analyze(fake_image_pil, extracted_text=sample_extracted_text)
        assert result.primary_type.value == "marksheet"
        assert result.confidence_score >= 0.5

    def test_classifies_semester_subtype(self, classifier, fake_image_pil, sample_extracted_text):
        """Should detect semester sub-type."""
        result = classifier.analyze(fake_image_pil, extracted_text=sample_extracted_text)
        assert result.sub_type.value in ("semester_wise", "unknown")

    def test_returns_unknown_for_empty(self, classifier, fake_image_pil):
        """Should return unknown for empty text."""
        result = classifier.analyze(fake_image_pil, extracted_text="")
        assert result.primary_type.value == "unknown"

    def test_classifies_id_card(self, classifier, fake_image_pil):
        """Should classify ID card from keywords."""
        result = classifier.analyze(
            fake_image_pil,
            extracted_text="Student Identity Card Valid upto 2025 Blood Group: B+ Photo ID",
        )
        assert result.primary_type.value == "id_card"


class TestFormatValidator:
    """Tests for FormatValidator."""

    @pytest.fixture
    def validator(self):
        from src.format_validator import FormatValidator
        return FormatValidator(confidence_threshold=0.95)

    def test_validates_with_all_dimensions(self, validator, fake_image_pil, sample_extracted_text):
        """Should return scores for all 5 dimensions."""
        result = validator.analyze(fake_image_pil, extracted_text=sample_extracted_text)
        scores = result.validation_scores
        assert "layout_similarity" in scores
        assert "field_presence" in scores
        assert "typography_match" in scores
        assert "security_features" in scores
        assert "data_format" in scores
        assert all(0 <= s <= 1 for s in scores.values())

    def test_overall_confidence_in_range(self, validator, fake_image_pil, sample_extracted_text):
        """Overall confidence should be between 0 and 1."""
        result = validator.analyze(fake_image_pil, extracted_text=sample_extracted_text)
        assert 0.0 <= result.overall_confidence <= 1.0

    def test_empty_text_low_confidence(self, validator, fake_image_pil):
        """Empty text should yield low format confidence."""
        result = validator.analyze(fake_image_pil, extracted_text="")
        assert result.overall_confidence < 0.95
        assert result.is_authentic is False


class TestCircuitBreaker:
    """Tests for CircuitBreaker utility."""

    def test_starts_closed(self):
        from src.utils.circuit_breaker import CircuitBreaker, CircuitState
        cb = CircuitBreaker("test", failure_threshold=2, recovery_timeout=0.1)
        assert cb.state == CircuitState.CLOSED

    def test_opens_after_threshold(self):
        from src.utils.circuit_breaker import CircuitBreaker, CircuitState
        from src.exceptions import CircuitBreakerOpenError

        cb = CircuitBreaker("test", failure_threshold=2, recovery_timeout=60)

        for _ in range(2):
            try:
                cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
            except ValueError:
                pass

        assert cb.state == CircuitState.OPEN
        with pytest.raises(CircuitBreakerOpenError):
            cb.call(lambda: "hello")

    def test_successful_calls_reset_count(self):
        from src.utils.circuit_breaker import CircuitBreaker, CircuitState

        cb = CircuitBreaker("test", failure_threshold=3)
        # One failure
        try:
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
        except ValueError:
            pass
        # One success resets
        result = cb.call(lambda: "ok")
        assert result == "ok"
        assert cb.state == CircuitState.CLOSED


class TestTTLCache:
    """Tests for TTLCache utility."""

    def test_set_and_get(self):
        from src.utils.cache import TTLCache
        cache = TTLCache(max_size=10, ttl_seconds=60)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_returns_none_for_missing(self):
        from src.utils.cache import TTLCache
        cache = TTLCache(max_size=10, ttl_seconds=60)
        assert cache.get("nonexistent") is None

    def test_evicts_oldest_when_full(self):
        from src.utils.cache import TTLCache
        cache = TTLCache(max_size=2, ttl_seconds=60)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)  # Should evict "a"
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3

    def test_stats(self):
        from src.utils.cache import TTLCache
        cache = TTLCache(max_size=10, ttl_seconds=60)
        cache.set("x", 1)
        cache.get("x")  # hit
        cache.get("y")  # miss
        stats = cache.stats
        assert stats["hits"] == 1
        assert stats["misses"] == 1


class TestCNNModelFactory:
    """Tests for CNNModelFactory."""

    def test_create_resnet18(self):
        from src.cnn.model_factory import CNNModelFactory, ModelArchitecture
        factory = CNNModelFactory()
        model = factory.create(ModelArchitecture.RESNET18_TRANSFER)
        assert model is not None

    def test_create_custom_cnn(self):
        from src.cnn.model_factory import CNNModelFactory, ModelArchitecture
        factory = CNNModelFactory()
        model = factory.create(ModelArchitecture.CUSTOM_CNN)
        assert model is not None

    def test_load_missing_model_mock_mode(self):
        from src.cnn.model_factory import CNNModelFactory
        factory = CNNModelFactory()
        model, names, is_mock = factory.load("nonexistent.pth", allow_mock=True)
        assert model is None
        assert is_mock is True

    def test_load_missing_model_strict_raises(self):
        from src.cnn.model_factory import CNNModelFactory
        from src.exceptions import ModelNotFoundError
        factory = CNNModelFactory()
        with pytest.raises(ModelNotFoundError):
            factory.load("nonexistent.pth", allow_mock=False)

    def test_available_architectures(self):
        from src.cnn.model_factory import CNNModelFactory
        archs = CNNModelFactory.available_architectures()
        assert "resnet18_transfer" in archs
        assert "custom_cnn" in archs
