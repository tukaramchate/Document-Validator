from datetime import datetime, timezone
from models import db

class ValidationJob(db.Model):
    __tablename__ = 'validation_jobs'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='QUEUED')  # QUEUED, PROCESSING, COMPLETED, FAILED
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)

    document = db.relationship(
        'Document',
        backref=db.backref('validation_jobs', cascade='all, delete-orphan', passive_deletes=True),
    )
    user = db.relationship(
        'User',
        backref=db.backref('validation_jobs', cascade='all, delete-orphan', passive_deletes=True),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'user_id': self.user_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'error_message': self.error_message,
        }
