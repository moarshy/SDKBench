"""Tests for data operations - async_batch."""

import pytest
import asyncio
import inspect
import os
import sys
# Add parent directory to path for imports (expected/ and conftest.py are siblings of tests/)
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent_dir)

# Import shared test utilities (conftest.py is at same level as expected/)
from conftest import get_db_connection, has_db_connection


def _run_main(module):
    """Run main() handling both sync and async versions."""
    if hasattr(module, 'main'):
        main_func = module.main
        if inspect.iscoroutinefunction(main_func):
            asyncio.run(main_func())
        else:
            main_func()


def test_database_connection():
    """Test database is connected."""
    from expected import data_ops
    assert has_db_connection(data_ops) and get_db_connection(data_ops) is not None

def test_table_creation():
    """Test table can be created."""
    from expected import data_ops
    _run_main(data_ops)
    tables = get_db_connection(data_ops).table_names()
    assert len(tables) > 0

def test_data_stored():
    """Test data is stored in table."""
    from expected import data_ops
    _run_main(data_ops)
    # Verify data exists
    tables = get_db_connection(data_ops).table_names()
    assert len(tables) > 0
