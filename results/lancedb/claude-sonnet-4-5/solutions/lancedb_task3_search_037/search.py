# filepath: search.py
"""Hybrid search with Full-Text Search."""

import lancedb
import pandas as pd
import numpy as np
from typing import Optional


def setup_fts_index(table):
    """Create FTS index on table.
    
    Creates a full-text search index using BM25 algorithm
    on the 'text' column for efficient text-based retrieval.
    
    Args:
        table: LanceDB table instance
    """
    try:
        # Create FTS index on the text column
        # This enables BM25 text search capabilities
        table.create_fts_index("text")
        print("FTS index created successfully on 'text' column")
    except Exception as e:
        print(f"Error creating FTS index: {e}")
        # Index might already exist, which is fine
        pass


def hybrid_search(table, query_text: str, query_vector, k: int = 10):
    """Perform hybrid vector + text search.
    
    Combines vector similarity search with BM25 full-text search
    to leverage both semantic and keyword-based matching.
    
    Args:
        table: LanceDB table instance
        query_text: Text query for BM25 search
        query_vector: Vector embedding for similarity search
        k: Number of results to return
        
    Returns:
        pandas.DataFrame: Search results with combined scores
    """
    try:
        # Perform hybrid search combining vector similarity and text search
        # Results are ranked using a combination of:
        # - Vector similarity (cosine/L2 distance)
        # - BM25 text relevance score
        results = (
            table.search(query_type="hybrid")
            .vector(query_vector)
            .text(query_text)
            .limit(k)
            .to_pandas()
        )
        
        return results
    except Exception as e:
        print(f"Error performing hybrid search: {e}")
        return pd.DataFrame()


def vector_only_search(table, query_vector, k: int = 10, filter_expr: Optional[str] = None):
    """Perform vector-only similarity search.
    
    Args:
        table: LanceDB table instance
        query_vector: Vector embedding for similarity search
        k: Number of results to return
        filter_expr: Optional SQL-like filter expression
        
    Returns:
        pandas.DataFrame: Search results
    """
    try:
        search = table.search(query_vector).limit(k)
        
        if filter_expr:
            search = search.where(filter_expr)
        
        results = search.to_pandas()
        return results
    except Exception as e:
        print(f"Error performing vector search: {e}")
        return pd.DataFrame()


def text_only_search(table, query_text: str, k: int = 10):
    """Perform text-only BM25 search.
    
    Args:
        table: LanceDB table instance
        query_text: Text query for BM25 search
        k: Number of results to return
        
    Returns:
        pandas.DataFrame: Search results
    """
    try:
        results = (
            table.search(query_text, query_type="fts")
            .limit(k)
            .to_pandas()
        )
        return results
    except Exception as e:
        print(f"Error performing text search: {e}")
        return pd.DataFrame()


def main():
    """Main function demonstrating hybrid search setup and usage."""
    
    # Connect to LanceDB
    db = lancedb.connect("./lancedb_data")
    
    # Create sample data with text and vector embeddings
    print("Creating sample data...")
    sample_data = pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "text": [
            "LanceDB is a vector database for AI applications",
            "Hybrid search combines vector and text search",
            "Full-text search uses BM25 algorithm",
            "Vector embeddings capture semantic meaning",
            "Database systems store and retrieve data efficiently"
        ],
        "vector": [
            np.random.rand(128).tolist(),
            np.random.rand(128).tolist(),
            np.random.rand(128).tolist(),
            np.random.rand(128).tolist(),
            np.random.rand(128).tolist()
        ],
        "category": ["database", "search", "search", "ml", "database"]
    })
    
    # Create or recreate table
    try:
        db.drop_table("documents")
    except:
        pass
    
    table = db.create_table("documents", sample_data)
    print(f"Created table with {len(sample_data)} documents")
    
    # Setup FTS index
    print("\nSetting up FTS index...")
    setup_fts_index(table)
    
    # Prepare query
    query_text = "vector search database"
    query_vector = np.random.rand(128).tolist()
    
    # Perform hybrid search
    print(f"\nPerforming hybrid search for: '{query_text}'")
    hybrid_results = hybrid_search(table, query_text, query_vector, k=3)
    
    if not hybrid_results.empty:
        print("\nHybrid Search Results:")
        print("-" * 80)
        for idx, row in hybrid_results.iterrows():
            print(f"ID: {row['id']}")
            print(f"Text: {row['text']}")
            print(f"Category: {row['category']}")
            if '_score' in row:
                print(f"Score: {row['_score']:.4f}")
            print("-" * 80)
    
    # Demonstrate vector-only search
    print("\nPerforming vector-only search...")
    vector_results = vector_only_search(table, query_vector, k=3)
    print(f"Found {len(vector_results)} results")
    
    # Demonstrate text-only search
    print("\nPerforming text-only search...")
    text_results = text_only_search(table, query_text, k=3)
    print(f"Found {len(text_results)} results")
    
    # Demonstrate filtered search
    print("\nPerforming filtered vector search (category='search')...")
    filtered_results = vector_only_search(
        table, 
        query_vector, 
        k=3, 
        filter_expr="category = 'search'"
    )
    print(f"Found {len(filtered_results)} results")
    
    print("\nHybrid search complete")


if __name__ == "__main__":
    main()