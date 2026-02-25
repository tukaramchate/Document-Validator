import re
import logging
from datetime import datetime, timedelta, timezone
import jwt
from flask import current_app
from models import db
from models.user import User

logger = logging.getLogger(__name__)


def register_user(email, password, name, role='user'):
    """Register a new user and return user dict + JWT token."""
    # Validate required fields first (prevents TypeError on None)
    if not email or not password or not name:
        raise ValueError('Email, password, and name are required')

    # Validate role
    if role not in ('admin', 'institution', 'user'):
        raise ValueError('Invalid role')

    # Normalize inputs early so all checks use the canonical form
    email = email.strip().lower()
    name = name.strip()

    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError('Invalid email format')

    if len(password) < 6:
        raise ValueError('Password must be at least 6 characters')

    if len(name) < 2:
        raise ValueError('Name must be at least 2 characters')

    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        raise ValueError('DUPLICATE_EMAIL')

    # Create new user
    user = User(
        email=email,
        name=name,
        role=role
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    # Generate token
    token = generate_token(user.id)

    logger.info(f'New user registered: {user.email}')
    return user.to_dict(), token


def login_user(email, password):
    """Authenticate user and return user dict + JWT token."""
    if not email or not password:
        raise ValueError('Email and password are required')

    user = User.query.filter_by(email=email.lower().strip()).first()
    if not user:
        raise ValueError('INVALID_CREDENTIALS')

    if not user.check_password(password):
        raise ValueError('INVALID_CREDENTIALS')

    # Generate token
    token = generate_token(user.id)

    logger.info(f'User logged in: {user.email}')
    return user.to_dict(), token


def generate_token(user_id):
    """Generate a JWT token for the given user ID."""
    now = datetime.now(timezone.utc)
    payload = {
        'user_id': user_id,
        'exp': now + timedelta(hours=24),
        'iat': now
    }
    return jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )


def get_user_by_id(user_id):
    """Retrieve user by ID."""
    return db.session.get(User, user_id)


def change_password(user_id, old_password, new_password):
    """Change user password after verifying the old password."""
    if not old_password or not new_password:
        raise ValueError('Old password and new password are required')

    if len(new_password) < 6:
        raise ValueError('New password must be at least 6 characters')

    user = db.session.get(User, user_id)
    if not user:
        raise ValueError('NOT_FOUND')

    if not user.check_password(old_password):
        raise ValueError('INVALID_CREDENTIALS')

    user.set_password(new_password)
    db.session.commit()

    logger.info(f'Password changed for user: {user.email}')
    return user.to_dict()
