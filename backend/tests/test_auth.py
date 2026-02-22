"""Tests for authentication endpoints."""


class TestRegister:
    """Tests for POST /api/auth/register"""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@example.com',
            'password': 'password123',
            'name': 'New User'
        })
        data = response.get_json()

        assert response.status_code == 201
        assert data['success'] is True
        assert 'token' in data['data']
        assert data['data']['user']['email'] == 'newuser@example.com'
        assert data['data']['user']['name'] == 'New User'

    def test_register_duplicate_email(self, client):
        """Test registration with existing email returns 409."""
        # Register first user
        client.post('/api/auth/register', json={
            'email': 'duplicate@example.com',
            'password': 'password123',
            'name': 'First User'
        })
        # Try to register again with same email
        response = client.post('/api/auth/register', json={
            'email': 'duplicate@example.com',
            'password': 'password456',
            'name': 'Second User'
        })
        data = response.get_json()

        assert response.status_code == 409
        assert data['success'] is False

    def test_register_missing_fields(self, client):
        """Test registration with missing fields returns 400."""
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com'
        })
        data = response.get_json()

        assert response.status_code == 400
        assert data['success'] is False

    def test_register_short_password(self, client):
        """Test registration with too short password returns 400."""
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': '123',
            'name': 'Test User'
        })
        data = response.get_json()

        assert response.status_code == 400
        assert data['success'] is False

    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        response = client.post('/api/auth/register', json={
            'email': 'not-an-email',
            'password': 'password123',
            'name': 'Test User'
        })
        data = response.get_json()

        assert response.status_code == 400
        assert data['success'] is False


class TestLogin:
    """Tests for POST /api/auth/login"""

    def test_login_success(self, client):
        """Test successful login."""
        # Register first
        client.post('/api/auth/register', json={
            'email': 'logintest@example.com',
            'password': 'password123',
            'name': 'Login User'
        })
        # Login
        response = client.post('/api/auth/login', json={
            'email': 'logintest@example.com',
            'password': 'password123'
        })
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True
        assert 'token' in data['data']

    def test_login_wrong_password(self, client):
        """Test login with wrong password returns 401."""
        # Register first
        client.post('/api/auth/register', json={
            'email': 'wrongpw@example.com',
            'password': 'correctpassword',
            'name': 'Test User'
        })
        # Login with wrong password
        response = client.post('/api/auth/login', json={
            'email': 'wrongpw@example.com',
            'password': 'wrongpassword'
        })
        data = response.get_json()

        assert response.status_code == 401
        assert data['success'] is False

    def test_login_nonexistent_email(self, client):
        """Test login with non-existent email returns 401."""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        })
        data = response.get_json()

        assert response.status_code == 401
        assert data['success'] is False

    def test_login_missing_fields(self, client):
        """Test login with missing fields returns 400."""
        response = client.post('/api/auth/login', json={})
        data = response.get_json()

        assert response.status_code == 400
        assert data['success'] is False


class TestProfile:
    """Tests for GET /api/auth/profile"""

    def test_profile_success(self, client, auth_headers):
        """Test getting profile with valid token."""
        response = client.get('/api/auth/profile', headers=auth_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['user']['email'] == 'test@example.com'

    def test_profile_no_token(self, client):
        """Test profile access without token returns 401."""
        response = client.get('/api/auth/profile')
        data = response.get_json()

        assert response.status_code == 401
        assert data['success'] is False

    def test_profile_invalid_token(self, client):
        """Test profile access with invalid token returns 401."""
        response = client.get('/api/auth/profile', headers={
            'Authorization': 'Bearer invalidtoken123'
        })
        data = response.get_json()

        assert response.status_code == 401
        assert data['success'] is False


class TestChangePassword:
    """Tests for PUT /api/auth/password"""

    def test_change_password_success(self, client, auth_headers):
        """Test successful password change."""
        response = client.put('/api/auth/password', headers=auth_headers, json={
            'old_password': 'testpassword123',
            'new_password': 'newpassword456'
        })
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True

        # Verify can login with new password
        login_response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'newpassword456'
        })
        assert login_response.status_code == 200

    def test_change_password_wrong_old(self, client, auth_headers):
        """Test password change with wrong old password returns 401."""
        response = client.put('/api/auth/password', headers=auth_headers, json={
            'old_password': 'wrongoldpassword',
            'new_password': 'newpassword456'
        })
        data = response.get_json()

        assert response.status_code == 401
        assert data['success'] is False

    def test_change_password_short_new(self, client, auth_headers):
        """Test password change with too short new password returns 400."""
        response = client.put('/api/auth/password', headers=auth_headers, json={
            'old_password': 'testpassword123',
            'new_password': '123'
        })
        data = response.get_json()

        assert response.status_code == 400
        assert data['success'] is False

    def test_change_password_no_auth(self, client):
        """Test password change without auth returns 401."""
        response = client.put('/api/auth/password', json={
            'old_password': 'testpassword123',
            'new_password': 'newpassword456'
        })
        assert response.status_code == 401
