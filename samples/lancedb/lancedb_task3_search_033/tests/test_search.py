"""Tests for search - prefilter_where."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_database_connection():
    """Test database is connected."""
    from expected import search
    assert search.db is not None

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
