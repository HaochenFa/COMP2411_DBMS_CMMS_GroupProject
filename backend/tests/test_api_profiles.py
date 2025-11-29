"""
Unit tests for Profile API endpoints.
"""
import pytest
import json
from unittest.mock import patch, MagicMock
import mysql.connector


class TestProfilesEndpoint:
    """Tests for /api/profiles endpoint."""

    def test_get_profiles_success(self, client, mock_get_db_connection):
        """Test GET /api/profiles returns list of profiles."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {'personal_id': 'P001', 'name': 'John Doe', 'job_role': 'Manager',
             'status': 'Current'}
        ]

        response = client.get('/api/profiles')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['job_role'] == 'Manager'

    def test_create_profile_success(self, client, mock_get_db_connection, sample_profile):
        """Test POST /api/profiles creates a new profile."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchone.return_value = {'count': 0}

        response = client.post(
            '/api/profiles',
            data=json.dumps(sample_profile),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Profile created'

    def test_create_profile_missing_required_fields(self, client, mock_get_db_connection):
        """Test POST /api/profiles fails when required fields are missing."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.post(
            '/api/profiles',
            data=json.dumps({'personal_id': 'P001'}),  # Missing job_role
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_create_profile_mid_level_limit(self, client, mock_get_db_connection):
        """Test POST /api/profiles enforces Mid-level Manager limit."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchone.return_value = {'count': 10}  # At limit

        response = client.post(
            '/api/profiles',
            data=json.dumps({
                'personal_id': 'P002',
                'job_role': 'Mid-level Manager'
            }),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Limit reached' in data['error']

    def test_create_profile_base_level_limit(self, client, mock_get_db_connection):
        """Test POST /api/profiles enforces Base-level Worker limit."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchone.return_value = {'count': 50}  # At limit

        response = client.post(
            '/api/profiles',
            data=json.dumps({
                'personal_id': 'P002',
                'job_role': 'Base-level Worker'
            }),
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_create_profile_db_error(self, client, mock_get_db_connection):
        """Test POST /api/profiles handles database errors."""
        mock_conn, mock_cursor = mock_get_db_connection

        # For 'Manager' role, INSERT is the first execute call (no count query)
        mock_cursor.execute.side_effect = mysql.connector.Error(
            "Duplicate entry")

        response = client.post(
            '/api/profiles',
            data=json.dumps({
                'personal_id': 'P001',
                'job_role': 'Manager'
            }),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Duplicate entry' in data['error']
