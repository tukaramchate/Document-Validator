"""Tests for validation endpoints."""
import io


def upload_test_file(client, auth_headers, filename='test.pdf'):
    """Helper to upload a test file and return document ID."""
    response = client.post(
        '/api/upload',
        data={'file': (io.BytesIO(b'%PDF-1.4 test content'), filename)},
        headers={'Authorization': auth_headers['Authorization']},
        content_type='multipart/form-data'
    )
    return response.get_json()['data']['document']['id']


class TestValidation:
    """Tests for POST /api/validate/<doc_id>"""

    def test_validate_document(self, client, auth_headers):
        """Test successful document validation."""
        doc_id = upload_test_file(client, auth_headers)

        response = client.post(f'/api/validate/{doc_id}', headers=auth_headers)
        result = response.get_json()

        assert response.status_code == 200
        assert result['success'] is True
        assert 'result' in result['data']
        assert 'scores' in result['data']['result']
        assert result['data']['result']['verdict'] in ['AUTHENTIC', 'SUSPICIOUS', 'FAKE']

    def test_validate_nonexistent_document(self, client, auth_headers):
        """Test validating non-existent document returns 404."""
        response = client.post('/api/validate/99999', headers=auth_headers)
        result = response.get_json()

        assert response.status_code == 404
        assert result['success'] is False

    def test_validate_already_validated(self, client, auth_headers):
        """Test re-validating returns existing result."""
        doc_id = upload_test_file(client, auth_headers, 'revalidate.pdf')

        # Validate once
        first_response = client.post(f'/api/validate/{doc_id}', headers=auth_headers)
        first_result = first_response.get_json()['data']['result']

        # Validate again — should return same result
        second_response = client.post(f'/api/validate/{doc_id}', headers=auth_headers)
        second_result = second_response.get_json()['data']['result']

        assert first_result['id'] == second_result['id']

    def test_validate_other_users_document(self, client, auth_headers, second_user_headers):
        """Test validating another user's document returns 403."""
        doc_id = upload_test_file(client, auth_headers)

        response = client.post(f'/api/validate/{doc_id}', headers=second_user_headers)
        result = response.get_json()

        assert response.status_code == 403
        assert result['success'] is False


class TestResults:
    """Tests for GET /api/results/<doc_id>"""

    def test_get_results(self, client, auth_headers):
        """Test getting validation results."""
        doc_id = upload_test_file(client, auth_headers, 'results.pdf')

        # Validate first
        client.post(f'/api/validate/{doc_id}', headers=auth_headers)

        # Get results
        response = client.get(f'/api/results/{doc_id}', headers=auth_headers)
        result = response.get_json()

        assert response.status_code == 200
        assert result['success'] is True
        assert 'scores' in result['data']['result']

    def test_get_results_not_validated(self, client, auth_headers):
        """Test getting results for un-validated document returns 404."""
        doc_id = upload_test_file(client, auth_headers, 'notvalidated.pdf')

        response = client.get(f'/api/results/{doc_id}', headers=auth_headers)
        result = response.get_json()

        assert response.status_code == 404
        assert result['success'] is False


class TestHistory:
    """Tests for GET /api/history"""

    def test_get_history(self, client, auth_headers):
        """Test getting validation history."""
        # Upload and validate a document
        doc_id = upload_test_file(client, auth_headers, 'history.pdf')
        client.post(f'/api/validate/{doc_id}', headers=auth_headers)

        # Get history
        response = client.get('/api/history', headers=auth_headers)
        result = response.get_json()

        assert response.status_code == 200
        assert result['success'] is True
        assert 'results' in result['data']
        assert len(result['data']['results']) >= 1

    def test_get_history_pagination(self, client, auth_headers):
        """Test history pagination."""
        response = client.get('/api/history?page=1&per_page=5', headers=auth_headers)
        result = response.get_json()

        assert response.status_code == 200
        assert 'pagination' in result['data']


class TestRevalidation:
    """Tests for PUT /api/validate/<doc_id>"""

    def test_revalidate_document(self, client, auth_headers):
        """Test force re-validation returns a new result."""
        doc_id = upload_test_file(client, auth_headers, 'revalidate_test.pdf')

        # Validate first time
        first = client.post(f'/api/validate/{doc_id}', headers=auth_headers)
        assert first.status_code == 200

        # Force re-validate
        second = client.put(f'/api/validate/{doc_id}', headers=auth_headers)
        second_result = second.get_json()

        assert second.status_code == 200
        assert second_result['success'] is True
        assert 'result' in second_result['data']
        assert 'scores' in second_result['data']['result']
        assert second_result['data']['result']['verdict'] in ['AUTHENTIC', 'SUSPICIOUS', 'FAKE']
        assert second_result['message'] == 'Re-validation complete'

    def test_revalidate_nonexistent_document(self, client, auth_headers):
        """Test re-validating non-existent document returns 404."""
        response = client.put('/api/validate/99999', headers=auth_headers)
        assert response.status_code == 404
