"""Tests for LanceDB initialization."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_lancedb_connection():
    """Test that LanceDB connection is established."""
    from expected import app

    # Check that db is initialized
    assert app.db is not None

    # Check connection method was called
    assert hasattr(app.db, 'table_names')

def test_main_function():
    """Test main function runs without errors."""
    from expected import app

    # Should run without raising exceptions
    app.main()
