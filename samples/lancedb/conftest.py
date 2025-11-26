"""Shared test utilities for LanceDB samples.

This module provides helper functions that allow tests to work with multiple
valid implementation patterns (module-level variables vs factory functions).
"""

import pytest
import os


def get_db_connection(module):
    """Get database connection from module using various patterns.

    Supports:
    - module.db (module-level variable)
    - module.get_database() (factory function)
    - module.get_db() (short factory)
    - module.connect() (direct connect)
    - module.get_cloud_database() (cloud variant)

    Args:
        module: The imported module to extract connection from

    Returns:
        Database connection or None if not found
    """
    # Module-level variable
    if hasattr(module, 'db') and module.db is not None:
        return module.db

    # Factory functions
    for func_name in ['get_database', 'get_db', 'get_connection', 'connect', 'get_cloud_database']:
        if hasattr(module, func_name):
            func = getattr(module, func_name)
            if callable(func):
                try:
                    return func()
                except Exception:
                    continue

    return None


def has_db_connection(module):
    """Check if module has any way to get a database connection.

    Args:
        module: The imported module to check

    Returns:
        True if module has database connection capability
    """
    # Check for module-level variable
    if hasattr(module, 'db'):
        return True

    # Check for factory functions
    connection_funcs = ['get_database', 'get_db', 'get_connection', 'connect', 'get_cloud_database']
    return any(hasattr(module, name) and callable(getattr(module, name)) for name in connection_funcs)


def has_search_capability(module):
    """Check if module has any search function.

    Args:
        module: The imported module to check

    Returns:
        True if module has search capability
    """
    search_names = ['search', 'search_similar', 'vector_search', 'hybrid_search', 'full_text_search']
    return any(hasattr(module, name) and callable(getattr(module, name)) for name in search_names)


def has_ingest_capability(module):
    """Check if module has any ingest function.

    Args:
        module: The imported module to check

    Returns:
        True if module has ingest capability
    """
    ingest_names = ['ingest', 'ingest_documents', 'add_documents', 'insert', 'add']
    return any(hasattr(module, name) and callable(getattr(module, name)) for name in ingest_names)


def get_table(module, table_name=None):
    """Get a table from the database connection.

    Args:
        module: The imported module
        table_name: Optional table name (uses first table if not specified)

    Returns:
        Table object or None
    """
    db = get_db_connection(module)
    if db is None:
        return None

    try:
        tables = db.table_names()
        if not tables:
            return None

        name = table_name or tables[0]
        return db.open_table(name)
    except Exception:
        return None


@pytest.fixture
def skip_without_credentials():
    """Skip test if required AWS credentials are missing."""
    if not os.getenv('AWS_ACCESS_KEY_ID'):
        pytest.skip("AWS credentials not configured")


@pytest.fixture
def skip_without_openai():
    """Skip test if OpenAI API key is missing."""
    if not os.getenv('OPENAI_API_KEY'):
        pytest.skip("OpenAI API key not configured")
