"""
Unit tests for School API endpoints.
"""
import pytest
import json
from unittest.mock import patch, MagicMock


class TestSchoolsEndpoint:
    """Tests for /api/schools endpoint."""

    def test_get_schools_success(self, client, mock_get_db_connection):
        """Test GET /api/schools returns list of schools."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {'department': 'COMP', 'school_name': 'Computing', 
             'faculty': 'Engineering', 'hq_building': 'Block Y'}
        ]
        
        response = client.get('/api/schools')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['school_name'] == 'Computing'

    def test_create_school_success(self, client, mock_get_db_connection, sample_school):
        """Test POST /api/schools creates a new school."""
        mock_conn, mock_cursor = mock_get_db_connection
        
        response = client.post(
            '/api/schools',
            data=json.dumps(sample_school),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Department created'

    def test_create_school_missing_fields(self, client, mock_get_db_connection):
        """Test POST /api/schools fails when required fields are missing."""
        mock_conn, mock_cursor = mock_get_db_connection
        
        response = client.post(
            '/api/schools',
            data=json.dumps({'department': 'COMP'}),  # Missing school_name
            content_type='application/json'
        )
        
        assert response.status_code == 400


class TestSchoolItemEndpoint:
    """Tests for /api/schools/<id> endpoint."""

    def test_update_school_success(self, client, mock_get_db_connection):
        """Test PUT /api/schools/<id> updates a school."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 1
        
        response = client.put(
            '/api/schools/COMP',
            data=json.dumps({'school_name': 'Computer Science'}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Department updated'

    def test_update_school_not_found(self, client, mock_get_db_connection):
        """Test PUT /api/schools/<id> returns 404 when school not found."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 0
        
        response = client.put(
            '/api/schools/INVALID',
            data=json.dumps({'school_name': 'New Name'}),
            content_type='application/json'
        )
        
        assert response.status_code == 404

    def test_update_school_no_fields(self, client, mock_get_db_connection):
        """Test PUT /api/schools/<id> fails when no valid fields provided."""
        mock_conn, mock_cursor = mock_get_db_connection
        
        response = client.put(
            '/api/schools/COMP',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400

    def test_delete_school_success(self, client, mock_get_db_connection):
        """Test DELETE /api/schools/<id> deletes a school."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 1
        
        response = client.delete('/api/schools/COMP')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Department deleted'

    def test_delete_school_not_found(self, client, mock_get_db_connection):
        """Test DELETE /api/schools/<id> returns 404 when school not found."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 0
        
        response = client.delete('/api/schools/INVALID')
        
        assert response.status_code == 404

