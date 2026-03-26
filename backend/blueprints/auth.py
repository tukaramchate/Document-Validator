import logging
from flask import Blueprint, request
from extensions import limiter
from services.auth_service import register_user, login_user, change_password, logout_user
from middleware.auth_middleware import token_required, admin_required
from utils.response_utils import success_response, error_response

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@limiter.limit('10 per minute')
def register():
    """Register a new user (default: user role)."""
    return _handle_registration('user')


@auth_bp.route('/register/institution', methods=['POST'])
@limiter.limit('10 per minute')
def register_institution():
    """Register a new institution."""
    return _handle_registration('institution')


@auth_bp.route('/register/admin', methods=['POST'])
@token_required
@admin_required
@limiter.limit('10 per minute')
def register_admin(current_user):
    """Register a new admin. Only existing admins can create new admins."""
    return _handle_registration('admin')


def _handle_registration(role):
    data = request.get_json()
    if not data:
        return error_response('Request body is required', 'BAD_REQUEST', 400)

    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    try:
        user, token = register_user(email, password, name, role=role)
        return success_response(
            message=f'{role.capitalize()} registered successfully',
            data={'user': user, 'token': token},
            status_code=201
        )
    except ValueError as e:
        msg = str(e)
        if msg == 'DUPLICATE_EMAIL':
            return error_response('Email already exists', 'CONFLICT', 409)
        return error_response(msg, 'VALIDATION_ERROR', 400)
    except Exception as e:
        logger.error(f'Registration error: {e}', exc_info=True)
        return error_response('Failed to register', 'INTERNAL_ERROR', 500)


@auth_bp.route('/login', methods=['POST'])
@limiter.limit('5 per minute')
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
        if msg == 'PENDING_APPROVAL':
            return error_response('Your account is pending admin approval', 'PENDING_APPROVAL', 403)
        return error_response(msg, 'VALIDATION_ERROR', 400)
    except Exception as e:
        logger.error(f'Login error: {e}', exc_info=True)
        return error_response('Login failed', 'INTERNAL_ERROR', 500)


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Logout by revoking the current token."""
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else None
    if token:
        try:
            logout_user(token, current_user.id)
        except Exception as e:
            logger.error(f'Logout error: {e}', exc_info=True)
    return success_response(message='Logged out successfully')


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
