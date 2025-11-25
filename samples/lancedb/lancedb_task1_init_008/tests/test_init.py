"""Tests for LanceDB initialization."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_fastapi_app_exists():
    """Test FastAPI app is created."""
    from expected import app
    assert hasattr(app, "app")
    assert app.app is not None

def test_lifespan_defined():
    """Test lifespan context manager is defined."""
    from expected import app
    assert hasattr(app, "lifespan")

def test_get_db_dependency():
    """Test get_db dependency is defined."""
    from expected import app
    assert hasattr(app, "get_db")
    assert callable(app.get_db)
