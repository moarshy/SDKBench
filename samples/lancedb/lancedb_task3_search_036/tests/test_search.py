"""Tests for search - filtered_search."""

import pytest
import os
import sys
# Add parent directory to path for imports (expected/ and conftest.py are siblings of tests/)
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent_dir)

# Import shared test utilities (conftest.py is at same level as expected/)
from conftest import get_db_connection, has_db_connection

def test_database_connection():
    """Test database is connected."""
    from expected import search
    assert has_db_connection(search) and get_db_connection(search) is not None

def test_search_function_exists():
    """Test search function exists."""
    from expected import search
    # Check for common search function names
    has_search = (
        hasattr(search, 'search') or
        hasattr(search, 'search_similar') or
        hasattr(search, 'hybrid_search') or
        hasattr(search, 'search_with_rrf') or
        hasattr(search, 'hyde_search')
    )
    assert has_search
