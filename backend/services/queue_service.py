import logging
from datetime import datetime, timezone
from models import db
from models.validation_job import ValidationJob

logger = logging.getLogger(__name__)

def enqueue_validation_job(document_id, user_id):
    """Create a validation job for the given document and user."""
    job = ValidationJob(
        document_id=document_id,
        user_id=user_id,
        status='QUEUED'
    )
    db.session.add(job)
    db.session.flush()
    logger.info(f"Validation job {job.id} queued for document {document_id} by user {user_id}")
    return job

def get_next_queued_job():
    """Fetch the next queued validation job (FIFO)."""
    return ValidationJob.query.filter_by(status='QUEUED').order_by(ValidationJob.created_at.asc()).first()


def mark_job_processing(job):
    job.status = 'PROCESSING'
    job.started_at = datetime.now(timezone.utc)
    db.session.commit()


def mark_job_completed(job):
    job.status = 'COMPLETED'
    job.finished_at = datetime.now(timezone.utc)
    db.session.commit()


def mark_job_failed(job, error_message):
    job.status = 'FAILED'
    job.finished_at = datetime.now(timezone.utc)
    job.error_message = error_message
    db.session.commit()
