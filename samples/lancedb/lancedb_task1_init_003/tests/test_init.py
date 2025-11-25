"""Tests for LanceDB initialization."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_streamlit_cache_decorator():
    """Test that @st.cache_resource is used."""
    from expected import app
    # Check get_database has cache decorator
    assert hasattr(app.get_database, "__wrapped__") or "cache" in str(app.get_database)

def test_database_connection():
    """Test database is connected."""
    from expected import app
    assert app.db is not None
