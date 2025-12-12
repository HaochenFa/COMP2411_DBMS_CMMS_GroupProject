"""
Unit tests for Relationship API endpoints (Participations and Affiliations).
"""

import json
from unittest.mock import MagicMock, patch

import pytest


class TestParticipationsEndpoint:
    """Tests for /api/participations endpoint."""

    def test_get_participations_success(self, client, mock_get_db_connection):
        """Test GET /api/participations returns list of participations."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {
                "personal_id": "P001",
                "person_name": "John Doe",
                "activity_id": "A001",
                "activity_type": "Seminar",
                "activity_time": "2024-03-15 14:00:00",
                "building": "Block A",
                "room": "101",
            }
        ]

        response = client.get("/api/participations")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]["person_name"] == "John Doe"

    def test_create_participation_success(
        self, client, mock_get_db_connection, sample_participation
    ):
        """Test POST /api/participations creates a new participation."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.post(
            "/api/participations",
            data=json.dumps(sample_participation),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["message"] == "Participation added"

    def test_create_participation_missing_fields(self, client, mock_get_db_connection):
        """Test POST /api/participations fails when required fields are missing."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.post(
            "/api/participations",
            data=json.dumps({"personal_id": "P001"}),  # Missing activity_id
            content_type="application/json",
        )

        assert response.status_code == 400


class TestAffiliationsEndpoint:
    """Tests for /api/affiliations endpoint."""

    def test_get_affiliations_success(self, client, mock_get_db_connection):
        """Test GET /api/affiliations returns list of affiliations."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {
                "personal_id": "P001",
                "person_name": "John Doe",
                "department": "COMP",
                "school_name": "Computing",
            }
        ]

        response = client.get("/api/affiliations")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]["department"] == "COMP"

    def test_create_affiliation_success(
        self, client, mock_get_db_connection, sample_affiliation
    ):
        """Test POST /api/affiliations creates a new affiliation."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.post(
            "/api/affiliations",
            data=json.dumps(sample_affiliation),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["message"] == "Affiliation added"

    def test_create_affiliation_missing_fields(self, client, mock_get_db_connection):
        """Test POST /api/affiliations fails when required fields are missing."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.post(
            "/api/affiliations",
            data=json.dumps({"personal_id": "P001"}),  # Missing department
            content_type="application/json",
        )

        assert response.status_code == 400


class TestExternalCompaniesEndpoint:
    """Tests for /api/external-companies endpoint."""

    def test_get_companies_success(self, client, mock_get_db_connection):
        """Test GET /api/external-companies returns list of companies."""
        mock_conn, mock_cursor = mock_get_db_connection
        mock_cursor.fetchall.return_value = [
            {"company_id": 1, "name": "CleanCo", "contact_info": "info@cleanco.com"}
        ]

        response = client.get("/api/external-companies")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1

    def test_create_company_success(
        self, client, mock_get_db_connection, sample_external_company
    ):
        """Test POST /api/external-companies creates a new company."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.post(
            "/api/external-companies",
            data=json.dumps(sample_external_company),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["message"] == "External Company created"

    def test_create_company_missing_name(self, client, mock_get_db_connection):
        """Test POST /api/external-companies fails when name is missing."""
        mock_conn, mock_cursor = mock_get_db_connection

        response = client.post(
            "/api/external-companies",
            data=json.dumps({"contact_info": "info@test.com"}),
            content_type="application/json",
        )

        assert response.status_code == 400
