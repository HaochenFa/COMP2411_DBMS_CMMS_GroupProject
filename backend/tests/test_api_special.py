"""
Unit tests for Special API endpoints (Safety Search, Bulk Import).
"""
import pytest
import json
from unittest.mock import patch, MagicMock


class TestSafetySearchEndpoint:
    """Tests for /api/search/safety endpoint."""

    def test_safety_search_success(self, client, mock_get_db_connection):
        """Test GET /api/search/safety returns cleaning tasks."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {'maintenance_id': 1, 'type': 'Cleaning', 'frequency': 'Daily',
             'location_id': 1, 'active_chemical': False, 'building': 'Block A',
             'room': '101', 'floor': '1'}
        ]
        
        response = client.get('/api/search/safety?building=Block A')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['type'] == 'Cleaning'

    def test_safety_search_with_chemical_warning(self, client, mock_get_db_connection):
        """Test GET /api/search/safety adds warning for chemical tasks."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {'maintenance_id': 1, 'type': 'Cleaning', 'frequency': 'Daily',
             'location_id': 1, 'active_chemical': True, 'building': 'Block A',
             'room': '101', 'floor': '1'}
        ]
        
        response = client.get('/api/search/safety?building=Block A')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert 'warning' in data[0]
        assert 'Hazardous' in data[0]['warning']

    def test_safety_search_no_building_filter(self, client, mock_get_db_connection):
        """Test GET /api/search/safety works without building filter."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = []
        
        response = client.get('/api/search/safety')
        
        assert response.status_code == 200


class TestBulkImportEndpoint:
    """Tests for /api/import endpoint."""

    def test_bulk_import_persons_success(self, client, mock_get_db_connection):
        """Test POST /api/import imports persons successfully."""
        mock_conn, mock_cursor = mock_get_db_connection
        
        response = client.post(
            '/api/import',
            data=json.dumps({
                'entity': 'persons',
                'items': [
                    {'personal_id': 'P001', 'name': 'John Doe'},
                    {'personal_id': 'P002', 'name': 'Jane Doe'}
                ]
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert '2 items' in data['message']

    def test_bulk_import_locations_success(self, client, mock_get_db_connection):
        """Test POST /api/import imports locations successfully."""
        mock_conn, mock_cursor = mock_get_db_connection
        
        response = client.post(
            '/api/import',
            data=json.dumps({
                'entity': 'locations',
                'items': [
                    {'room': '101', 'floor': '1', 'building': 'Block A'}
                ]
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201

    def test_bulk_import_activities_success(self, client, mock_get_db_connection):
        """Test POST /api/import imports activities successfully."""
        mock_conn, mock_cursor = mock_get_db_connection
        
        response = client.post(
            '/api/import',
            data=json.dumps({
                'entity': 'activities',
                'items': [
                    {'activity_id': 'A001', 'type': 'Seminar', 'organiser_id': 'P001'}
                ]
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201

    def test_bulk_import_unsupported_entity(self, client, mock_get_db_connection):
        """Test POST /api/import fails for unsupported entity."""
        mock_conn, mock_cursor = mock_get_db_connection
        
        response = client.post(
            '/api/import',
            data=json.dumps({
                'entity': 'unsupported',
                'items': [{'field': 'value'}]
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Unsupported entity' in data['error']

    def test_bulk_import_invalid_items_type(self, client, mock_get_db_connection):
        """Test POST /api/import fails when items is not a list."""
        mock_conn, mock_cursor = mock_get_db_connection
        
        response = client.post(
            '/api/import',
            data=json.dumps({
                'entity': 'persons',
                'items': 'not a list'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'must be a list' in data['error']

    def test_bulk_import_missing_fields(self, client):
        """Test POST /api/import fails when required fields are missing."""
        response = client.post(
            '/api/import',
            data=json.dumps({'entity': 'persons'}),  # Missing items
            content_type='application/json'
        )
        
        assert response.status_code == 400

