"""
Unit tests for Location API endpoints.
"""

import json
from unittest.mock import MagicMock, patch

import pytest


class TestLocationsEndpoint:
    """Tests for /api/locations endpoint."""

    def test_get_locations_success(self, client, mock_get_db_connection):
        """Test GET /api/locations returns list of locations."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {
                "location_id": 1,
                "room": "101",
                "floor": "1",
                "building": "Block A",
                "type": "Classroom",
                "campus": "Main",
                "department": "COMP",
                "dept_name": "Computing",
                "faculty": "Engineering",
            }
        ]

        response = client.get("/api/locations")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]["building"] == "Block A"

    def test_create_location_success(
        self, client, mock_get_db_connection, sample_location
    ):
        """Test POST /api/locations creates a new location."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.post(
            "/api/locations",
            data=json.dumps(sample_location),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["message"] == "Location created"

    def test_create_location_minimal_data(self, client, mock_get_db_connection):
        """Test POST /api/locations works with minimal data."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.post(
            "/api/locations",
            data=json.dumps({"building": "Block B"}),
            content_type="application/json",
        )

        assert response.status_code == 201


class TestLocationItemEndpoint:
    """Tests for /api/locations/<id> endpoint."""

    def test_update_location_success(self, client, mock_get_db_connection):
        """Test PUT /api/locations/<id> updates a location."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 1

        response = client.put(
            "/api/locations/1",
            data=json.dumps({"room": "102", "floor": "2"}),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Location updated"

    def test_update_location_not_found(self, client, mock_get_db_connection):
        """Test PUT /api/locations/<id> returns 404 when location not found."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 0

        response = client.put(
            "/api/locations/999",
            data=json.dumps({"room": "102"}),
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_update_location_no_fields(self, client, mock_get_db_connection):
        """Test PUT /api/locations/<id> fails when no fields provided."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.put(
            "/api/locations/1", data=json.dumps({}), content_type="application/json"
        )

        assert response.status_code == 400

    def test_delete_location_success(self, client, mock_get_db_connection):
        """Test DELETE /api/locations/<id> deletes a location."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchone.return_value = {"count": 0}  # No maintenance tasks
        mock_cursor.rowcount = 1

        response = client.delete("/api/locations/1")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Location deleted"

    def test_delete_location_with_maintenance(self, client, mock_get_db_connection):
        """Test DELETE /api/locations/<id> fails when location has maintenance."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchone.return_value = {"count": 5}  # Has maintenance tasks

        response = client.delete("/api/locations/1")

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Cannot delete" in data["error"]

    def test_delete_location_not_found(self, client, mock_get_db_connection):
        """Test DELETE /api/locations/<id> returns 404 when location not found."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchone.return_value = {"count": 0}
        mock_cursor.rowcount = 0

        response = client.delete("/api/locations/999")

        assert response.status_code == 404
