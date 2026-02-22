import logging
from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Register global error handlers for the Flask app."""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'BAD_REQUEST',
                'message': str(error.description) if hasattr(error, 'description') else 'Bad request'
            }
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'UNAUTHORIZED',
                'message': 'Authentication required'
            }
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'FORBIDDEN',
                'message': 'You do not have permission to access this resource'
            }
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Resource not found'
            }
        }), 404

    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'FILE_TOO_LARGE',
                'message': 'File size exceeds the 16MB limit'
            }
        }), 413

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Internal server error: {error}', exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An unexpected error occurred'
            }
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        # Pass through HTTP errors
        if isinstance(error, HTTPException):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'HTTP_ERROR',
                    'message': error.description
                }
            }), error.code

        # Non-HTTP exceptions
        logger.error(f'Unhandled exception: {error}', exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An unexpected error occurred'
            }
        }), 500
