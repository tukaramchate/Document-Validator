from datetime import datetime, timezone
from models import db


class Result(db.Model):
    """Validation result model for AI analysis output."""
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), unique=True, nullable=False, index=True)
    cnn_score = db.Column(db.Float, nullable=True)          # Visual analysis score (0–1)
    ocr_confidence = db.Column(db.Float, nullable=True)     # OCR confidence score (0–1)
    db_match_score = db.Column(db.Float, nullable=True)     # Database match score (0–1)
    final_score = db.Column(db.Float, nullable=False)       # Weighted combined score (0–1)
    verdict = db.Column(db.String(20), nullable=False)      # AUTHENTIC / SUSPICIOUS / FAKE
    extracted_data = db.Column(db.JSON, nullable=True)       # OCR-extracted fields
    field_matches = db.Column(db.JSON, nullable=True)        # Per-field match details
    validated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Serialize result to JSON-safe dict."""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'scores': {
                'cnn_score': self.cnn_score,
                'ocr_confidence': self.ocr_confidence,
                'db_match_score': self.db_match_score,
                'final_score': self.final_score
            },
            'verdict': self.verdict,
            'extracted_data': self.extracted_data,
            'field_matches': self.field_matches,
            'validated_at': self.validated_at.isoformat() if self.validated_at else None
        }

    def __repr__(self):
        return f'<Result doc_id={self.document_id} verdict={self.verdict}>'
