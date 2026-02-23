from functools import wraps
from flask import request, current_app
import jwt
from models import db
from models.user import User
from utils.response_utils import error_response


def token_required(f):
    """Decorator to require a valid JWT token for access."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')

        if not token:
            return error_response('Authentication token is missing', 'AUTH_ERROR', 401)

        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            user_id = payload.get('user_id')
            if not user_id:
                return error_response('Token payload is invalid', 'AUTH_ERROR', 401)
            current_user = db.session.get(User, user_id)
            if current_user is None:
                return error_response('User not found', 'AUTH_ERROR', 401)
        except jwt.ExpiredSignatureError:
            return error_response('Token has expired', 'AUTH_ERROR', 401)
        except jwt.InvalidTokenError:
            return error_response('Token is invalid', 'AUTH_ERROR', 401)

        return f(current_user, *args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator to require admin role. Must be used with @token_required applied first."""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user or current_user.role != 'admin':
            return error_response('Admin access required', 'FORBIDDEN', 403)
        return f(current_user, *args, **kwargs)
    return decorated
