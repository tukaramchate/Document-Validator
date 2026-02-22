import os
import logging
from models import db
from models.document import Document
from utils.file_utils import (
    allowed_file, generate_stored_name, get_safe_filename,
    get_upload_path, delete_file, ensure_upload_dir, validate_file_content
)

logger = logging.getLogger(__name__)


def save_document(file, user_id):
    """Save an uploaded file and create a document record."""
    if not file or file.filename == '':
        raise ValueError('No file provided')

    if not allowed_file(file.filename):
        raise ValueError('File type not allowed. Allowed types: pdf, jpg, jpeg, png')

    # Ensure upload directory exists
    ensure_upload_dir()

    # Validate file content matches extension (magic bytes check)
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if file_ext and not validate_file_content(file, file_ext):
        raise ValueError('File content does not match its extension')

    # Generate safe names
    original_name = get_safe_filename(file.filename)
    stored_name = generate_stored_name(file.filename)

    # Save file to disk
    file_path = get_upload_path(stored_name)
    file.save(file_path)

    # Get file size
    file_size = os.path.getsize(file_path)

    # Get file extension
    file_type = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'unknown'

    # Create database record
    document = Document(
        filename=original_name,
        stored_name=stored_name,
        file_type=file_type,
        file_size=file_size,
        user_id=user_id
    )
    db.session.add(document)
    db.session.commit()

    logger.info(f'Document uploaded: {original_name} by user {user_id}')
    return document.to_dict()


def get_user_documents(user_id, page=1, per_page=10):
    """Get paginated list of documents for a user."""
    pagination = Document.query.filter_by(user_id=user_id) \
        .order_by(Document.uploaded_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    documents = [doc.to_dict() for doc in pagination.items]
    return documents, pagination.total


def get_document(doc_id, user_id):
    """Get a single document, verifying ownership."""
    document = db.session.get(Document, doc_id)
    if not document:
        raise ValueError('NOT_FOUND')
    if document.user_id != user_id:
        raise ValueError('FORBIDDEN')
    return document


def delete_document(doc_id, user_id):
    """Delete a document and its file, verifying ownership."""
    document = get_document(doc_id, user_id)

    # Delete the file from disk
    if not delete_file(document.stored_name):
        logger.warning(f'Physical file not found for document {doc_id}: {document.stored_name}')

    # Delete the database record (cascades to Result)
    db.session.delete(document)
    db.session.commit()

    logger.info(f'Document deleted: {document.filename} by user {user_id}')
    return True
