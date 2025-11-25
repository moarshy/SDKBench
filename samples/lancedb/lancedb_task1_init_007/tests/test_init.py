"""Tests for LanceDB initialization."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_lancedb_connection():
    """Test that LanceDB connection is established."""
    from expected import app
    assert hasattr(app, "db") or hasattr(app, "get_database")

def test_main_function():
    """Test main function runs without errors."""
    from expected import app
    app.main()
