"""
Integration tests for complex workflows.
Tests multi-step operations that span multiple entities.
"""

import json

import pytest


class TestPersonProfileWorkflow:
    """Test person with profile creation workflow."""

    def test_create_person_then_profile(self, integration_client, sample_person_data):
        """Test creating a person and then adding a profile."""
        # Create person
        response = integration_client.post(
            "/api/persons",
            data=json.dumps(sample_person_data),
            content_type="application/json",
        )
        assert response.status_code == 201

        # Create profile for person
        profile_data = {
            "personal_id": sample_person_data["personal_id"],
            "job_role": "Manager",
        }
        response = integration_client.post(
            "/api/profiles",
            data=json.dumps(profile_data),
            content_type="application/json",
        )
        assert response.status_code == 201

        # Verify profile exists
        response = integration_client.get("/api/profiles")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert any(p["personal_id"] == sample_person_data["personal_id"] for p in data)


class TestSchoolAffiliationWorkflow:
    """Test school and affiliation workflow."""

    def test_create_school_person_affiliation(
        self, integration_client, sample_person_data, sample_school_data
    ):
        """Test creating school, person, and linking them via affiliation."""
        # Create school
        response = integration_client.post(
            "/api/schools",
            data=json.dumps(sample_school_data),
            content_type="application/json",
        )
        assert response.status_code == 201

        # Create person
        response = integration_client.post(
            "/api/persons",
            data=json.dumps(sample_person_data),
            content_type="application/json",
        )
        assert response.status_code == 201

        # Create affiliation
        affiliation_data = {
            "personal_id": sample_person_data["personal_id"],
            "department": sample_school_data["department"],
        }
        response = integration_client.post(
            "/api/affiliations",
            data=json.dumps(affiliation_data),
            content_type="application/json",
        )
        assert response.status_code == 201

        # Verify affiliation exists
        response = integration_client.get("/api/affiliations")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert any(
            a["personal_id"] == sample_person_data["personal_id"]
            and a["department"] == sample_school_data["department"]
            for a in data
        )


class TestMaintenanceWorkflow:
    """Test maintenance task workflow."""

    def test_create_location_then_maintenance(
        self, integration_client, sample_location_data
    ):
        """Test creating a location and then adding maintenance tasks."""
        # Create location
        response = integration_client.post(
            "/api/locations",
            data=json.dumps(sample_location_data),
            content_type="application/json",
        )
        assert response.status_code == 201

        # Get location ID
        response = integration_client.get("/api/locations")
        data = json.loads(response.data)
        location_id = data[0]["location_id"]

        # Create maintenance task
        maintenance_data = {
            "type": "Cleaning",
            "frequency": "Daily",
            "location_id": location_id,
            "active_chemical": False,
        }
        response = integration_client.post(
            "/api/maintenance",
            data=json.dumps(maintenance_data),
            content_type="application/json",
        )
        assert response.status_code == 201

        # Verify maintenance task exists
        response = integration_client.get("/api/maintenance")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert any(m["location_id"] == location_id for m in data)


class TestBulkImportWorkflow:
    """Test bulk import functionality."""

    def test_bulk_import_persons(self, integration_client):
        """Test bulk importing multiple persons."""
        import_data = {
            "entity": "persons",
            "items": [
                {"personal_id": "BULK001", "name": "Bulk Person 1"},
                {"personal_id": "BULK002", "name": "Bulk Person 2"},
                {"personal_id": "BULK003", "name": "Bulk Person 3"},
            ],
        }

        response = integration_client.post(
            "/api/import", data=json.dumps(import_data), content_type="application/json"
        )
        assert response.status_code == 201

        # Verify all persons were created
        response = integration_client.get("/api/persons")
        data = json.loads(response.data)
        ids = [p["personal_id"] for p in data]
        assert "BULK001" in ids
        assert "BULK002" in ids
        assert "BULK003" in ids


class TestSafetySearchWorkflow:
    """Test safety search functionality."""

    def test_safety_search_with_chemical(
        self, integration_client, sample_location_data
    ):
        """Test safety search finds maintenance with chemicals."""
        # Create location
        response = integration_client.post(
            "/api/locations",
            data=json.dumps(sample_location_data),
            content_type="application/json",
        )
        assert response.status_code == 201

        # Get location ID
        response = integration_client.get("/api/locations")
        data = json.loads(response.data)
        location_id = data[0]["location_id"]

        # Create maintenance with chemicals
        maintenance_data = {
            "type": "Cleaning",
            "frequency": "Daily",
            "location_id": location_id,
            "active_chemical": True,
        }
        response = integration_client.post(
            "/api/maintenance",
            data=json.dumps(maintenance_data),
            content_type="application/json",
        )
        assert response.status_code == 201

        # Search for safety info
        response = integration_client.get(
            f'/api/search/safety?building={sample_location_data["building"]}'
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        # Verify warning is present for chemical maintenance
        assert any(
            m.get("active_chemical") == True
            or m.get("active_chemical") == 1
            or "warning" in m
            for m in data
        )
