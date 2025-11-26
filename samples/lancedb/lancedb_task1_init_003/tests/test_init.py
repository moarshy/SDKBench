"""Tests for LanceDB initialization."""

import pytest
import os
import sys
# Add parent directory to path for imports (expected/ and conftest.py are siblings of tests/)
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent_dir)

# Import shared test utilities (conftest.py is at same level as expected/)
from conftest import get_db_connection, has_db_connection


def test_streamlit_cache_decorator():
    """Test that @st.cache_resource is used."""
    from expected import app
    # Check get_database has cache decorator
    assert hasattr(app.get_database, "__wrapped__") or "cache" in str(app.get_database)

def test_database_connection():
    """Test database is connected."""
    from expected import app
    assert has_db_connection(app) and get_db_connection(app) is not None
