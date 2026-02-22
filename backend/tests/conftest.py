import os
import sys
import pytest

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from models import db as _db
from models.user import User


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    return app


@pytest.fixture(scope='function')
def db(app):
    """Create a fresh database for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app, db):
    """Create a test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def auth_headers(client):
    """Register a user and return auth headers with JWT token."""
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'password': 'testpassword123',
        'name': 'Test User'
    })
    data = response.get_json()
    token = data['data']['token']
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


@pytest.fixture(scope='function')
def second_user_headers(client):
    """Register a second user for ownership tests."""
    response = client.post('/api/auth/register', json={
        'email': 'other@example.com',
        'password': 'otherpassword123',
        'name': 'Other User'
    })
    data = response.get_json()
    token = data['data']['token']
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
