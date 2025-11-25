"""Tests for LanceDB initialization."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_get_tenant_db():
    """Test tenant database creation."""
    from expected import app
    assert hasattr(app, "get_tenant_db")
    assert callable(app.get_tenant_db)

def test_tenant_isolation():
    """Test tenants are isolated."""
    from expected import app
    db_a = app.get_tenant_db("test_a")
    db_b = app.get_tenant_db("test_b")
    # Different paths means different databases
    assert db_a is not db_b
