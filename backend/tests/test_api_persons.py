"""
Unit tests for Person API endpoints.
"""
import pytest
import json
from unittest.mock import patch, MagicMock


class TestPersonsEndpoint:
    """Tests for /api/persons endpoint."""

    def test_get_persons_success(self, client, mock_get_db_connection):
        """Test GET /api/persons returns list of persons."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {'personal_id': 'P001', 'name': 'John Doe', 'gender': 'Male', 
             'date_of_birth': '1990-01-15', 'entry_date': '2020-01-01', 
             'supervisor_id': None, 'age': 34}
        ]
        
        response = client.get('/api/persons')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['name'] == 'John Doe'

    def test_get_persons_db_connection_failure(self, client):
        """Test GET /api/persons handles db connection failure."""
        with patch('app.get_db_connection', return_value=None):
            response = client.get('/api/persons')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data

    def test_create_person_success(self, client, mock_get_db_connection, sample_person):
        """Test POST /api/persons creates a new person."""
        mock_conn, mock_cursor = mock_get_db_connection
        
        response = client.post(
            '/api/persons',
            data=json.dumps(sample_person),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Person created'

    def test_create_person_missing_required_fields(self, client, mock_get_db_connection):
        """Test POST /api/persons fails when required fields are missing."""
        mock_conn, mock_cursor = mock_get_db_connection
        
        response = client.post(
            '/api/persons',
            data=json.dumps({'name': 'John'}),  # Missing personal_id
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_create_person_invalid_json(self, client):
        """Test POST /api/persons fails with invalid JSON."""
        response = client.post(
            '/api/persons',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400


class TestPersonItemEndpoint:
    """Tests for /api/persons/<id> endpoint."""

    def test_update_person_success(self, client, mock_get_db_connection):
        """Test PUT /api/persons/<id> updates a person."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 1
        
        response = client.put(
            '/api/persons/P001',
            data=json.dumps({'name': 'Jane Doe'}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Person updated'

    def test_update_person_not_found(self, client, mock_get_db_connection):
        """Test PUT /api/persons/<id> returns 404 when person not found."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 0
        
        response = client.put(
            '/api/persons/INVALID',
            data=json.dumps({'name': 'Jane Doe'}),
            content_type='application/json'
        )
        
        assert response.status_code == 404

    def test_update_person_no_fields(self, client, mock_get_db_connection):
        """Test PUT /api/persons/<id> fails when no fields provided."""
        mock_conn, mock_cursor = mock_get_db_connection
        
        response = client.put(
            '/api/persons/P001',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400

    def test_delete_person_success(self, client, mock_get_db_connection):
        """Test DELETE /api/persons/<id> deletes a person."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 1
        
        response = client.delete('/api/persons/P001')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Person deleted'

    def test_delete_person_not_found(self, client, mock_get_db_connection):
        """Test DELETE /api/persons/<id> returns 404 when person not found."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 0
        
        response = client.delete('/api/persons/INVALID')
        
        assert response.status_code == 404

