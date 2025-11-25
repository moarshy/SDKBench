"""Tests for LanceDB initialization."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_lancedb_import():
    """Test that lancedb is imported."""
    from expected import app
    import lancedb
    assert lancedb is not None

def test_database_connection():
    """Test that database connection is established."""
    from expected import app
    assert app.db is not None
    assert hasattr(app.db, "table_names")

def test_main_runs():
    """Test main function runs without errors."""
    from expected import app
    app.main()
