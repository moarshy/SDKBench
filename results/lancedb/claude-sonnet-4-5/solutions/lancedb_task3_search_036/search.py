# filepath: search.py
"""Filtered search with projections."""

import lancedb
import numpy as np
import pandas as pd
import pyarrow as pa


def search_with_select(query_vector, k: int = 10):
    """Search with column selection.

    Args:
        query_vector: Query vector for similarity search
        k: Number of results to return

    Returns:
        pandas.DataFrame with only selected columns
    """
    try:
        # Connect to the database
        db = lancedb.connect("./lancedb_data")
        
        # Open the table
        table = db.open_table("documents")
        
        # Perform vector search with:
        # 1. Vector similarity search
        # 2. Column selection using .select()
        # 3. Filtering using .where()
        # 4. Cosine distance metric
        results = (
            table.search(query_vector)
            .metric("cosine")
            .where("category IS NOT NULL")  # Filter out null categories
            .select(["text", "category"])  # Only return these columns
            .limit(k)
            .to_pandas()
        )
        
        return results
        
    except Exception as e:
        print(f"Error during search: {e}")
        raise


def create_sample_data():
    """Create sample data for demonstration."""
    try:
        # Connect to database
        db = lancedb.connect("./lancedb_data")
        
        # Create sample data with vectors, text, and categories
        data = [
            {
                "vector": np.random.randn(128).tolist(),
                "text": "Machine learning is a subset of artificial intelligence",
                "category": "AI",
                "id": 1
            },
            {
                "vector": np.random.randn(128).tolist(),
                "text": "Deep learning uses neural networks with multiple layers",
                "category": "AI",
                "id": 2
            },
            {
                "vector": np.random.randn(128).tolist(),
                "text": "Python is a popular programming language",
                "category": "Programming",
                "id": 3
            },
            {
                "vector": np.random.randn(128).tolist(),
                "text": "Data science involves statistics and machine learning",
                "category": "Data Science",
                "id": 4
            },
            {
                "vector": np.random.randn(128).tolist(),
                "text": "Natural language processing enables computers to understand text",
                "category": "AI",
                "id": 5
            },
            {
                "vector": np.random.randn(128).tolist(),
                "text": "JavaScript is used for web development",
                "category": "Programming",
                "id": 6
            },
            {
                "vector": np.random.randn(128).tolist(),
                "text": "Computer vision allows machines to interpret images",
                "category": "AI",
                "id": 7
            },
            {
                "vector": np.random.randn(128).tolist(),
                "text": "SQL is used for database management",
                "category": "Database",
                "id": 8
            },
        ]
        
        # Define schema
        schema = pa.schema([
            pa.field("vector", pa.list_(pa.float32(), 128)),
            pa.field("text", pa.string()),
            pa.field("category", pa.string()),
            pa.field("id", pa.int64())
        ])
        
        # Create table with schema
        table = db.create_table(
            "documents",
            data=data,
            schema=schema,
            mode="overwrite"
        )
        
        print(f"Created table with {len(data)} documents")
        return table
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        raise


def advanced_filtered_search(query_vector, category_filter: str = None, k: int = 5):
    """Advanced search with category filtering.
    
    Args:
        query_vector: Query vector for similarity search
        category_filter: Optional category to filter by
        k: Number of results to return
        
    Returns:
        pandas.DataFrame with filtered results
    """
    try:
        db = lancedb.connect("./lancedb_data")
        table = db.open_table("documents")
        
        # Build search query
        search_query = table.search(query_vector).metric("cosine")
        
        # Add category filter if provided
        if category_filter:
            search_query = search_query.where(f"category = '{category_filter}'")
        
        # Execute search with projections
        results = (
            search_query
            .select(["text", "category"])
            .limit(k)
            .to_pandas()
        )
        
        return results
        
    except Exception as e:
        print(f"Error during advanced search: {e}")
        raise


def main():
    """Main function to demonstrate filtered search with projections."""
    try:
        # Create sample data
        print("Creating sample data...")
        create_sample_data()
        print()
        
        # Generate a random query vector (128 dimensions)
        query_vector = np.random.randn(128).tolist()
        
        # Example 1: Basic search with projections
        print("=" * 60)
        print("Example 1: Basic search with column selection")
        print("=" * 60)
        results = search_with_select(query_vector, k=5)
        print(f"\nFound {len(results)} results:")
        print(results.to_string(index=False))
        print()
        
        # Example 2: Search filtered by category
        print("=" * 60)
        print("Example 2: Search filtered by 'AI' category")
        print("=" * 60)
        ai_results = advanced_filtered_search(
            query_vector, 
            category_filter="AI", 
            k=3
        )
        print(f"\nFound {len(ai_results)} AI-related results:")
        print(ai_results.to_string(index=False))
        print()
        
        # Example 3: Search filtered by 'Programming' category
        print("=" * 60)
        print("Example 3: Search filtered by 'Programming' category")
        print("=" * 60)
        prog_results = advanced_filtered_search(
            query_vector,
            category_filter="Programming",
            k=3
        )
        print(f"\nFound {len(prog_results)} Programming-related results:")
        print(prog_results.to_string(index=False))
        print()
        
        # Example 4: Demonstrate different metrics
        print("=" * 60)
        print("Example 4: Search with L2 distance metric")
        print("=" * 60)
        db = lancedb.connect("./lancedb_data")
        table = db.open_table("documents")
        l2_results = (
            table.search(query_vector)
            .metric("l2")
            .select(["text", "category"])
            .limit(3)
            .to_pandas()
        )
        print(f"\nFound {len(l2_results)} results using L2 distance:")
        print(l2_results.to_string(index=False))
        print()
        
        print("=" * 60)
        print("Filtered search complete")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    main()