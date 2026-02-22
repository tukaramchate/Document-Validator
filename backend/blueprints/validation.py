import logging
from flask import Blueprint, request
from services.validation_service import validate_document, get_result, get_validation_history, revalidate_document
from middleware.auth_middleware import token_required
from utils.response_utils import success_response, error_response, paginated_response

logger = logging.getLogger(__name__)

validation_bp = Blueprint('validation', __name__)


@validation_bp.route('/validate/<int:doc_id>', methods=['POST'])
@token_required
def validate(current_user, doc_id):
    """Run AI validation pipeline on a document."""
    try:
        result = validate_document(doc_id, current_user.id)
        return success_response(
            data={'result': result},
            message='Validation complete'
        )
    except ValueError as e:
        msg = str(e)
        if msg == 'NOT_FOUND':
            return error_response('Document not found', 'NOT_FOUND', 404)
        if msg == 'FORBIDDEN':
            return error_response('Access denied', 'FORBIDDEN', 403)
        return error_response(msg, 'ERROR', 400)
    except Exception as e:
        logger.error(f'Validation error: {e}', exc_info=True)
        return error_response('Validation failed', 'INTERNAL_ERROR', 500)


@validation_bp.route('/validate/<int:doc_id>', methods=['PUT'])
@token_required
def revalidate(current_user, doc_id):
    """Force re-validation of a previously validated document."""
    try:
        result = revalidate_document(doc_id, current_user.id)
        return success_response(
            data={'result': result},
            message='Re-validation complete'
        )
    except ValueError as e:
        msg = str(e)
        if msg == 'NOT_FOUND':
            return error_response('Document not found', 'NOT_FOUND', 404)
        if msg == 'FORBIDDEN':
            return error_response('Access denied', 'FORBIDDEN', 403)
        return error_response(msg, 'ERROR', 400)
    except Exception as e:
        logger.error(f'Re-validation error: {e}', exc_info=True)
        return error_response('Re-validation failed', 'INTERNAL_ERROR', 500)


@validation_bp.route('/results/<int:doc_id>', methods=['GET'])
@token_required
def results(current_user, doc_id):
    """Get validation results for a specific document."""
    try:
        result = get_result(doc_id, current_user.id)
        return success_response(data={'result': result})
    except ValueError as e:
        msg = str(e)
        if msg == 'NOT_FOUND':
            return error_response('Document not found', 'NOT_FOUND', 404)
        if msg == 'FORBIDDEN':
            return error_response('Access denied', 'FORBIDDEN', 403)
        if msg == 'NOT_VALIDATED':
            return error_response('Document has not been validated yet', 'NOT_VALIDATED', 404)
        return error_response(msg, 'ERROR', 400)


@validation_bp.route('/history', methods=['GET'])
@token_required
def history(current_user):
    """Get paginated validation history for the current user."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = min(per_page, 50)

    try:
        results, total = get_validation_history(current_user.id, page, per_page)
        return paginated_response(results, total, page, per_page, 'results')
    except Exception as e:
        logger.error(f'History error: {e}', exc_info=True)
        return error_response('Failed to retrieve history', 'INTERNAL_ERROR', 500)
