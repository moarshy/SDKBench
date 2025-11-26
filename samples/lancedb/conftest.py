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
    - Running main() to initialize module state

    Args:
        module: The imported module to extract connection from

    Returns:
        Database connection or None if not found
    """
    # Module-level variable
    if hasattr(module, 'db') and module.db is not None:
        return module.db

    # Factory functions - common patterns for getting/creating database connections
    factory_funcs = [
        'get_database', 'get_db', 'get_connection', 'connect', 'get_cloud_database',
        'create_test_db', 'create_db', 'create_database', 'init_db', 'initialize_db',
        'setup_db', 'setup_database', 'make_db', 'build_db',
    ]
    for func_name in factory_funcs:
        if hasattr(module, func_name):
            func = getattr(module, func_name)
            if callable(func):
                try:
                    return func()
                except Exception:
                    continue

    # Last resort: try running main() which might initialize module-level db
    if hasattr(module, 'main') and callable(module.main):
        try:
            module.main()
            # Check if db was set after main() ran
            if hasattr(module, 'db') and module.db is not None:
                return module.db
        except Exception:
            pass

    return None


def has_db_connection(module):
    """Check if module has any way to get a database connection.

    This actually tries to get a connection to verify it works.

    Args:
        module: The imported module to check

    Returns:
        True if module has database connection capability
    """
    # Actually try to get the connection - this is more reliable than just checking attributes
    return get_db_connection(module) is not None


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


def get_embedding_model(module):
    """Get embedding model from module using various patterns.

    Supports:
    - module.model (module-level variable)
    - module.embedding_model (alternative name)
    - module.get_model() (factory function)
    - module.get_embedding_model() (full name factory)
    - module.create_model() (creator pattern)
    - Running main() to initialize module state

    Args:
        module: The imported module to extract model from

    Returns:
        Embedding model or None if not found
    """
    # Module-level variables
    for attr_name in ['model', 'embedding_model', 'embed_model', 'embedder']:
        if hasattr(module, attr_name):
            model = getattr(module, attr_name)
            if model is not None and hasattr(model, 'ndims'):
                return model

    # Factory functions
    factory_funcs = [
        'get_model', 'get_embedding_model', 'create_model', 'create_embedding_model',
        'get_embedder', 'create_embedder', 'init_model', 'initialize_model',
    ]
    for func_name in factory_funcs:
        if hasattr(module, func_name):
            func = getattr(module, func_name)
            if callable(func):
                try:
                    model = func()
                    if model is not None and hasattr(model, 'ndims'):
                        return model
                except Exception:
                    continue

    # Last resort: try running main() which might initialize module-level model
    if hasattr(module, 'main') and callable(module.main):
        try:
            module.main()
            # Check if model was set after main() ran
            for attr_name in ['model', 'embedding_model', 'embed_model', 'embedder']:
                if hasattr(module, attr_name):
                    model = getattr(module, attr_name)
                    if model is not None and hasattr(model, 'ndims'):
                        return model
        except Exception:
            pass

    return None


def has_embedding_model(module):
    """Check if module has any way to get an embedding model.

    Args:
        module: The imported module to check

    Returns:
        True if module has embedding model capability
    """
    return get_embedding_model(module) is not None


def get_document_class(module):
    """Get document/schema class from module using various patterns.

    Supports:
    - module.Document (standard name)
    - module.DocSchema, module.Schema (alternative names)
    - module.get_document_class() (factory)
    - Any class with 'text' and 'vector' fields

    Args:
        module: The imported module to extract document class from

    Returns:
        Document class or None if not found
    """
    # Standard names for document classes
    class_names = ['Document', 'DocSchema', 'Schema', 'DocumentSchema',
                   'VectorDocument', 'EmbeddingDocument', 'Record']

    for class_name in class_names:
        if hasattr(module, class_name):
            cls = getattr(module, class_name)
            if cls is not None and hasattr(cls, '__fields__'):
                fields = cls.__fields__
                if 'text' in fields and 'vector' in fields:
                    return cls

    # Factory functions
    factory_funcs = [
        'get_document_class', 'create_document_class', 'get_schema',
        'create_schema', 'make_document_class',
    ]
    for func_name in factory_funcs:
        if hasattr(module, func_name):
            func = getattr(module, func_name)
            if callable(func):
                try:
                    # Some factories need the model as argument
                    model = get_embedding_model(module)
                    if model:
                        cls = func(model)
                    else:
                        cls = func()
                    if cls is not None and hasattr(cls, '__fields__'):
                        return cls
                except Exception:
                    continue

    # Last resort: try running main() and scan for any LanceModel subclass
    if hasattr(module, 'main') and callable(module.main):
        try:
            module.main()
            for class_name in class_names:
                if hasattr(module, class_name):
                    cls = getattr(module, class_name)
                    if cls is not None and hasattr(cls, '__fields__'):
                        return cls
        except Exception:
            pass

    return None


def has_document_class(module):
    """Check if module has a document/schema class.

    Args:
        module: The imported module to check

    Returns:
        True if module has a document class with text and vector fields
    """
    return get_document_class(module) is not None


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
