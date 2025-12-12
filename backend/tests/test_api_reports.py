"""
Unit tests for Report API endpoints.
"""

import json
from unittest.mock import MagicMock, patch

import pytest


class TestMaintenanceSummaryReport:
    """Tests for /api/reports/maintenance-summary endpoint."""

    def test_maintenance_summary_success(self, client, mock_get_db_connection):
        """Test GET /api/reports/maintenance-summary returns summary."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {"type": "Cleaning", "building": "Block A", "campus": "Main", "count": 5},
            {"type": "Repair", "building": "Block B", "campus": "Main", "count": 3},
        ]

        response = client.get("/api/reports/maintenance-summary")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        assert data[0]["count"] == 5


class TestPeopleSummaryReport:
    """Tests for /api/reports/people-summary endpoint."""

    def test_people_summary_success(self, client, mock_get_db_connection):
        """Test GET /api/reports/people-summary returns summary."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {"job_role": "Manager", "status": "Current", "count": 10},
            {"job_role": "Worker", "status": "Current", "count": 50},
        ]

        response = client.get("/api/reports/people-summary")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2


class TestActivitiesSummaryReport:
    """Tests for /api/reports/activities-summary endpoint."""

    def test_activities_summary_success(self, client, mock_get_db_connection):
        """Test GET /api/reports/activities-summary returns summary."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {"type": "Seminar", "organiser_name": "John Doe", "activity_count": 5}
        ]

        response = client.get("/api/reports/activities-summary")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]["activity_count"] == 5


class TestSchoolStatsReport:
    """Tests for /api/reports/school-stats endpoint."""

    def test_school_stats_success(self, client, mock_get_db_connection):
        """Test GET /api/reports/school-stats returns statistics."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {
                "department": "COMP",
                "school_name": "Computing",
                "faculty": "Engineering",
                "affiliated_people": 25,
                "locations_count": 10,
            }
        ]

        response = client.get("/api/reports/school-stats")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]["affiliated_people"] == 25


class TestMaintenanceFrequencyReport:
    """Tests for /api/reports/maintenance-frequency endpoint."""

    def test_maintenance_frequency_success(self, client, mock_get_db_connection):
        """Test GET /api/reports/maintenance-frequency returns frequency analysis."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {"frequency": "Daily", "type": "Cleaning", "task_count": 20},
            {"frequency": "Weekly", "type": "Repair", "task_count": 10},
        ]

        response = client.get("/api/reports/maintenance-frequency")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        assert data[0]["task_count"] == 20


class TestHealthCheck:
    """Tests for /api/health endpoint."""

    def test_health_check_success(self, client):
        """Test GET /api/health returns healthy status."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"


class TestQueryEndpoint:
    """Tests for /api/query endpoint."""

    def test_select_query_success(self, client, mock_get_db_connection):
        """Test POST /api/query with SELECT statement."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [{"name": "John"}]

        response = client.post(
            "/api/query",
            data=json.dumps({"query": "SELECT * FROM Person"}),
            content_type="application/json",
        )

        assert response.status_code == 200

    def test_write_query_success(self, client, mock_get_db_connection):
        """Test POST /api/query with write statement."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.rowcount = 1

        response = client.post(
            "/api/query",
            data=json.dumps(
                {"query": "UPDATE Person SET name='Jane' WHERE personal_id='P001'"}
            ),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "rows_affected" in data

    def test_empty_query_fails(self, client, mock_get_db_connection):
        """Test POST /api/query with empty query fails."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.post(
            "/api/query",
            data=json.dumps({"query": "   "}),
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_missing_query_fails(self, client):
        """Test POST /api/query without query parameter fails."""
        response = client.post(
            "/api/query", data=json.dumps({}), content_type="application/json"
        )

        assert response.status_code == 400
