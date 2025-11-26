"""Tests for LanceDB initialization."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conftest import get_db_connection, has_db_connection


def test_lancedb_connection():
    """Test that LanceDB connection is established."""
    from expected import app
    assert has_db_connection(app), "Module should have a database connection"
    db = get_db_connection(app)
    assert db is not None
    assert hasattr(db, "table_names")

def test_main_function():
    """Test main function runs without errors."""
    from expected import app
    app.main()
