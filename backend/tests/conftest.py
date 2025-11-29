"""
Pytest fixtures for backend testing.
Provides mock database connections and Flask test client.
"""
from app import app
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def client():
    """Create a Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_db_connection():
    """Create a mock database connection."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


@pytest.fixture
def mock_get_db_connection(mock_db_connection):
    """Patch get_db_connection to return mock connection."""
    mock_conn, mock_cursor = mock_db_connection
    with patch('app.get_db_connection', return_value=mock_conn):
        yield mock_conn, mock_cursor


@pytest.fixture
def sample_person():
    """Sample person data for testing."""
    return {
        'personal_id': 'P001',
        'name': 'John Doe',
        'gender': 'Male',
        'date_of_birth': '1990-01-15',
        'supervisor_id': None
    }


@pytest.fixture
def sample_profile():
    """Sample profile data for testing."""
    return {
        'personal_id': 'P001',
        'job_role': 'Base-level Worker',
        'status': 'Current'
    }


@pytest.fixture
def sample_school():
    """Sample school data for testing."""
    return {
        'department': 'COMP',
        'school_name': 'Computing',
        'faculty': 'Engineering',
        'hq_building': 'Block Y'
    }


@pytest.fixture
def sample_location():
    """Sample location data for testing."""
    return {
        'room': '101',
        'floor': '1',
        'building': 'Block A',
        'type': 'Classroom',
        'campus': 'Main',
        'department': 'COMP'
    }


@pytest.fixture
def sample_activity():
    """Sample activity data for testing."""
    return {
        'activity_id': 'A001',
        'type': 'Seminar',
        'time': '2024-03-15 14:00:00',
        'organiser_id': 'P001',
        'location_id': 1
    }


@pytest.fixture
def sample_maintenance():
    """Sample maintenance data for testing."""
    return {
        'type': 'Cleaning',
        'frequency': 'Daily',
        'location_id': 1,
        'active_chemical': False,
        'contracted_company_id': None
    }


@pytest.fixture
def sample_participation():
    """Sample participation data for testing."""
    return {
        'personal_id': 'P001',
        'activity_id': 'A001'
    }


@pytest.fixture
def sample_affiliation():
    """Sample affiliation data for testing."""
    return {
        'personal_id': 'P001',
        'department': 'COMP'
    }


@pytest.fixture
def sample_external_company():
    """Sample external company data for testing."""
    return {
        'name': 'CleanCo Ltd',
        'contact_info': 'contact@cleanco.com'
    }
