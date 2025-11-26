"""Tests for LanceDB initialization."""

import pytest
import os
import sys

# Add parent directory to path for imports (expected/ and conftest.py are siblings of tests/)
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent_dir)

# Import shared test utilities (conftest.py is at same level as expected/)
from conftest import get_db_connection, has_db_connection


def test_lancedb_import():
    """Test that lancedb is imported."""
    from expected import app
    import lancedb
    assert lancedb is not None

def test_database_connection():
    """Test that database connection is established."""
    from expected import app
    assert has_db_connection(app) and get_db_connection(app) is not None
    assert hasattr(get_db_connection(app), "table_names")

def test_main_runs():
    """Test main function runs without errors."""
    from expected import app
    app.main()
