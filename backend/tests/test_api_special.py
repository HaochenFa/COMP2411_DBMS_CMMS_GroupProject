"""
Unit tests for Special API endpoints (Safety Search, Bulk Import).
"""

import json
from unittest.mock import MagicMock, patch

import pytest


class TestSafetySearchEndpoint:
    """Tests for /api/search/safety endpoint."""

    def test_safety_search_success(self, client, mock_get_db_connection):
        """Test GET /api/search/safety returns cleaning tasks."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {
                "maintenance_id": 1,
                "type": "Cleaning",
                "frequency": "Daily",
                "location_id": 1,
                "active_chemical": False,
                "building": "Block A",
                "room": "101",
                "floor": "1",
            }
        ]

        response = client.get("/api/search/safety?building=Block A")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]["type"] == "Cleaning"

    def test_safety_search_with_chemical_warning(self, client, mock_get_db_connection):
        """Test GET /api/search/safety adds warning for chemical tasks."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {
                "maintenance_id": 1,
                "type": "Cleaning",
                "frequency": "Daily",
                "location_id": 1,
                "active_chemical": True,
                "building": "Block A",
                "room": "101",
                "floor": "1",
            }
        ]

        response = client.get("/api/search/safety?building=Block A")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert "warning" in data[0]
        assert "Hazardous" in data[0]["warning"]

    def test_safety_search_no_building_filter(self, client, mock_get_db_connection):
        """Test GET /api/search/safety works without building filter."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = []

        response = client.get("/api/search/safety")

        assert response.status_code == 200

    def test_safety_search_with_time_period(self, client, mock_get_db_connection):
        """Test GET /api/search/safety with start_time and end_time filters."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {
                "maintenance_id": 1,
                "type": "Cleaning",
                "frequency": "Daily",
                "location_id": 1,
                "active_chemical": False,
                "building": "Block A",
                "room": "101",
                "floor": "1",
                "campus": "Main",
                "scheduled_time": "2024-01-15T10:00:00",
                "end_time": "2024-01-15T12:00:00",
                "company_name": None,
            }
        ]

        response = client.get(
            "/api/search/safety?building=Block A&start_time=2024-01-01&end_time=2024-01-31"
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1


class TestBuildingSupervisionEndpoints:
    """Tests for /api/building-supervision endpoints."""

    def test_get_building_supervisions(self, client, mock_get_db_connection):
        """Test GET /api/building-supervision returns all supervisions."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {
                "supervision_id": 1,
                "personal_id": "P001",
                "building": "Block A",
                "assigned_date": "2024-01-01",
                "manager_name": "John Manager",
            }
        ]

        response = client.get("/api/building-supervision")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "data" in data
        assert len(data["data"]) == 1
        assert data["data"][0]["building"] == "Block A"

    def test_create_building_supervision(self, client, mock_get_db_connection):
        """Test POST /api/building-supervision creates a new supervision."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.lastrowid = 1

        response = client.post(
            "/api/building-supervision",
            data=json.dumps({"personal_id": "P001", "building": "Block A"}),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert "id" in data

    def test_create_building_supervision_missing_fields(
        self, client, mock_get_db_connection
    ):
        """Test POST /api/building-supervision fails with missing fields."""
        response = client.post(
            "/api/building-supervision",
            data=json.dumps({"personal_id": "P001"}),  # Missing building
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_delete_building_supervision(self, client, mock_get_db_connection):
        """Test DELETE /api/building-supervision/<id> removes supervision."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 1

        response = client.delete("/api/building-supervision/1")

        assert response.status_code == 200

    def test_delete_building_supervision_not_found(
        self, client, mock_get_db_connection
    ):
        """Test DELETE /api/building-supervision/<id> returns 404 if not found."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 0

        response = client.delete("/api/building-supervision/999")

        assert response.status_code == 404

    def test_get_supervisions_by_manager(self, client, mock_get_db_connection):
        """Test GET /api/building-supervision/by-manager/<id> returns manager's buildings."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {"supervision_id": 1, "building": "Block A", "assigned_date": "2024-01-01"},
            {"supervision_id": 2, "building": "Block B", "assigned_date": "2024-01-02"},
        ]

        response = client.get("/api/building-supervision/by-manager/P001")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["data"]) == 2

    def test_get_supervisions_by_building(self, client, mock_get_db_connection):
        """Test GET /api/building-supervision/by-building/<building> returns building's managers."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {
                "supervision_id": 1,
                "personal_id": "P001",
                "assigned_date": "2024-01-01",
                "manager_name": "John Manager",
            }
        ]

        response = client.get("/api/building-supervision/by-building/Block%20A")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["data"]) == 1


class TestManagerBuildingReport:
    """Tests for /api/reports/manager-buildings endpoint."""

    def test_get_manager_building_report(self, client, mock_get_db_connection):
        """Test GET /api/reports/manager-buildings returns hierarchical report."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {
                "personal_id": "P001",
                "manager_name": "John Manager",
                "building": "Block A",
                "assigned_date": None,
                "maintenance_count": 5,
                "chemical_maintenance_count": 1,
            }
        ]

        response = client.get("/api/reports/manager-buildings")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "data" in data
        assert "summary" in data
        assert data["summary"]["total_managers"] == 1


class TestBulkImportEndpoint:
    """Tests for /api/import endpoint."""

    def test_bulk_import_persons_success(self, client, mock_get_db_connection):
        """Test POST /api/import imports persons successfully."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.post(
            "/api/import",
            data=json.dumps(
                {
                    "entity": "persons",
                    "items": [
                        {"personal_id": "P001", "name": "John Doe"},
                        {"personal_id": "P002", "name": "Jane Doe"},
                    ],
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert "2 items" in data["message"]

    def test_bulk_import_locations_success(self, client, mock_get_db_connection):
        """Test POST /api/import imports locations successfully."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.post(
            "/api/import",
            data=json.dumps(
                {
                    "entity": "locations",
                    "items": [{"room": "101", "floor": "1", "building": "Block A"}],
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 201

    def test_bulk_import_activities_success(self, client, mock_get_db_connection):
        """Test POST /api/import imports activities successfully."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.post(
            "/api/import",
            data=json.dumps(
                {
                    "entity": "activities",
                    "items": [
                        {
                            "activity_id": "A001",
                            "type": "Seminar",
                            "organiser_id": "P001",
                        }
                    ],
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 201

    def test_bulk_import_unsupported_entity(self, client, mock_get_db_connection):
        """Test POST /api/import fails for unsupported entity."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.post(
            "/api/import",
            data=json.dumps({"entity": "unsupported", "items": [{"field": "value"}]}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Unsupported entity" in data["error"]

    def test_bulk_import_invalid_items_type(self, client, mock_get_db_connection):
        """Test POST /api/import fails when items is not a list."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.post(
            "/api/import",
            data=json.dumps({"entity": "persons", "items": "not a list"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "must be a list" in data["error"]

    def test_bulk_import_missing_fields(self, client):
        """Test POST /api/import fails when required fields are missing."""
        response = client.post(
            "/api/import",
            data=json.dumps({"entity": "persons"}),  # Missing items
            content_type="application/json",
        )

        assert response.status_code == 400
