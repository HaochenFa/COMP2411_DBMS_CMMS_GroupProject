"""
Integration test fixtures.
These tests require a running MySQL database.
"""
import pytest
import os
import mysql.connector
from app import app

# Integration test database configuration
TEST_DB_CONFIG = {
    'host': os.environ.get('TEST_DB_HOST', 'localhost'),
    'port': int(os.environ.get('TEST_DB_PORT', '3306')),
    'user': os.environ.get('TEST_DB_USER', 'root'),
    'password': os.environ.get('TEST_DB_PASSWORD', 'rootpassword'),
    'database': os.environ.get('TEST_DB_NAME', 'cmms_test'),
}


@pytest.fixture(scope='session')
def db_connection():
    """Create a database connection for integration tests."""
    # First connect without database to create it if needed
    config_no_db = {k: v for k, v in TEST_DB_CONFIG.items() if k != 'database'}

    try:
        conn = mysql.connector.connect(**config_no_db)
        cursor = conn.cursor()

        # Create test database if it doesn't exist
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {TEST_DB_CONFIG['database']}")
        cursor.close()
        conn.close()

        # Connect to test database
        conn = mysql.connector.connect(**TEST_DB_CONFIG)
        yield conn

        conn.close()
    except mysql.connector.Error as e:
        pytest.skip(f"Database not available for integration tests: {e}")


@pytest.fixture(scope='function')
def clean_db(db_connection):
    """Clean the database before each test."""
    cursor = db_connection.cursor()

    # Disable foreign key checks for cleanup
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    # Get all tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    # Truncate all tables
    for (table,) in tables:
        cursor.execute(f"TRUNCATE TABLE {table}")

    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    db_connection.commit()
    cursor.close()

    yield db_connection


@pytest.fixture
def integration_client(clean_db):
    """Create a Flask test client with real database connection."""
    # Set environment variables to point to test database
    os.environ['DB_HOST'] = TEST_DB_CONFIG['host']
    os.environ['DB_PORT'] = str(TEST_DB_CONFIG['port'])
    os.environ['DB_USER'] = TEST_DB_CONFIG['user']
    os.environ['DB_PASSWORD'] = TEST_DB_CONFIG['password']
    os.environ['DB_NAME'] = TEST_DB_CONFIG['database']

    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_person_data():
    """Sample person data for testing."""
    return {
        'personal_id': 'TEST001',
        'name': 'Test Person',
        'gender': 'Male',
        'date_of_birth': '1990-01-01',
        'entry_date': '2024-01-01',
    }


@pytest.fixture
def sample_school_data():
    """Sample school data for testing."""
    return {
        'department': 'TEST',
        'school_name': 'Test School',
        'faculty': 'Test Faculty',
        'hq_building': 'Block T',
    }


@pytest.fixture
def sample_location_data():
    """Sample location data for testing."""
    return {
        'room': 'T101',
        'floor': '1',
        'building': 'Block T',
        'type': 'Classroom',
        'campus': 'Main',
    }
