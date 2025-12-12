"""
Integration tests for API endpoints with real database.
These tests verify the complete flow from API to database and back.

To run these tests, you need a running MySQL database.
Set the following environment variables:
- TEST_DB_HOST (default: localhost)
- TEST_DB_PORT (default: 3306)
- TEST_DB_USER (default: root)
- TEST_DB_PASSWORD (default: rootpassword)
- TEST_DB_NAME (default: cmms_test)

Run with: pytest backend/tests/integration/ -v
"""

import json

import pytest


class TestPersonIntegration:
    """Integration tests for Person CRUD operations."""

    def test_full_person_lifecycle(self, integration_client, sample_person_data):
        """Test creating, reading, updating, and deleting a person."""
        # Create
        response = integration_client.post(
            "/api/persons",
            data=json.dumps(sample_person_data),
            content_type="application/json",
        )
        assert response.status_code == 201

        # Read (list)
        response = integration_client.get("/api/persons")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
        assert any(p["personal_id"] == "TEST001" for p in data)

        # Update
        response = integration_client.put(
            f"/api/persons/{sample_person_data['personal_id']}",
            data=json.dumps({"name": "Updated Name"}),
            content_type="application/json",
        )
        assert response.status_code == 200

        # Verify update
        response = integration_client.get("/api/persons")
        data = json.loads(response.data)
        person = next(p for p in data if p["personal_id"] == "TEST001")
        assert person["name"] == "Updated Name"

        # Delete
        response = integration_client.delete(
            f"/api/persons/{sample_person_data['personal_id']}"
        )
        assert response.status_code == 200

        # Verify deletion
        response = integration_client.get("/api/persons")
        data = json.loads(response.data)
        assert not any(p["personal_id"] == "TEST001" for p in data)


class TestSchoolIntegration:
    """Integration tests for School CRUD operations."""

    def test_full_school_lifecycle(self, integration_client, sample_school_data):
        """Test creating, reading, updating, and deleting a school."""
        # Create
        response = integration_client.post(
            "/api/schools",
            data=json.dumps(sample_school_data),
            content_type="application/json",
        )
        assert response.status_code == 201

        # Read
        response = integration_client.get("/api/schools")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert any(s["department"] == "TEST" for s in data)

        # Update
        response = integration_client.put(
            f"/api/schools/{sample_school_data['department']}",
            data=json.dumps({"school_name": "Updated School"}),
            content_type="application/json",
        )
        assert response.status_code == 200

        # Delete
        response = integration_client.delete(
            f"/api/schools/{sample_school_data['department']}"
        )
        assert response.status_code == 200


class TestLocationIntegration:
    """Integration tests for Location CRUD operations."""

    def test_full_location_lifecycle(self, integration_client, sample_location_data):
        """Test creating, reading, updating, and deleting a location."""
        # Create
        response = integration_client.post(
            "/api/locations",
            data=json.dumps(sample_location_data),
            content_type="application/json",
        )
        assert response.status_code == 201

        # Read
        response = integration_client.get("/api/locations")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
        location = data[0]
        location_id = location["location_id"]

        # Update
        response = integration_client.put(
            f"/api/locations/{location_id}",
            data=json.dumps({"room": "T102"}),
            content_type="application/json",
        )
        assert response.status_code == 200

        # Delete
        response = integration_client.delete(f"/api/locations/{location_id}")
        assert response.status_code == 200


class TestHealthCheck:
    """Integration tests for health check endpoint."""

    def test_health_check(self, integration_client):
        """Test that health check returns healthy status."""
        response = integration_client.get("/api/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"


class TestReportsIntegration:
    """Integration tests for report endpoints."""

    def test_maintenance_summary_empty(self, integration_client):
        """Test maintenance summary with empty database."""
        response = integration_client.get("/api/reports/maintenance-summary")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_people_summary_empty(self, integration_client):
        """Test people summary with empty database."""
        response = integration_client.get("/api/reports/people-summary")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
