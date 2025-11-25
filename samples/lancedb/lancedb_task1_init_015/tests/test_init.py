"""Tests for LanceDB initialization."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_registry_import():
    """Test EmbeddingFunctionRegistry is imported."""
    from lancedb.embeddings import EmbeddingFunctionRegistry
    registry = EmbeddingFunctionRegistry.get_instance()
    assert registry is not None

def test_model_created():
    """Test embedding model is created."""
    from expected import app
    assert hasattr(app, "model")
    assert hasattr(app.model, "ndims")

def test_document_schema():
    """Test Document schema with SourceField/VectorField."""
    from expected import app
    assert hasattr(app, "Document")
    # Check schema has expected fields
    fields = app.Document.__fields__
    assert "text" in fields
    assert "vector" in fields
