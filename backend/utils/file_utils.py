import os
import uuid
import logging
from werkzeug.utils import secure_filename
from flask import current_app

logger = logging.getLogger(__name__)


def allowed_file(filename):
    """Check if file extension is in the allowed set."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def get_file_extension(filename):
    """Extract the file extension from a filename."""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def generate_stored_name(filename):
    """Generate a UUID-based stored name to prevent collisions."""
    ext = get_file_extension(filename)
    return f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex


def get_safe_filename(filename):
    """Return a sanitized version of the filename."""
    return secure_filename(filename)


def get_upload_path(stored_name):
    """Get the full path for an uploaded file."""
    return os.path.join(current_app.config['UPLOAD_FOLDER'], stored_name)


def delete_file(stored_name):
    """Delete a file from the uploads directory."""
    file_path = get_upload_path(stored_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    logger.warning(f'File not found on disk during deletion: {stored_name}')
    return False


def ensure_upload_dir():
    """Create the upload directory if it doesn't exist."""
    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)


# Magic bytes signatures for content-type validation
FILE_SIGNATURES = {
    'pdf': [b'%PDF'],
    'jpg': [b'\xff\xd8'],
    'jpeg': [b'\xff\xd8'],
    'png': [b'\x89PNG\r\n\x1a\n'],
    'webp': [b'RIFF'],
}


def validate_file_content(file_storage, extension):
    """Validate file content matches the declared file extension's signature.
    Returns True if the file content matches the expected format, False otherwise.
    Resets the file stream position after reading.
    """
    max_sig_len = 8
    header = file_storage.read(max_sig_len)
    file_storage.seek(0)  # Reset stream position

    # If we have known signatures for this extension, enforce strict match
    expected_sigs = FILE_SIGNATURES.get(extension)
    if expected_sigs:
        if any(header.startswith(sig) for sig in expected_sigs):
            return True
        # Also log what the header was so we can debug future rejections
        logger.warning(f"File rejected: extension='{extension}' but header doesn't match expected signatures. Header: {header}")
        return False

    # For extensions without known signatures, allow if header matches any allowed format
    for sigs in FILE_SIGNATURES.values():
        if any(header.startswith(sig) for sig in sigs):
            return True

    logger.warning(f"File rejected by magic bytes check. Header: {header}")
    return False
