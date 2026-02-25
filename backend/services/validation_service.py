import os
import random
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

def mock_cnn_predict(image_path):
    """[STUB] CNN visual analysis — replace with real model inference once trained."""
    return round(random.uniform(0.6, 0.95), 4)


def extract_data_with_gemini(image_path):
    """Use Gemini AI to extract text data from document images."""
    model = get_genai_model()
    if not model:
        return {
            'fields': {'note': 'Gemini API not configured. Contact admin.'},
            'confidence': 0.0
        }

    try:
        # Load image
        from PIL import Image
        img = Image.open(image_path)

        prompt = """
        Analyze this document image and extract the following fields in JSON format:
        - name
        - id_number
        - institution
        - date
        
        If a field is missing, use null. Return ONLY the JSON object.
        """
        
        response = model.generate_content([prompt, img])
        text = response.text.strip()
        
        # Strip markdown code blocks if present
        if text.startswith('```json'):
            text = text[7:-3].strip()
        elif text.startswith('```'):
            text = text[3:-3].strip()
            
        fields = json.loads(text)
        return {
            'fields': fields,
            'confidence': 0.95 # Gemini doesn't return raw per-field confidence easily
        }
    except Exception as e:
        logger.error(f"Gemini extraction error: {e}", exc_info=True)
        return {'fields': {}, 'confidence': 0.0}


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

    # Step 4 & 5: CNN Prediction (mock for now)
    cnn_score = mock_cnn_predict(image_path)

    # Step 6: OCR Extraction with Gemini
    ocr_result = extract_data_with_gemini(image_path)
    ocr_confidence = ocr_result['confidence']
    extracted_data = ocr_result['fields']

    # Step 7: Database Cross-Verification against Institution Data
    db_result = verify_against_institution_data(extracted_data, user_id)
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
    
    # Increment usage count for free users
    if user.role == 'user':
        user.validation_count += 1
        
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
