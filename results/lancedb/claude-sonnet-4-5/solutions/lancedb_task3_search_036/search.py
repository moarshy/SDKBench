# filepath: search.py
"""Filtered search with projections."""

import lancedb
import numpy as np
import pandas as pd


def search_with_select(query_vector, k: int = 10):
    """Search with column selection.

    Args:
        query_vector: Query vector for similarity search
        k: Number of results to return

    Returns:
        pandas.DataFrame: Search results with selected columns
    """
    try:
        # Connect to the database
        db = lancedb.connect("./my_lancedb")
        
        # Open the table (assuming it exists)
        table = db.open_table("documents")
        
        # Perform vector search with:
        # - Column selection using .select()
        # - Filtering using .where()
        # - Cosine distance metric
        # - Limit results to k
        results = (
            table.search(query_vector)
            .metric("cosine")
            .where("category IS NOT NULL")  # Filter condition
            .select(["text", "category"])    # Select specific columns
            .limit(k)
            .to_pandas()
        )
        
        return results
        
    except Exception as e:
        print(f"Error during search: {e}")
        return pd.DataFrame()


def create_sample_data():
    """Create sample data for demonstration."""
    # Sample data with vectors, text, and categories
    data = [
        {
            "vector": np.random.randn(128).tolist(),
            "text": "Machine learning is a subset of artificial intelligence",
            "category": "AI"
        },
        {
            "vector": np.random.randn(128).tolist(),
            "text": "Deep learning uses neural networks with multiple layers",
            "category": "AI"
        },
        {
            "vector": np.random.randn(128).tolist(),
            "text": "Python is a popular programming language",
            "category": "Programming"
        },
        {
            "vector": np.random.randn(128).tolist(),
            "text": "Vector databases enable semantic search",
            "category": "Database"
        },
        {
            "vector": np.random.randn(128).tolist(),
            "text": "Natural language processing helps computers understand text",
            "category": "AI"
        },
    ]
    return data


def main():
    """Main function to demonstrate filtered search with projections."""
    try:
        # Connect to LanceDB
        db = lancedb.connect("./my_lancedb")
        
        # Create sample data
        data = create_sample_data()
        
        # Create or replace the table
        table = db.create_table("documents", data=data, mode="overwrite")
        print(f"Created table with {len(data)} documents")
        
        # Generate a random query vector (same dimension as data)
        query_vector = np.random.randn(128).tolist()
        
        # Perform search with projections
        print("\n=== Search with column selection and filtering ===")
        results = search_with_select(query_vector, k=3)
        
        if not results.empty:
            print(f"\nFound {len(results)} results:")
            print(results.to_string(index=False))
            
            # Verify only selected columns are returned
            print(f"\nColumns in results: {results.columns.tolist()}")
        else:
            print("No results found")
        
        # Example: Search with specific category filter
        print("\n=== Search filtered by category ===")
        ai_results = (
            table.search(query_vector)
            .metric("cosine")
            .where("category = 'AI'")
            .select(["text", "category"])
            .limit(5)
            .to_pandas()
        )
        
        if not ai_results.empty:
            print(f"\nFound {len(ai_results)} AI-related results:")
            print(ai_results.to_string(index=False))
        
        print("\nFiltered search complete")
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    main()