import random
import logging
from models import db
from models.document import Document
from models.result import Result

logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────
# Mock AI Functions (to be replaced with real AI model later)
# ────────────────────────────────────────────────────────────

def mock_cnn_predict(image_path):
    """Simulate CNN visual analysis score."""
    return round(random.uniform(0.6, 0.95), 4)


def mock_ocr_extract(image_path):
    """Simulate OCR text extraction and confidence."""
    return {
        'fields': {
            'name': 'Sample Name',
            'id_number': '12345',
            'institution': 'Sample Institution',
            'date': '2025-01-15'
        },
        'confidence': round(random.uniform(0.7, 0.98), 4)
    }


def mock_db_match(extracted_fields):
    """Simulate database cross-verification."""
    field_matches = {}
    for key in extracted_fields:
        field_matches[key] = random.choice([True, True, False])  # Weighted toward matches

    matched = sum(1 for v in field_matches.values() if v)
    total = len(field_matches)
    score = matched / total if total > 0 else 0.0

    return {
        'score': round(score, 4),
        'matches': field_matches
    }


# ────────────────────────────────────────────────────────────
# Validation Pipeline
# ────────────────────────────────────────────────────────────

def calculate_verdict(final_score):
    """Determine verdict based on final score thresholds."""
    if final_score >= 0.90:
        return 'AUTHENTIC'
    elif final_score >= 0.70:
        return 'SUSPICIOUS'
    else:
        return 'FAKE'


def validate_document(doc_id, user_id):
    """Run the full validation pipeline on a document."""
    # Step 1: Verify document exists and belongs to user
    document = db.session.get(Document, doc_id)
    if not document:
        raise ValueError('NOT_FOUND')
    if document.user_id != user_id:
        raise ValueError('FORBIDDEN')

    # Step 2: Check if already validated
    if document.result:
        logger.info(f'Document {doc_id} already validated, returning existing result')
        return document.result.to_dict()

    # Step 3: Get file path
    from utils.file_utils import get_upload_path
    image_path = get_upload_path(document.stored_name)

    # Step 4 & 5: CNN Prediction (mock for now)
    cnn_score = mock_cnn_predict(image_path)

    # Step 6: OCR Extraction (mock for now)
    ocr_result = mock_ocr_extract(image_path)
    ocr_confidence = ocr_result['confidence']
    extracted_data = ocr_result['fields']

    # Step 7: Database Cross-Verification (mock for now)
    db_result = mock_db_match(extracted_data)
    db_match_score = db_result['score']
    field_matches = db_result['matches']

    # Step 8: Score Combination
    final_score = round(
        (cnn_score * 0.4) + (ocr_confidence * 0.2) + (db_match_score * 0.4),
        4
    )
    verdict = calculate_verdict(final_score)

    # Step 9: Save result
    result = Result(
        document_id=doc_id,
        cnn_score=cnn_score,
        ocr_confidence=ocr_confidence,
        db_match_score=db_match_score,
        final_score=final_score,
        verdict=verdict,
        extracted_data=extracted_data,
        field_matches=field_matches
    )
    db.session.add(result)
    db.session.commit()

    logger.info(f'Document {doc_id} validated: {verdict} (score: {final_score})')
    return result.to_dict()


def revalidate_document(doc_id, user_id):
    """Force re-validation by deleting existing result and re-running the pipeline."""
    document = db.session.get(Document, doc_id)
    if not document:
        raise ValueError('NOT_FOUND')
    if document.user_id != user_id:
        raise ValueError('FORBIDDEN')

    # Delete existing result if present
    if document.result:
        db.session.delete(document.result)
        db.session.flush()
        logger.info(f'Deleted existing result for document {doc_id} for re-validation')

    # Expire ALL objects in session to ensure no stale relationships
    db.session.expire_all()
    db.session.commit()

    # Re-run the pipeline (document.result is now None, so validate_document won't short-circuit)
    return validate_document(doc_id, user_id)


def get_result(doc_id, user_id):
    """Get validation result for a document."""
    document = db.session.get(Document, doc_id)
    if not document:
        raise ValueError('NOT_FOUND')
    if document.user_id != user_id:
        raise ValueError('FORBIDDEN')
    if not document.result:
        raise ValueError('NOT_VALIDATED')
    return document.result.to_dict()


def get_validation_history(user_id, page=1, per_page=10):
    """Get paginated validation history for a user."""
    pagination = Result.query \
        .join(Document) \
        .filter(Document.user_id == user_id) \
        .order_by(Result.validated_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    results = []
    for result in pagination.items:
        result_dict = result.to_dict()
        result_dict['document'] = result.document.to_dict()
        results.append(result_dict)

    return results, pagination.total
