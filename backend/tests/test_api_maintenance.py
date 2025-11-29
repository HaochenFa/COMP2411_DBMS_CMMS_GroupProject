"""
Unit tests for Maintenance API endpoints.
"""
import pytest
import json
from unittest.mock import patch, MagicMock


class TestMaintenanceEndpoint:
    """Tests for /api/maintenance endpoint."""

    def test_get_maintenance_success(self, client, mock_get_db_connection):
        """Test GET /api/maintenance returns list of maintenance tasks."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {'maintenance_id': 1, 'type': 'Cleaning', 'frequency': 'Daily',
             'location_id': 1, 'active_chemical': False, 'contracted_company_id': None,
             'building': 'Block A', 'room': '101', 'campus': 'Main'}
        ]

        response = client.get('/api/maintenance')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['type'] == 'Cleaning'

    def test_create_maintenance_success(self, client, mock_get_db_connection, sample_maintenance):
        """Test POST /api/maintenance creates a new maintenance task."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.post(
            '/api/maintenance',
            data=json.dumps(sample_maintenance),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Maintenance task created'

    def test_create_maintenance_missing_fields(self, client, mock_get_db_connection):
        """Test POST /api/maintenance fails when required fields are missing."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.post(
            '/api/maintenance',
            data=json.dumps({'type': 'Cleaning'}),  # Missing location_id
            content_type='application/json'
        )

        assert response.status_code == 400


class TestMaintenanceItemEndpoint:
    """Tests for /api/maintenance/<id> endpoint."""

    def test_update_maintenance_success(self, client, mock_get_db_connection):
        """Test PUT /api/maintenance/<id> updates a maintenance task."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 1

        response = client.put(
            '/api/maintenance/1',
            data=json.dumps({'frequency': 'Weekly', 'active_chemical': True}),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Maintenance task updated'

    def test_update_maintenance_not_found(self, client, mock_get_db_connection):
        """Test PUT /api/maintenance/<id> returns 404 when task not found."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 0

        response = client.put(
            '/api/maintenance/999',
            data=json.dumps({'frequency': 'Weekly'}),
            content_type='application/json'
        )

        assert response.status_code == 404

    def test_update_maintenance_no_fields(self, client, mock_get_db_connection):
        """Test PUT /api/maintenance/<id> fails when no fields provided."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.put(
            '/api/maintenance/1',
            data=json.dumps({}),
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_delete_maintenance_success(self, client, mock_get_db_connection):
        """Test DELETE /api/maintenance/<id> deletes a maintenance task."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 1

        response = client.delete('/api/maintenance/1')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Maintenance task deleted'

    def test_delete_maintenance_not_found(self, client, mock_get_db_connection):
        """Test DELETE /api/maintenance/<id> returns 404 when task not found."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 0

        response = client.delete('/api/maintenance/999')

        assert response.status_code == 404
