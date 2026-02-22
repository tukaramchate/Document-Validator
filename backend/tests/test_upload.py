"""Tests for file upload endpoints."""
import io


def create_test_file(filename='test.pdf', content=b'%PDF-1.4 test content'):
    """Helper to create a test file upload."""
    return (io.BytesIO(content), filename)


class TestUpload:
    """Tests for POST /api/upload"""

    def test_upload_pdf_success(self, client, auth_headers):
        """Test successful PDF upload."""
        data = {'file': create_test_file('test.pdf')}
        response = client.post(
            '/api/upload',
            data=data,
            headers={'Authorization': auth_headers['Authorization']},
            content_type='multipart/form-data'
        )
        result = response.get_json()

        assert response.status_code == 201
        assert result['success'] is True
        assert 'document' in result['data']
        assert result['data']['document']['file_type'] == 'pdf'

    def test_upload_jpg_success(self, client, auth_headers):
        """Test successful JPG upload."""
        data = {'file': create_test_file('test.jpg', b'\xff\xd8\xff\xe0 test')}
        response = client.post(
            '/api/upload',
            data=data,
            headers={'Authorization': auth_headers['Authorization']},
            content_type='multipart/form-data'
        )
        result = response.get_json()

        assert response.status_code == 201
        assert result['success'] is True

    def test_upload_invalid_type(self, client, auth_headers):
        """Test upload of disallowed file type returns 400."""
        data = {'file': create_test_file('malicious.exe', b'MZ evil content')}
        response = client.post(
            '/api/upload',
            data=data,
            headers={'Authorization': auth_headers['Authorization']},
            content_type='multipart/form-data'
        )
        result = response.get_json()

        assert response.status_code == 400
        assert result['success'] is False

    def test_upload_no_file(self, client, auth_headers):
        """Test upload without file returns 400."""
        response = client.post(
            '/api/upload',
            data={},
            headers={'Authorization': auth_headers['Authorization']},
            content_type='multipart/form-data'
        )
        result = response.get_json()

        assert response.status_code == 400
        assert result['success'] is False

    def test_upload_without_auth(self, client):
        """Test upload without authentication returns 401."""
        data = {'file': create_test_file('test.pdf')}
        response = client.post(
            '/api/upload',
            data=data,
            content_type='multipart/form-data'
        )
        result = response.get_json()

        assert response.status_code == 401
        assert result['success'] is False


class TestListDocuments:
    """Tests for GET /api/upload/list"""

    def test_list_documents(self, client, auth_headers):
        """Test listing user's documents."""
        # Upload a file first
        client.post(
            '/api/upload',
            data={'file': create_test_file('test.pdf')},
            headers={'Authorization': auth_headers['Authorization']},
            content_type='multipart/form-data'
        )

        response = client.get('/api/upload/list', headers=auth_headers)
        result = response.get_json()

        assert response.status_code == 200
        assert result['success'] is True
        assert 'documents' in result['data']
        assert len(result['data']['documents']) >= 1

    def test_list_documents_pagination(self, client, auth_headers):
        """Test pagination in document listing."""
        response = client.get('/api/upload/list?page=1&per_page=5', headers=auth_headers)
        result = response.get_json()

        assert response.status_code == 200
        assert 'pagination' in result['data']


class TestDeleteDocument:
    """Tests for DELETE /api/upload/<id>"""

    def test_delete_own_document(self, client, auth_headers):
        """Test deleting own document succeeds."""
        # Upload first
        upload_response = client.post(
            '/api/upload',
            data={'file': create_test_file('delete_me.pdf')},
            headers={'Authorization': auth_headers['Authorization']},
            content_type='multipart/form-data'
        )
        doc_id = upload_response.get_json()['data']['document']['id']

        # Delete
        response = client.delete(f'/api/upload/{doc_id}', headers=auth_headers)
        result = response.get_json()

        assert response.status_code == 200
        assert result['success'] is True

    def test_delete_other_users_document(self, client, auth_headers, second_user_headers):
        """Test deleting another user's document returns 403."""
        # Upload as first user
        upload_response = client.post(
            '/api/upload',
            data={'file': create_test_file('owned.pdf')},
            headers={'Authorization': auth_headers['Authorization']},
            content_type='multipart/form-data'
        )
        doc_id = upload_response.get_json()['data']['document']['id']

        # Try to delete as second user
        response = client.delete(f'/api/upload/{doc_id}', headers=second_user_headers)
        result = response.get_json()

        assert response.status_code == 403
        assert result['success'] is False

    def test_delete_nonexistent_document(self, client, auth_headers):
        """Test deleting non-existent document returns 404."""
        response = client.delete('/api/upload/99999', headers=auth_headers)
        result = response.get_json()

        assert response.status_code == 404
        assert result['success'] is False


class TestGetDocument:
    """Tests for GET /api/upload/<id>"""

    def test_get_single_document(self, client, auth_headers):
        """Test getting a single document's details."""
        upload_response = client.post(
            '/api/upload',
            data={'file': create_test_file('detail.pdf')},
            headers={'Authorization': auth_headers['Authorization']},
            content_type='multipart/form-data'
        )
        doc_id = upload_response.get_json()['data']['document']['id']

        response = client.get(f'/api/upload/{doc_id}', headers=auth_headers)
        result = response.get_json()

        assert response.status_code == 200
        assert result['success'] is True
        assert result['data']['document']['id'] == doc_id

    def test_get_other_users_document(self, client, auth_headers, second_user_headers):
        """Test getting another user's document returns 403."""
        upload_response = client.post(
            '/api/upload',
            data={'file': create_test_file('private.pdf')},
            headers={'Authorization': auth_headers['Authorization']},
            content_type='multipart/form-data'
        )
        doc_id = upload_response.get_json()['data']['document']['id']

        response = client.get(f'/api/upload/{doc_id}', headers=second_user_headers)
        result = response.get_json()

        assert response.status_code == 403
        assert result['success'] is False
