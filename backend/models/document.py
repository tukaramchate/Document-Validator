from datetime import datetime, timezone
from models import db


class Document(db.Model):
    """Document model for uploaded files."""
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)           # Original name
    stored_name = db.Column(db.String(255), unique=True, nullable=False)  # UUID-based name
    file_type = db.Column(db.String(10), nullable=False)           # pdf, jpg, png
    file_size = db.Column(db.Integer, nullable=False)              # Size in bytes
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    result = db.relationship('Result', backref='document', uselist=False, lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        """Serialize document to JSON-safe dict."""
        return {
            'id': self.id,
            'filename': self.filename,
            'stored_name': self.stored_name,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'user_id': self.user_id,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'has_result': self.result is not None
        }

    def __repr__(self):
        return f'<Document {self.filename}>'
