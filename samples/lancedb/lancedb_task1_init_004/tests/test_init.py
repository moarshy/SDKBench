"""Tests for LanceDB initialization."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conftest import get_embedding_model, has_embedding_model, get_document_class, has_document_class


def test_registry_import():
    """Test EmbeddingFunctionRegistry is imported."""
    from lancedb.embeddings import EmbeddingFunctionRegistry
    registry = EmbeddingFunctionRegistry.get_instance()
    assert registry is not None

def test_model_created():
    """Test embedding model is created."""
    from expected import app
    assert has_embedding_model(app), "Module should have an embedding model"
    model = get_embedding_model(app)
    assert model is not None
    assert hasattr(model, "ndims"), "Model should have ndims attribute"

def test_document_schema():
    """Test Document schema with SourceField/VectorField."""
    from expected import app
    assert has_document_class(app), "Module should have a Document class"
    doc_class = get_document_class(app)
    assert doc_class is not None
    # Check schema has expected fields
    fields = doc_class.__fields__
    assert "text" in fields, "Document should have 'text' field"
    assert "vector" in fields, "Document should have 'vector' field"
