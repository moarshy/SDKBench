"""Tests for LanceDB initialization."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conftest import get_db_connection, has_db_connection


def test_flask_app_exists():
    """Test Flask app is created."""
    from expected import app
    assert hasattr(app, "app") or hasattr(app, "flask_app") or hasattr(app, "application"), \
        "Module should have a Flask app"

def test_get_db_function():
    """Test get_db function or db connection exists."""
    from expected import app
    # Should have some way to get database
    assert has_db_connection(app), "Module should have database connection capability"
