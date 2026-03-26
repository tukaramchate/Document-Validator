"""
Integration tests for FastAPI endpoints using TestClient with mocked AI services.
Run with: pytest tests/test_endpoints.py -v
"""
import io
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set env vars before importing app
os.environ.setdefault("GEMINI_API_KEY", "test-key-mock")
os.environ.setdefault("APP_ENV", "development")

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


# ─── Helper: create a minimal fake JPEG bytes ──────────────────────
def _make_fake_image_bytes():
    from PIL import Image
    import io
    img = Image.new("RGB", (100, 100), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ─── Fixtures ──────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def client():
    """Build a TestClient with mocked validator loaded into app.state."""
    mock_validator = MagicMock()
    mock_validator.validate.return_value = {
        "cnn_result": {
            "score": 0.9,
            "label": "real",
            "confidence": 0.9,
            "is_mock": True
        },
        "ocr_result": {
            "fields": {"name": "Test Student", "cgpa": "8.5"},
            "confidence": 0.95
        }
    }

    with patch("src.pipeline.DocumentValidator", return_value=mock_validator), \
         patch("src.ocr.text_extractor.get_genai_model") as mock_genai:

        # Mock Gemini response
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"name": "Test Student", "cgpa": "8.5", "id_number": null, "course": null, "branch": null, "year": null, "sgpa": null, "certificate_id": null, "institution": null, "date": null}'
        mock_model.generate_content.return_value = mock_response
        mock_genai.return_value = mock_model

        from app.main import app
        app.state.validator = mock_validator
        with TestClient(app) as c:
            yield c


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data


class TestOCREndpoint:
    def test_rejects_unsupported_file_type(self, client):
        response = client.post(
            "/api/ocr/extract/",
            files={"file": ("test.txt", b"hello world", "text/plain")}
        )
        assert response.status_code == 400

    def test_accepts_jpeg_image(self, client):
        image_bytes = _make_fake_image_bytes()
        with patch("app.api.endpoints.ocr._extract_sync", return_value={"name": "Test Student"}):
            response = client.post(
                "/api/ocr/extract/",
                files={"file": ("test.jpg", image_bytes, "image/jpeg")}
            )
        assert response.status_code == 200

    def test_accepts_png_image(self, client):
        image_bytes = _make_fake_image_bytes()
        with patch("app.api.endpoints.ocr._extract_sync", return_value={"name": "Test Student"}):
            response = client.post(
                "/api/ocr/extract/",
                files={"file": ("test.png", image_bytes, "image/png")}
            )
        assert response.status_code == 200


class TestForgeEndpoint:
    def test_rejects_unsupported_file_type(self, client):
        response = client.post(
            "/api/forge/detect/",
            files={"file": ("test.txt", b"hello world", "text/plain")}
        )
        assert response.status_code == 400

    def test_accepts_jpeg_and_returns_score(self, client):
        image_bytes = _make_fake_image_bytes()
        with patch("app.api.endpoints.forge._detect_sync", return_value={"score": 0.9, "label": "real", "confidence": 0.9, "is_mock": True}):
            response = client.post(
                "/api/forge/detect/",
                files={"file": ("test.jpg", image_bytes, "image/jpeg")}
            )
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert "label" in data


class TestPipelineEndpoint:
    def test_rejects_unsupported_file_type(self, client):
        response = client.post(
            "/api/pipeline/full/",
            files={"file": ("test.csv", b"a,b,c", "text/csv")}
        )
        assert response.status_code == 400

    def test_accepts_jpeg_and_returns_full_result(self, client):
        image_bytes = _make_fake_image_bytes()
        mock_result = {
            "cnn_result": {"score": 0.9, "label": "real", "confidence": 0.9, "is_mock": True},
            "ocr_result": {"fields": {"name": "Test"}, "confidence": 0.95}
        }
        with patch("app.api.endpoints.pipeline._validate_sync", return_value=mock_result):
            response = client.post(
                "/api/pipeline/full/",
                files={"file": ("test.jpg", image_bytes, "image/jpeg")}
            )
        assert response.status_code == 200
        data = response.json()
        assert "cnn_result" in data
        assert "ocr_result" in data
