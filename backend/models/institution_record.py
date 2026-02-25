from datetime import datetime, timezone
from models import db


class InstitutionRecord(db.Model):
    """Model for ground-truth data (e.g. students, employees) against which documents are verified."""
    __tablename__ = 'institution_records'

    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False, index=True)
    id_number = db.Column(db.String(50), nullable=False, index=True)
    metadata_fields = db.Column(db.JSON, nullable=True) # JSON store for extra fields like DOB, expiry, etc.
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship back to the institution (User)
    institution = db.relationship('User', backref=db.backref('records', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'institution_id': self.institution_id,
            'name': self.name,
            'id_number': self.id_number,
            'metadata_fields': self.metadata_fields,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<InstitutionRecord {self.id_number} for {self.institution_id}>'
