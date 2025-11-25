"""Tests for RAG pipeline."""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_document_ingestion():
    """Test document ingestion."""
    from expected import pipeline

    docs = [{"text": "Test document"}]
    count = pipeline.ingest_documents(docs)
    assert count == 1

def test_search_returns_results():
    """Test search functionality."""
    from expected import pipeline

    # Ingest first
    docs = [{"text": "LanceDB is great"}]
    pipeline.ingest_documents(docs)

    # Search
    results = pipeline.search("LanceDB", k=1)
    assert len(results) > 0

def test_pipeline_end_to_end():
    """Test complete pipeline."""
    from expected import pipeline

    # Ingest
    docs = [{"text": "Test content for pipeline"}]
    pipeline.ingest_documents(docs)

    # Run pipeline
    response = pipeline.run_pipeline("test query")
    assert isinstance(response, str)
    assert len(response) > 0
