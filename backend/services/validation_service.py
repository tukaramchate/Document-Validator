import os
import logging
import json
import google.generativeai as genai
from models import db
from models.document import Document
from models.result import Result
from models.institution_record import InstitutionRecord

logger = logging.getLogger(__name__)


def get_genai_model():
    """Initialize and return the Gemini model."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your_gemini_api_key_here':
        logger.warning("Gemini API key not configured. Falling back to mock data.")
        return None
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')




# ────────────────────────────────────────────────────────────
# AI Pipeline Implementation
# ────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────
# Integration Helper
# ────────────────────────────────────────────────────────────


def verify_against_institution_data(extracted_fields, user_id=None):
    """
    Verify extracted fields against ground-truth data in InstitutionRecord.
    If multiple institutions exist, it tries to match against the one mentioned in the doc.
    """
    id_number = extracted_fields.get('id_number')
    if not id_number:
        return {'score': 0.0, 'matches': {}}

    # Try to find a record matching this ID number
    record = InstitutionRecord.query.filter_by(id_number=str(id_number)).first()
    
    if not record:
        return {'score': 0.0, 'matches': {'id_number': False}}

    matches = {}
    score_components = []
    
    # Check ID match (already found if we are here, but let's be explicit)
    matches['id_number'] = True
    score_components.append(1.0)

    # Check Name match (case-insensitive fuzzy)
    if 'name' in extracted_fields and extracted_fields['name']:
        name_match = extracted_fields['name'].strip().lower() == record.name.strip().lower()
        matches['name'] = name_match
        score_components.append(1.0 if name_match else 0.0)

    # Check Institution match
    if 'institution' in extracted_fields and extracted_fields['institution']:
        # Fetch the institution name from the record owner
        inst_user = record.institution
        inst_match = extracted_fields['institution'].strip().lower() in inst_user.name.lower()
        matches['institution'] = inst_match
        score_components.append(1.0 if inst_match else 0.0)

    score = sum(score_components) / len(score_components) if score_components else 0.0

    return {
        'score': round(score, 4),
        'matches': matches
    }


# ────────────────────────────────────────────────────────────
# Validation Pipeline
# ────────────────────────────────────────────────────────────

def validate_document(doc_id, user_id):
    """Run the full validation pipeline on a document."""
    # Step 1: Verify user and check usage limits
    from models.user import User
    user = db.session.get(User, user_id)
    if not user:
        raise ValueError('USER_NOT_FOUND')
    
    # Enforce 10-doc limit for free 'user' role
    if user.role == 'user' and not user.is_paid:
        if user.validation_count >= 10:
            raise ValueError('USAGE_LIMIT_REACHED')

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

    # Step 4: Run Real Validation Pipeline
    import sys
    import pathlib
    # Add AI Model dir to path
    _AI_DIR = pathlib.Path(__file__).parent.parent.parent / "AI Model"
    if str(_AI_DIR) not in sys.path:
        sys.path.append(str(_AI_DIR))
        
    from model import DocumentValidator
    
    # We construct the DB record fields expected by the ai matcher if we have ground truth
    # If the user is an institution, we don't know who the document belongs to yet (they upload many)
    # If the user is a normal user, we could potentially look up their institution records but the
    # AI matcher handles the DB matching logic internally.
    
    # For now, we will extract text, and then use the previous verify_against_institution_data logic
    # because the DB schema is tied to SQLAlchemy here in the backend. 
    # Long term, the AI Model's db_matcher can hit an API endpoint or we pass the dict.
    # Let's use the DocumentValidator for CNN taking the image, and OCR taking the image.
    
    validator = DocumentValidator()
    validator.load_model()
    
    # We call validate without db_record_fields to just get CNN + OCR
    ai_result = validator.validate(image_path)
    
    cnn_score = ai_result["cnn_result"].get("score", 0.0)
    ocr_confidence = ai_result["ocr_result"].get("confidence", 0.0)
    extracted_data = ai_result["ocr_result"]["fields"]

    # Step 7: Database Cross-Verification against Institution Data
    # we reuse the backend's specific DB lookup logic for now since it has access to the db models
    db_result = verify_against_institution_data(extracted_data, user_id)
    db_match_score = db_result['score']
    field_matches = db_result['matches']

    # Step 8: Score Combination (Reusing AI Model's calculator)
    from verification.score_calculator import calculate_final_score
    final_calc = calculate_final_score(cnn_score, ocr_confidence, db_match_score)
    
    final_score = final_calc["final_score"]
    verdict = final_calc["verdict"]

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
    
    # Increment usage count for free users — atomic SQL to prevent race conditions (H1 fix)
    if user.role == 'user':
        from models.user import User as UserModel
        db.session.query(UserModel).filter_by(id=user_id).update(
            {UserModel.validation_count: UserModel.validation_count + 1}
        )
        
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
        # Decrement validation_count so re-running validate_document doesn't double-count
        from models.user import User
        user = db.session.get(User, user_id)
        if user and user.role == 'user' and user.validation_count > 0:
            user.validation_count -= 1

        db.session.delete(document.result)
        db.session.flush()  # Flush deletion before expiring
        logger.info(f'Deleted existing result for document {doc_id} for re-validation')

    # Commit. Then expire only the specific document object to clear stale
    # relationship cache so document.result is correctly read as None.
    db.session.commit()
    db.session.expire(document)

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


def get_validation_history(user_id, page=1, per_page=10, verdict_filter=None):
    """Get paginated validation history for a user, with optional verdict filter."""
    query = Result.query \
        .join(Document) \
        .filter(Document.user_id == user_id)

    if verdict_filter:
        query = query.filter(Result.verdict == verdict_filter)

    pagination = query \
        .order_by(Result.validated_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    results = []
    for result in pagination.items:
        result_dict = result.to_dict()
        result_dict['document'] = result.document.to_dict()
        results.append(result_dict)

    return results, pagination.total
