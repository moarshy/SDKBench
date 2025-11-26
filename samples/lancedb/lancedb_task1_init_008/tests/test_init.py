"""Tests for LanceDB initialization."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conftest import get_db_connection, has_db_connection


def test_fastapi_app_exists():
    """Test FastAPI app is created."""
    from expected import app
    assert hasattr(app, "app") or hasattr(app, "fastapi_app") or hasattr(app, "api"), \
        "Module should have a FastAPI app"

def test_lifespan_defined():
    """Test lifespan context manager is defined."""
    from expected import app
    # Accept various lifespan patterns
    has_lifespan = (
        hasattr(app, "lifespan") or
        hasattr(app, "app_lifespan") or
        hasattr(app, "startup") or
        hasattr(app, "on_startup")
    )
    assert has_lifespan, "Module should have lifespan/startup handling"

def test_get_db_dependency():
    """Test get_db dependency is defined."""
    from expected import app
    # Should have some way to get database
    assert has_db_connection(app), "Module should have database connection capability"
