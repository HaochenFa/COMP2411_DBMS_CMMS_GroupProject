"""
Unit tests for Activity API endpoints.
"""

import json
from unittest.mock import MagicMock, patch

import pytest


class TestActivitiesEndpoint:
    """Tests for /api/activities endpoint."""

    def test_get_activities_success(self, client, mock_get_db_connection):
        """Test GET /api/activities returns list of activities."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {
                "activity_id": "A001",
                "type": "Seminar",
                "time": "2024-03-15 14:00:00",
                "organiser_name": "John Doe",
                "building": "Block A",
                "room": "101",
                "floor": "1",
            }
        ]

        response = client.get("/api/activities")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]["type"] == "Seminar"

    def test_create_activity_success(
        self, client, mock_get_db_connection, sample_activity
    ):
        """Test POST /api/activities creates a new activity."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.post(
            "/api/activities",
            data=json.dumps(sample_activity),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["message"] == "Activity created"

    def test_create_activity_missing_fields(self, client, mock_get_db_connection):
        """Test POST /api/activities fails when required fields are missing."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.post(
            "/api/activities",
            data=json.dumps({"activity_id": "A001"}),  # Missing organiser_id
            content_type="application/json",
        )

        assert response.status_code == 400


class TestActivityItemEndpoint:
    """Tests for /api/activities/<id> endpoint."""

    def test_update_activity_success(self, client, mock_get_db_connection):
        """Test PUT /api/activities/<id> updates an activity."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 1

        response = client.put(
            "/api/activities/A001",
            data=json.dumps({"type": "Workshop"}),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Activity updated"

    def test_update_activity_not_found(self, client, mock_get_db_connection):
        """Test PUT /api/activities/<id> returns 404 when activity not found."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 0

        response = client.put(
            "/api/activities/INVALID",
            data=json.dumps({"type": "Workshop"}),
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_update_activity_no_fields(self, client, mock_get_db_connection):
        """Test PUT /api/activities/<id> fails when no fields provided."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.put(
            "/api/activities/A001", data=json.dumps({}), content_type="application/json"
        )

        assert response.status_code == 400

    def test_delete_activity_success(self, client, mock_get_db_connection):
        """Test DELETE /api/activities/<id> deletes an activity."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 1

        response = client.delete("/api/activities/A001")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Activity deleted"

    def test_delete_activity_not_found(self, client, mock_get_db_connection):
        """Test DELETE /api/activities/<id> returns 404 when activity not found."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 0

        response = client.delete("/api/activities/INVALID")

        assert response.status_code == 404
