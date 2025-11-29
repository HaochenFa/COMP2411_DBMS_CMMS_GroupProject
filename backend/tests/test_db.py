"""
Unit tests for backend/db.py module.
Tests database connection and initialization functions.
"""
import pytest
from unittest.mock import patch, MagicMock, mock_open
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestGetDbConnection:
    """Tests for get_db_connection function."""

    @patch('db.mysql.connector.connect')
    def test_successful_connection(self, mock_connect):
        """Test successful database connection."""
        from db import get_db_connection
        
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        result = get_db_connection()
        
        assert result == mock_conn
        mock_connect.assert_called_once()

    @patch('db.mysql.connector.connect')
    def test_connection_failure(self, mock_connect):
        """Test database connection failure returns None."""
        from db import get_db_connection
        from mysql.connector import Error
        
        mock_connect.side_effect = Error("Connection failed")
        
        result = get_db_connection()
        
        assert result is None

    @patch.dict('os.environ', {
        'DB_HOST': 'testhost',
        'DB_USER': 'testuser',
        'DB_PASSWORD': 'testpass',
        'DB_NAME': 'testdb'
    })
    @patch('db.mysql.connector.connect')
    def test_uses_environment_variables(self, mock_connect):
        """Test that connection uses environment variables."""
        from db import get_db_connection
        
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        get_db_connection()
        
        mock_connect.assert_called_once_with(
            host='testhost',
            user='testuser',
            password='testpass',
            database='testdb'
        )


class TestIsDbInitialized:
    """Tests for is_db_initialized function."""

    @patch('db.get_db_connection')
    def test_initialized_when_person_table_exists(self, mock_get_conn):
        """Test returns True when Person table exists."""
        from db import is_db_initialized
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ('Person',)
        mock_get_conn.return_value = mock_conn
        
        result = is_db_initialized()
        
        assert result is True
        mock_cursor.execute.assert_called_once_with("SHOW TABLES LIKE 'Person'")

    @patch('db.get_db_connection')
    def test_not_initialized_when_no_person_table(self, mock_get_conn):
        """Test returns False when Person table doesn't exist."""
        from db import is_db_initialized
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_get_conn.return_value = mock_conn
        
        result = is_db_initialized()
        
        assert result is False

    @patch('db.get_db_connection')
    def test_not_initialized_when_no_connection(self, mock_get_conn):
        """Test returns False when database connection fails."""
        from db import is_db_initialized
        
        mock_get_conn.return_value = None
        
        result = is_db_initialized()
        
        assert result is False


class TestInitDb:
    """Tests for init_db function."""

    @patch('db.get_db_connection')
    @patch('builtins.open', mock_open(read_data='CREATE TABLE test;'))
    def test_init_db_executes_schema(self, mock_get_conn):
        """Test init_db executes schema.sql statements."""
        from db import init_db
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        init_db()
        
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called_once()

    @patch('db.get_db_connection')
    @patch('db.mysql.connector.connect')
    def test_init_db_creates_database_if_not_exists(self, mock_connect, mock_get_conn):
        """Test init_db creates database when it doesn't exist."""
        from db import init_db
        
        # First call returns None (db doesn't exist), then returns connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.side_effect = [None, mock_conn]
        mock_connect.return_value = mock_conn
        
        with patch('builtins.open', mock_open(read_data='CREATE TABLE test;')):
            init_db()
        
        # Should try to create database
        assert mock_connect.called

