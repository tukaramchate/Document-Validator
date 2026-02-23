import logging
from flask import Blueprint, request
from services.upload_service import save_document, get_user_documents, get_document, delete_document
from middleware.auth_middleware import token_required
from utils.response_utils import success_response, error_response, paginated_response

logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    """Upload a document file."""
    if 'file' not in request.files:
        return error_response('No file provided', 'BAD_REQUEST', 400)

    file = request.files['file']
    if file.filename == '':
        return error_response('No file selected', 'BAD_REQUEST', 400)

    try:
        document = save_document(file, current_user.id)
        return success_response(
            data={'document': document},
            message='File uploaded successfully',
            status_code=201
        )
    except ValueError as e:
        return error_response(str(e), 'VALIDATION_ERROR', 400)
    except Exception as e:
        logger.error(f'Upload error: {e}', exc_info=True)
        return error_response('Upload failed', 'INTERNAL_ERROR', 500)


@upload_bp.route('/upload/list', methods=['GET'])
@token_required
def list_files(current_user):
    """List current user's uploaded documents with pagination."""
    page = max(1, request.args.get('page', 1, type=int))
    per_page = max(1, min(request.args.get('per_page', 10, type=int), 50))

    try:
        documents, total = get_user_documents(current_user.id, page, per_page)
        return paginated_response(documents, total, page, per_page, 'documents')
    except Exception as e:
        logger.error(f'List documents error: {e}', exc_info=True)
        return error_response('Failed to retrieve documents', 'INTERNAL_ERROR', 500)


@upload_bp.route('/upload/<int:doc_id>', methods=['GET'])
@token_required
def get_file(current_user, doc_id):
    """Get a single document's details."""
    try:
        document = get_document(doc_id, current_user.id)
        return success_response(data={'document': document.to_dict()})
    except ValueError as e:
        msg = str(e)
        if msg == 'NOT_FOUND':
            return error_response('Document not found', 'NOT_FOUND', 404)
        if msg == 'FORBIDDEN':
            return error_response('Access denied', 'FORBIDDEN', 403)
        return error_response(msg, 'ERROR', 400)
    except Exception as e:
        logger.error(f'Get document error: {e}', exc_info=True)
        return error_response('Failed to retrieve document', 'INTERNAL_ERROR', 500)


@upload_bp.route('/upload/<int:doc_id>', methods=['DELETE'])
@token_required
def delete_file(current_user, doc_id):
    """Delete a document and its file."""
    try:
        delete_document(doc_id, current_user.id)
        return success_response(message='Document deleted successfully')
    except ValueError as e:
        msg = str(e)
        if msg == 'NOT_FOUND':
            return error_response('Document not found', 'NOT_FOUND', 404)
        if msg == 'FORBIDDEN':
            return error_response('Access denied', 'FORBIDDEN', 403)
        return error_response(msg, 'ERROR', 400)
    except Exception as e:
        logger.error(f'Delete error: {e}', exc_info=True)
        return error_response('Delete failed', 'INTERNAL_ERROR', 500)
