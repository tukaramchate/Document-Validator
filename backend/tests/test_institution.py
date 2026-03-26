"""Tests for institution endpoints."""
import io


def create_test_file(filename='test.pdf', content=b'%PDF-1.4 test content'):
    """Helper to create a test file upload."""
    return (io.BytesIO(content), filename)


def register_institution(client, email='inst@example.com', name='Test Institution', approved=True):
    """Register an institution user and return auth headers."""
    response = client.post('/api/auth/register/institution', json={
        'email': email,
        'password': 'password123',
        'name': name
    })
    data = response.get_json()
    token = data['data']['token']

    # If we need the institution approved, approve it directly via the DB
    if approved:
        from models import db
        from models.user import User
        user = User.query.filter_by(email=email).first()
        user.is_approved = True
        db.session.commit()

    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


def register_admin(client, db_session):
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


class TestAddRecord:
    """Tests for POST /api/institution/records"""

    def test_add_record_success(self, client, db):
        """Test adding a record as an approved institution."""
        headers = register_institution(client)
        response = client.post('/api/institution/records', headers=headers, json={
            'name': 'John Doe',
            'id_number': 'STU001',
            'metadata': {'course': 'CS', 'year': '2024'}
        })
        result = response.get_json()

        assert response.status_code == 201
        assert result['success'] is True
        assert result['data']['record']['name'] == 'John Doe'
        assert result['data']['record']['id_number'] == 'STU001'

    def test_add_record_missing_fields(self, client, db):
        """Test adding a record without required fields returns 400."""
        headers = register_institution(client)
        response = client.post('/api/institution/records', headers=headers, json={
            'name': 'John Doe'
        })
        result = response.get_json()

        assert response.status_code == 400
        assert result['success'] is False

    def test_add_record_not_institution(self, client, auth_headers):
        """Test regular user cannot add records."""
        response = client.post('/api/institution/records', headers=auth_headers, json={
            'name': 'John Doe',
            'id_number': 'STU001'
        })
        result = response.get_json()

        assert response.status_code == 403
        assert result['success'] is False

    def test_add_record_unapproved_institution(self, client, db):
        """Test unapproved institution cannot add records."""
        headers = register_institution(client, email='unapproved@inst.com', approved=False)
        response = client.post('/api/institution/records', headers=headers, json={
            'name': 'John Doe',
            'id_number': 'STU001'
        })
        result = response.get_json()

        assert response.status_code == 403
        assert result['success'] is False


class TestBulkAddRecords:
    """Tests for POST /api/institution/records/bulk"""

    def test_bulk_add_success(self, client, db):
        """Test bulk adding records."""
        headers = register_institution(client)
        response = client.post('/api/institution/records/bulk', headers=headers, json={
            'records': [
                {'name': 'Alice', 'id_number': 'STU001'},
                {'name': 'Bob', 'id_number': 'STU002'},
                {'name': 'Charlie', 'id_number': 'STU003'}
            ]
        })
        result = response.get_json()

        assert response.status_code == 201
        assert result['success'] is True

    def test_bulk_add_empty_records(self, client, db):
        """Test bulk add with empty records list returns 400."""
        headers = register_institution(client)
        response = client.post('/api/institution/records/bulk', headers=headers, json={
            'records': []
        })
        result = response.get_json()

        assert response.status_code == 400
        assert result['success'] is False

    def test_bulk_add_invalid_record(self, client, db):
        """Test bulk add with a record missing required fields returns 400."""
        headers = register_institution(client)
        response = client.post('/api/institution/records/bulk', headers=headers, json={
            'records': [
                {'name': 'Alice', 'id_number': 'STU001'},
                {'name': 'Bob'}  # missing id_number
            ]
        })
        result = response.get_json()

        assert response.status_code == 400
        assert result['success'] is False


class TestListRecords:
    """Tests for GET /api/institution/records"""

    def test_list_records(self, client, db):
        """Test listing institution records."""
        headers = register_institution(client)
        # Add a record first
        client.post('/api/institution/records', headers=headers, json={
            'name': 'John Doe',
            'id_number': 'STU001'
        })

        response = client.get('/api/institution/records', headers=headers)
        result = response.get_json()

        assert response.status_code == 200
        assert result['success'] is True
        assert 'records' in result['data']
        assert len(result['data']['records']) >= 1

    def test_list_records_pagination(self, client, db):
        """Test record listing with pagination."""
        headers = register_institution(client)
        response = client.get('/api/institution/records?page=1&per_page=5', headers=headers)
        result = response.get_json()

        assert response.status_code == 200
        assert 'pagination' in result['data']


class TestDeleteRecord:
    """Tests for DELETE /api/institution/records/<id>"""

    def test_delete_own_record(self, client, db):
        """Test deleting own record succeeds."""
        headers = register_institution(client)
        # Add a record
        add_response = client.post('/api/institution/records', headers=headers, json={
            'name': 'Delete Me',
            'id_number': 'DEL001'
        })
        record_id = add_response.get_json()['data']['record']['id']

        # Delete it
        response = client.delete(f'/api/institution/records/{record_id}', headers=headers)
        result = response.get_json()

        assert response.status_code == 200
        assert result['success'] is True

    def test_delete_nonexistent_record(self, client, db):
        """Test deleting non-existent record returns 404."""
        headers = register_institution(client)
        response = client.delete('/api/institution/records/99999', headers=headers)
        result = response.get_json()

        assert response.status_code == 404
        assert result['success'] is False


class TestInstitutionStats:
    """Tests for GET /api/institution/stats"""

    def test_get_stats(self, client, db):
        """Test getting institution stats."""
        headers = register_institution(client, name='My University')
        # Add some records
        client.post('/api/institution/records', headers=headers, json={
            'name': 'Student A',
            'id_number': 'S001'
        })

        response = client.get('/api/institution/stats', headers=headers)
        result = response.get_json()

        assert response.status_code == 200
        assert result['success'] is True
        assert result['data']['total_records'] >= 1
        assert result['data']['institution_name'] == 'My University'
