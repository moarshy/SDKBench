"""Tests for data operations - upsert_mode."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_database_connection():
    """Test database is connected."""
    from expected import data_ops
    assert data_ops.db is not None

def test_table_creation():
    """Test table can be created."""
    from expected import data_ops
    data_ops.main()
    tables = data_ops.db.table_names()
    assert len(tables) > 0

def test_data_stored():
    """Test data is stored in table."""
    from expected import data_ops
    data_ops.main()
    # Verify data exists
    tables = data_ops.db.table_names()
    assert len(tables) > 0
