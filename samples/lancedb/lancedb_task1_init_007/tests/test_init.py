"""Tests for LanceDB initialization with S3 cloud storage."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conftest import get_db_connection, has_db_connection


# Skip tests if AWS credentials are not available
requires_aws = pytest.mark.skipif(
    not os.environ.get('AWS_ACCESS_KEY_ID'),
    reason="AWS credentials not configured"
)


def test_has_cloud_database_function():
    """Test that module has cloud database capability."""
    from expected import app
    # Check for get_cloud_database or get_database or db attribute
    has_cloud_func = (
        hasattr(app, 'get_cloud_database') or
        hasattr(app, 'get_database') or
        hasattr(app, 'db') or
        hasattr(app, 'get_db')
    )
    assert has_cloud_func, "Module should have cloud database function or db attribute"


@requires_aws
def test_lancedb_connection():
    """Test that LanceDB S3 connection is established."""
    from expected import app
    assert has_db_connection(app), "Module should have a database connection"
    db = get_db_connection(app)
    assert db is not None
    assert hasattr(db, "table_names")


@requires_aws
def test_main_function():
    """Test main function runs without errors."""
    from expected import app
    app.main()
