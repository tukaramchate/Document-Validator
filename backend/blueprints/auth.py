import logging
from flask import Blueprint, request
from services.auth_service import register_user, login_user, change_password
from middleware.auth_middleware import token_required
from utils.response_utils import success_response, error_response

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    if not data:
        return error_response('Request body is required', 'BAD_REQUEST', 400)

    try:
        user, token = register_user(
            email=data.get('email'),
            password=data.get('password'),
            name=data.get('name')
        )
        return success_response(
            data={'user': user, 'token': token},
            message='Registration successful',
            status_code=201
        )
    except ValueError as e:
        msg = str(e)
        if msg == 'DUPLICATE_EMAIL':
            return error_response('Email already registered', 'CONFLICT', 409)
        return error_response(msg, 'VALIDATION_ERROR', 400)
    except Exception as e:
        logger.error(f'Registration error: {e}', exc_info=True)
        return error_response('Registration failed', 'INTERNAL_ERROR', 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return token."""
    data = request.get_json()
    if not data:
        return error_response('Request body is required', 'BAD_REQUEST', 400)

    try:
        user, token = login_user(
            email=data.get('email'),
            password=data.get('password')
        )
        return success_response(
            data={'user': user, 'token': token},
            message='Login successful'
        )
    except ValueError as e:
        msg = str(e)
        if msg == 'INVALID_CREDENTIALS':
            return error_response('Invalid email or password', 'AUTH_ERROR', 401)
        return error_response(msg, 'VALIDATION_ERROR', 400)
    except Exception as e:
        logger.error(f'Login error: {e}', exc_info=True)
        return error_response('Login failed', 'INTERNAL_ERROR', 500)


@auth_bp.route('/profile', methods=['GET'])
@token_required
def profile(current_user):
    """Get current user's profile."""
    return success_response(data={'user': current_user.to_dict()})


@auth_bp.route('/password', methods=['PUT'])
@token_required
def update_password(current_user):
    """Change the current user's password."""
    data = request.get_json()
    if not data:
        return error_response('Request body is required', 'BAD_REQUEST', 400)

    try:
        user = change_password(
            user_id=current_user.id,
            old_password=data.get('old_password'),
            new_password=data.get('new_password')
        )
        return success_response(
            data={'user': user},
            message='Password changed successfully'
        )
    except ValueError as e:
        msg = str(e)
        if msg == 'INVALID_CREDENTIALS':
            return error_response('Current password is incorrect', 'AUTH_ERROR', 401)
        return error_response(msg, 'VALIDATION_ERROR', 400)
    except Exception as e:
        logger.error(f'Password change error: {e}', exc_info=True)
        return error_response('Password change failed', 'INTERNAL_ERROR', 500)
