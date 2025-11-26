# filepath: search.py
"""Search with prefiltering (more efficient)."""

import lancedb
import numpy as np
import pandas as pd
from typing import Optional


def search_with_prefilter(query_vector, category: str, k: int = 10):
    """Search with prefiltering for efficiency.

    Args:
        query_vector: Query vector for similarity search
        category: Category to filter by
        k: Number of results to return

    Returns:
        pandas.DataFrame: Search results with prefiltering applied

    The prefilter=True parameter ensures filtering happens BEFORE
    computing vector distances, making the search much more efficient
    for large datasets.
    """
    try:
        # Connect to the database
        db = lancedb.connect("./lancedb_data")
        
        # Open the table (assumes it exists)
        table = db.open_table("products")
        
        # Perform search with prefiltering
        # The prefilter=True ensures filtering happens BEFORE distance computation
        results = (
            table.search(query_vector)
            .where(f"category = '{category}'", prefilter=True)
            .limit(k)
            .to_pandas()
        )
        
        return results
    
    except FileNotFoundError:
        print("Error: Database or table not found. Creating sample data...")
        return create_sample_data_and_search(query_vector, category, k)
    except Exception as e:
        print(f"Error during search: {e}")
        raise


def create_sample_data_and_search(query_vector, category: str, k: int = 10):
    """Create sample data and perform search (for demonstration)."""
    try:
        # Connect to database
        db = lancedb.connect("./lancedb_data")
        
        # Create sample data with vectors and categories
        data = []
        categories = ["electronics", "clothing", "books", "toys"]
        
        for i in range(100):
            data.append({
                "id": i,
                "vector": np.random.randn(128).tolist(),  # 128-dim vectors
                "category": categories[i % len(categories)],
                "name": f"Product {i}",
                "price": np.random.uniform(10, 1000),
                "rating": np.random.uniform(1, 5)
            })
        
        # Create table
        table = db.create_table("products", data, mode="overwrite")
        
        print(f"Created sample table with {len(data)} products")
        print(f"Categories: {categories}")
        
        # Perform search with prefiltering
        results = (
            table.search(query_vector)
            .where(f"category = '{category}'", prefilter=True)
            .limit(k)
            .to_pandas()
        )
        
        return results
    
    except Exception as e:
        print(f"Error creating sample data: {e}")
        raise


def search_with_multiple_filters(
    query_vector,
    category: str,
    min_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    k: int = 10
):
    """Search with multiple prefilters for more complex queries.
    
    Args:
        query_vector: Query vector for similarity search
        category: Category to filter by
        min_price: Minimum price filter (optional)
        min_rating: Minimum rating filter (optional)
        k: Number of results to return
    
    Returns:
        pandas.DataFrame: Filtered search results
    """
    try:
        db = lancedb.connect("./lancedb_data")
        table = db.open_table("products")
        
        # Build filter string with multiple conditions
        filters = [f"category = '{category}'"]
        
        if min_price is not None:
            filters.append(f"price >= {min_price}")
        
        if min_rating is not None:
            filters.append(f"rating >= {min_rating}")
        
        filter_string = " AND ".join(filters)
        
        # Perform search with combined prefilters
        results = (
            table.search(query_vector)
            .where(filter_string, prefilter=True)
            .limit(k)
            .to_pandas()
        )
        
        return results
    
    except Exception as e:
        print(f"Error during multi-filter search: {e}")
        raise


def compare_prefilter_vs_postfilter(query_vector, category: str, k: int = 10):
    """Demonstrate the difference between prefilter and postfilter.
    
    Prefilter (prefilter=True): Filters BEFORE computing distances - FASTER
    Postfilter (prefilter=False): Computes all distances, then filters - SLOWER
    """
    try:
        db = lancedb.connect("./lancedb_data")
        table = db.open_table("products")
        
        print("\n=== Prefilter Search (Efficient) ===")
        # Prefilter: Filter BEFORE distance computation
        prefilter_results = (
            table.search(query_vector)
            .where(f"category = '{category}'", prefilter=True)
            .limit(k)
            .to_pandas()
        )
        print(f"Found {len(prefilter_results)} results with prefilter")
        
        print("\n=== Postfilter Search (Less Efficient) ===")
        # Postfilter: Compute distances first, then filter
        postfilter_results = (
            table.search(query_vector)
            .where(f"category = '{category}'", prefilter=False)
            .limit(k)
            .to_pandas()
        )
        print(f"Found {len(postfilter_results)} results with postfilter")
        
        return prefilter_results, postfilter_results
    
    except Exception as e:
        print(f"Error during comparison: {e}")
        raise


def main():
    """Demonstrate prefiltered vector search."""
    print("=== LanceDB Prefiltered Vector Search Demo ===\n")
    
    # Create a random query vector (128 dimensions)
    query_vector = np.random.randn(128).tolist()
    
    # Example 1: Basic prefilter search
    print("1. Basic Prefilter Search")
    print("-" * 50)
    results = search_with_prefilter(query_vector, category="electronics", k=5)
    print(f"\nTop 5 electronics products:")
    print(results[["id", "name", "category", "price", "rating"]].to_string())
    
    # Example 2: Multiple filters
    print("\n\n2. Multiple Prefilters")
    print("-" * 50)
    multi_results = search_with_multiple_filters(
        query_vector,
        category="electronics",
        min_price=100,
        min_rating=3.5,
        k=5
    )
    print(f"\nElectronics with price >= 100 and rating >= 3.5:")
    print(multi_results[["id", "name", "category", "price", "rating"]].to_string())
    
    # Example 3: Compare prefilter vs postfilter
    print("\n\n3. Prefilter vs Postfilter Comparison")
    print("-" * 50)
    pre_results, post_results = compare_prefilter_vs_postfilter(
        query_vector,
        category="books",
        k=3
    )
    
    print("\n=== Summary ===")
    print(f"✓ Prefilter search: Filters BEFORE distance computation (faster)")
    print(f"✓ Use prefilter=True for better performance on large datasets")
    print(f"✓ Supports complex filters with AND/OR conditions")
    print("\nPrefilter search complete!")


if __name__ == "__main__":
    main()