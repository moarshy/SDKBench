"""Tests for schema migration: Upgrade embedding model."""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_backup_returns_dataframe():
    """Test backup function."""
    from expected import migration
    import pandas as pd

    backup = migration.backup_data("nonexistent_table")
    assert isinstance(backup, pd.DataFrame)

def test_migrate_data_transforms():
    """Test data transformation."""
    from expected import migration
    import pandas as pd

    # Create test data
    test_data = pd.DataFrame({
        "text": ["test"],
        "vector": [[0.1] * 384]
    })

    result = migration.migrate_data(test_data)
    assert len(result) == 1

def test_full_migration():
    """Test complete migration process."""
    from expected import migration

    success = migration.run_migration()
    assert success is True
