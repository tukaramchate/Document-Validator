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
            current_user = db.session.get(User, payload['user_id'])
            if current_user is None:
                return error_response('User not found', 'AUTH_ERROR', 401)
        except jwt.ExpiredSignatureError:
            return error_response('Token has expired', 'AUTH_ERROR', 401)
        except jwt.InvalidTokenError:
            return error_response('Token is invalid', 'AUTH_ERROR', 401)

        return f(current_user, *args, **kwargs)
    return decorated
