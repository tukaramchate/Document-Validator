"""
Pydantic v2 response models for the Document Validator API.

All API responses are validated against these schemas before being sent
to clients that request structured output. Provides:
  - Type safety at the API boundary.
  - Auto-generated OpenAPI/Swagger documentation.
  - Serialization with camelCase / snake_case support.
"""
from __future__ import annotations


from typing import Any

from pydantic import BaseModel, Field


# ────────────────────────────────────────────────────────────
# Sub-models
# ────────────────────────────────────────────────────────────

class CNNResultResponse(BaseModel):
    """CNN forgery detection output."""
    score: float = Field(0.0, ge=0.0, le=1.0, description="Authenticity score (0=fake, 1=real)")
    label: str = Field("unknown", description="Classification label: 'real' or 'fake'")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Model confidence")
    is_mock: bool = Field(True, description="Whether this was a mock prediction (no trained model)")


class InstitutionRecognitionResponse(BaseModel):
    """Institution recognition output."""
    university_id: str = Field("UNKNOWN", description="Unique institution identifier")
    university_name: str = Field("Unknown Institution", description="Full institution name")
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="Recognition confidence")


class DocumentClassificationResponse(BaseModel):
    """Document type classification output."""
    primary_type: str = Field("unknown", description="Document type (marksheet, degree_certificate, etc.)")
    sub_type: str = Field("unknown", description="Document sub-type (semester_wise, consolidated, etc.)")
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="Classification confidence")


class ValidationScoresResponse(BaseModel):
    """Per-dimension format validation scores."""
    layout_similarity: float = Field(0.0, ge=0.0, le=1.0)
    field_presence: float = Field(0.0, ge=0.0, le=1.0)
    typography_match: float = Field(0.0, ge=0.0, le=1.0)
    security_features: float = Field(0.0, ge=0.0, le=1.0)
    data_format: float = Field(0.0, ge=0.0, le=1.0)


class FormatValidationResponse(BaseModel):
    """5-dimensional format validation output."""
    is_authentic: bool = Field(False, description="Whether the document passes the confidence threshold")
    overall_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Weighted overall score")
    validation_scores: ValidationScoresResponse = Field(
        default_factory=ValidationScoresResponse,
        description="Per-dimension validation scores",
    )


class StudentInfoResponse(BaseModel):
    """Extracted student information."""
    name: str | None = None
    roll_number: str | None = None
    enrollment_number: str | None = None
    father_name: str | None = None
    mother_name: str | None = None
    date_of_birth: str | None = None
    course: str | None = None
    branch: str | None = None
    semester: str | None = None
    year_of_study: str | None = None
    academic_year: str | None = None


class InstitutionInfoResponse(BaseModel):
    """Extracted institution information."""
    name: str | None = None
    abbreviation: str | None = None
    city: str | None = None
    state: str | None = None


class GradeResponse(BaseModel):
    """A single subject grade entry."""
    subject_code: str | None = None
    subject_name: str | None = None
    credits: float | None = None
    marks_obtained: int | None = None
    max_marks: int | None = None
    grade: str | None = None
    grade_point: float | None = None


class ResultsResponse(BaseModel):
    """Aggregate result information."""
    sgpa: float | None = None
    cgpa: float | None = None
    percentage: float | None = None
    total_marks_obtained: int | None = None
    total_max_marks: int | None = None
    result_status: str | None = None
    division: str | None = None


class VerificationInfoResponse(BaseModel):
    """Verification and certificate metadata."""
    issue_date: str | None = None
    certificate_number: str | None = None
    qr_code_data: str | None = None
    examination_month_year: str | None = None


class ExtractedFieldsResponse(BaseModel):
    """Full extracted data matching the target schema."""
    student_info: StudentInfoResponse = Field(default_factory=StudentInfoResponse)
    institution_info: InstitutionInfoResponse = Field(default_factory=InstitutionInfoResponse)
    grades: list[GradeResponse] = Field(default_factory=list)
    results: ResultsResponse = Field(default_factory=ResultsResponse)
    verification_info: VerificationInfoResponse = Field(default_factory=VerificationInfoResponse)


class OCRResultResponse(BaseModel):
    """OCR extraction output."""
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Extraction confidence")
    fields: ExtractedFieldsResponse | dict[str, Any] = Field(
        default_factory=ExtractedFieldsResponse,
        description="Extracted structured data",
    )


class FlagsResponse(BaseModel):
    """Processing flags and alerts."""
    requires_manual_review: bool = Field(False, description="Flagged for human review")
    potential_forgery: bool = Field(False, description="Forgery indicators detected")


# ────────────────────────────────────────────────────────────
# Top-level API Response
# ────────────────────────────────────────────────────────────

class PipelineFullResponse(BaseModel):
    """
    Complete response from the /api/pipeline/full/ endpoint.

    Matches the target API specification with all analysis results.
    """
    request_id: str = Field(..., description="Unique request identifier (UUID)")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    cnn_result: CNNResultResponse = Field(default_factory=CNNResultResponse)
    institution_recognition: InstitutionRecognitionResponse = Field(
        default_factory=InstitutionRecognitionResponse,
    )
    document_classification: DocumentClassificationResponse = Field(
        default_factory=DocumentClassificationResponse,
    )
    format_validation: FormatValidationResponse = Field(
        default_factory=FormatValidationResponse,
    )
    ocr_result: OCRResultResponse = Field(default_factory=OCRResultResponse)
    flags: FlagsResponse = Field(default_factory=FlagsResponse)

    model_config = {"json_schema_extra": {
        "example": {
            "request_id": "550e8400-e29b-41d4-a716-446655440000",
            "timestamp": "2026-04-06T11:00:00Z",
            "cnn_result": {"score": 0.87, "label": "real", "confidence": 0.87, "is_mock": False},
            "institution_recognition": {
                "university_id": "IIT_BOMBAY",
                "university_name": "Indian Institute of Technology Bombay",
                "confidence_score": 0.96,
            },
            "document_classification": {
                "primary_type": "marksheet",
                "sub_type": "semester_wise",
                "confidence_score": 0.95,
            },
            "format_validation": {
                "is_authentic": True,
                "overall_confidence": 0.96,
                "validation_scores": {
                    "layout_similarity": 0.95,
                    "field_presence": 0.98,
                    "typography_match": 0.90,
                    "security_features": 0.97,
                    "data_format": 0.96,
                },
            },
            "ocr_result": {
                "confidence": 0.95,
                "fields": {
                    "student_info": {"name": "Rahul Sharma", "roll_number": "2019BCS0045"},
                    "grades": [{"subject_code": "CS301", "subject_name": "DSA", "grade": "A+"}],
                    "results": {"sgpa": 8.5, "cgpa": 8.2, "result_status": "Pass"},
                },
            },
            "flags": {"requires_manual_review": False, "potential_forgery": False},
        }
    }}




class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    service: str = "Document Validator API v2.0"
    components: dict[str, str] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Standardized error response."""
    error: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    request_id: str | None = None
