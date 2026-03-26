"""Tests for admin stats endpoints."""
import io


def create_admin_and_get_headers(client, db_session):
    """Create an admin user directly in the DB and return auth headers."""
    from models.user import User
    admin = User(
        email='admin@example.com',
        name='Admin User',
        role='admin',
        is_approved=True
    )
    admin.set_password('adminpassword123')
    db_session.session.add(admin)
    db_session.session.commit()

    response = client.post('/api/auth/login', json={
        'email': 'admin@example.com',
        'password': 'adminpassword123'
    })
    data = response.get_json()
    token = data['data']['token']
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


def upload_and_validate(client, headers):
    """Upload a test PDF and validate it, returning the doc_id."""
    upload_resp = client.post(
        '/api/upload',
        data={'file': (io.BytesIO(b'%PDF-1.4 test content'), 'test.pdf')},
        headers={'Authorization': headers['Authorization']},
        content_type='multipart/form-data'
    )
    doc_id = upload_resp.get_json()['data']['document']['id']
    client.post(f'/api/validate/{doc_id}', headers=headers)
    return doc_id


class TestSystemStats:
    """Tests for GET /api/admin/stats"""

    def test_admin_can_get_stats(self, client, db):
        """Test admin can retrieve system-wide stats."""
        admin_headers = create_admin_and_get_headers(client, db)
        response = client.get('/api/admin/stats', headers=admin_headers)
        result = response.get_json()

        assert response.status_code == 200
        assert result['success'] is True
        assert 'users' in result['data']
        assert 'institutions' in result['data']
        assert 'documents' in result['data']
        assert 'validations' in result['data']
        assert 'distribution' in result['data']

    def test_non_admin_cannot_get_stats(self, client, auth_headers):
        """Test regular user cannot access admin stats."""
        response = client.get('/api/admin/stats', headers=auth_headers)
        result = response.get_json()

        assert response.status_code == 403
        assert result['success'] is False

    def test_unauthenticated_cannot_get_stats(self, client, db):
        """Test unauthenticated request returns 401."""
        response = client.get('/api/admin/stats')
        result = response.get_json()

        assert response.status_code == 401
        assert result['success'] is False


class TestRecentActivity:
    """Tests for GET /api/admin/activity"""

    def test_admin_can_get_activity(self, client, db):
        """Test admin can retrieve recent activity."""
        admin_headers = create_admin_and_get_headers(client, db)
        response = client.get('/api/admin/activity', headers=admin_headers)
        result = response.get_json()

        assert response.status_code == 200
        assert result['success'] is True
        assert 'activity' in result['data']

    def test_non_admin_cannot_get_activity(self, client, auth_headers):
        """Test regular user cannot access activity."""
        response = client.get('/api/admin/activity', headers=auth_headers)
        result = response.get_json()

        assert response.status_code == 403
        assert result['success'] is False


class TestPendingInstitutions:
    """Tests for GET /api/admin/institutions/pending"""

    def test_list_pending_institutions(self, client, db):
        """Test listing pending institutions."""
        admin_headers = create_admin_and_get_headers(client, db)

        # Register an institution (default: is_approved=False for institutions)
        client.post('/api/auth/register/institution', json={
            'email': 'pending@inst.com',
            'password': 'password123',
            'name': 'Pending University'
        })

        response = client.get('/api/admin/institutions/pending', headers=admin_headers)
        result = response.get_json()

        assert response.status_code == 200
        assert result['success'] is True
        assert 'institutions' in result['data']
        assert len(result['data']['institutions']) >= 1

    def test_non_admin_cannot_list_pending(self, client, auth_headers):
        """Test regular user cannot list pending institutions."""
        response = client.get('/api/admin/institutions/pending', headers=auth_headers)
        assert response.status_code == 403


class TestApproveInstitution:
    """Tests for PUT /api/admin/institutions/<id>/approve"""

    def test_approve_institution(self, client, db):
        """Test approving an institution."""
        admin_headers = create_admin_and_get_headers(client, db)

        # Register an institution
        reg_resp = client.post('/api/auth/register/institution', json={
            'email': 'approve_me@inst.com',
            'password': 'password123',
            'name': 'Approve Me University'
        })
        user_id = reg_resp.get_json()['data']['user']['id']

        # Approve it
        response = client.put(
            f'/api/admin/institutions/{user_id}/approve',
            headers=admin_headers,
            json={'approved': True}
        )
        result = response.get_json()

        assert response.status_code == 200
        assert result['success'] is True
        assert result['data']['user']['is_approved'] is True

    def test_reject_institution(self, client, db):
        """Test rejecting an institution."""
        admin_headers = create_admin_and_get_headers(client, db)

        reg_resp = client.post('/api/auth/register/institution', json={
            'email': 'reject_me@inst.com',
            'password': 'password123',
            'name': 'Reject Me University'
        })
        user_id = reg_resp.get_json()['data']['user']['id']

        response = client.put(
            f'/api/admin/institutions/{user_id}/approve',
            headers=admin_headers,
            json={'approved': False}
        )
        result = response.get_json()

        assert response.status_code == 200
        assert result['data']['user']['is_approved'] is False

    def test_approve_nonexistent_user(self, client, db):
        """Test approving non-existent institution returns 404."""
        admin_headers = create_admin_and_get_headers(client, db)
        response = client.put(
            '/api/admin/institutions/99999/approve',
            headers=admin_headers,
            json={'approved': True}
        )
        assert response.status_code == 404

    def test_approve_non_institution_user(self, client, db):
        """Test approving a regular user returns 404."""
        admin_headers = create_admin_and_get_headers(client, db)

        # Register a regular user
        reg_resp = client.post('/api/auth/register', json={
            'email': 'regular@example.com',
            'password': 'password123',
            'name': 'Regular User'
        })
        user_id = reg_resp.get_json()['data']['user']['id']

        response = client.put(
            f'/api/admin/institutions/{user_id}/approve',
            headers=admin_headers,
            json={'approved': True}
        )
        assert response.status_code == 404

    def test_non_admin_cannot_approve(self, client, auth_headers, db):
        """Test regular user cannot approve institutions."""
        response = client.put(
            '/api/admin/institutions/1/approve',
            headers=auth_headers,
            json={'approved': True}
        )
        assert response.status_code == 403
