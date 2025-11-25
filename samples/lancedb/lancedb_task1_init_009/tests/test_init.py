"""Tests for LanceDB initialization."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_flask_app_exists():
    """Test Flask app is created."""
    from expected import app
    assert hasattr(app, "app")
    assert app.app is not None

def test_get_db_function():
    """Test get_db function exists."""
    from expected import app
    assert hasattr(app, "get_db")
    assert callable(app.get_db)
