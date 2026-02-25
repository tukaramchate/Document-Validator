import os
import logging
from flask import Blueprint, request, send_file
from app import limiter
from services.validation_service import validate_document, get_result, get_validation_history, revalidate_document
from services.report_service import generate_validation_report
from middleware.auth_middleware import token_required
from utils.response_utils import success_response, error_response, paginated_response

logger = logging.getLogger(__name__)

validation_bp = Blueprint('validation', __name__)


@validation_bp.route('/validate/<int:doc_id>', methods=['POST'])
@token_required
@limiter.limit('10 per minute')
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
        if msg == 'USAGE_LIMIT_REACHED':
            return error_response('Validation limit reached (10 max). Please upgrade to paid.', 'USAGE_LIMIT_REACHED', 403)
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
    except Exception as e:
        logger.error(f'Get result error: {e}', exc_info=True)
        return error_response('Failed to retrieve result', 'INTERNAL_ERROR', 500)


@validation_bp.route('/history', methods=['GET'])
@token_required
def history(current_user):
    """Get paginated validation history for the current user."""
    page = max(1, request.args.get('page', 1, type=int))
    per_page = max(1, min(request.args.get('per_page', 10, type=int), 50))

    # Optional verdict filter: AUTHENTIC, SUSPICIOUS, FAKE
    verdict_filter = request.args.get('verdict', None)
    if verdict_filter:
        verdict_filter = verdict_filter.upper()
        if verdict_filter not in ('AUTHENTIC', 'SUSPICIOUS', 'FAKE'):
            return error_response(
                'Invalid verdict filter. Must be AUTHENTIC, SUSPICIOUS, or FAKE.',
                'VALIDATION_ERROR', 400
            )

    try:
        results, total = get_validation_history(current_user.id, page, per_page, verdict_filter)
        return paginated_response(results, total, page, per_page, 'results')
    except Exception as e:
        logger.error(f'History error: {e}', exc_info=True)
        return error_response('Failed to retrieve history', 'INTERNAL_ERROR', 500)

@validation_bp.route('/results/<int:doc_id>/report', methods=['GET'])
@token_required
def download_report(current_user, doc_id):
    """Download the validation report as a PDF."""
    try:
        from models import db
        from models.document import Document
        document = db.session.get(Document, doc_id)
        if not document:
             return error_response('Document not found', 'NOT_FOUND', 404)
        if document.user_id != current_user.id:
             return error_response('Access denied', 'FORBIDDEN', 403)
        if not document.result:
             return error_response('Document not validated yet', 'NOT_VALIDATED', 400)

        # Generate report to a temporary path
        import tempfile
        temp_dir = tempfile.gettempdir()
        report_path = os.path.join(temp_dir, f"report_{doc_id}.pdf")
        
        generate_validation_report(document, document.result, report_path)

        return send_file(
            report_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Validation_Report_{document.filename}.pdf"
        )
    except Exception as e:
        logger.error(f'Report download error: {e}', exc_info=True)
        return error_response('Failed to generate report', 'INTERNAL_ERROR', 500)
