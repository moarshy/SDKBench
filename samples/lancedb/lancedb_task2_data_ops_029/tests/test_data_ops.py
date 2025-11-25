"""Tests for data operations."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_table_creation():
    """Test that table is created."""
    from expected import data_ops

    # Run main to create table
    data_ops.main()

    # Check table exists
    tables = data_ops.db.table_names()
    assert "items" in tables

def test_schema_definition():
    """Test Document schema is defined."""
    from expected.data_ops import Document

    # Check schema has required fields
    assert hasattr(Document, "__fields__")
