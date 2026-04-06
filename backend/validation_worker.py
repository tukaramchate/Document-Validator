import logging
import time
from services.queue_service import get_next_queued_job, mark_job_processing, mark_job_completed, mark_job_failed
from services.validation_service import validate_document
from models import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("validation_worker")

POLL_INTERVAL = 5  # seconds


def run_worker():
    logger.info("Validation worker started. Polling for jobs...")
    while True:
        job = get_next_queued_job()
        if not job:
            time.sleep(POLL_INTERVAL)
            continue
        try:
            logger.info(f"Processing validation job {job.id} (doc {job.document_id}, user {job.user_id})")
            mark_job_processing(job)
            # Run validation pipeline
            validate_document(job.document_id, job.user_id)
            mark_job_completed(job)
            logger.info(f"Validation job {job.id} completed.")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Validation job {job.id} failed: {e}", exc_info=True)
            mark_job_failed(job, str(e))
        time.sleep(1)  # avoid hammering DB

if __name__ == "__main__":
    run_worker()
