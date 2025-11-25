# filepath: search.py
"""Search with prefiltering (more efficient)."""

import lancedb
import numpy as np
import pandas as pd


def search_with_prefilter(query_vector, category: str, k: int = 10):
    """Search with prefiltering for efficiency.

    Args:
        query_vector: Query vector for similarity search
        category: Category to filter by
        k: Number of results to return

    Returns:
        pandas.DataFrame: Search results with filtered data
    """
    # Connect to the database
    db = lancedb.connect("./lancedb")
    
    # Open the table
    table = db.open_table("products")
    
    # Perform prefiltered search
    # prefilter=True means filtering happens BEFORE distance computation
    # This is much more efficient for large datasets
    results = (
        table.search(query_vector)
        .where(f"category = '{category}'", prefilter=True)
        .limit(k)
        .to_pandas()
    )
    
    return results


def create_sample_data():
    """Create sample data for demonstration."""
    db = lancedb.connect("./lancedb")
    
    # Create sample data with vectors and metadata
    data = []
    categories = ["electronics", "clothing", "books", "home"]
    
    for i in range(1000):
        data.append({
            "id": i,
            "vector": np.random.randn(128).tolist(),  # 128-dim random vector
            "category": categories[i % len(categories)],
            "name": f"Product {i}",
            "price": np.random.uniform(10, 1000),
            "rating": np.random.uniform(1, 5)
        })
    
    # Create table with the data
    try:
        db.create_table("products", data, mode="overwrite")
        print(f"Created table with {len(data)} products")
    except Exception as e:
        print(f"Error creating table: {e}")


def demonstrate_prefilter_vs_postfilter(query_vector, category: str, k: int = 10):
    """Demonstrate the difference between prefilter and postfilter."""
    db = lancedb.connect("./lancedb")
    table = db.open_table("products")
    
    print("\n=== Prefilter Search (Efficient) ===")
    # Prefilter: Filter BEFORE computing distances
    prefilter_results = (
        table.search(query_vector)
        .where(f"category = '{category}'", prefilter=True)
        .limit(k)
        .to_pandas()
    )
    print(f"Found {len(prefilter_results)} results with prefilter")
    print(prefilter_results[["id", "category", "name", "price"]].head())
    
    print("\n=== Postfilter Search (Less Efficient) ===")
    # Postfilter: Compute distances THEN filter
    # This computes distances for ALL vectors, then filters
    postfilter_results = (
        table.search(query_vector)
        .where(f"category = '{category}'")  # No prefilter=True
        .limit(k)
        .to_pandas()
    )
    print(f"Found {len(postfilter_results)} results with postfilter")
    print(postfilter_results[["id", "category", "name", "price"]].head())
    
    return prefilter_results, postfilter_results


def advanced_prefilter_examples():
    """Show advanced prefiltering examples."""
    db = lancedb.connect("./lancedb")
    table = db.open_table("products")
    
    # Generate a random query vector
    query_vector = np.random.randn(128).tolist()
    
    print("\n=== Advanced Prefilter Examples ===")
    
    # Example 1: Multiple conditions with AND
    print("\n1. Multiple conditions (category AND price range):")
    results = (
        table.search(query_vector)
        .where("category = 'electronics' AND price < 500", prefilter=True)
        .limit(5)
        .to_pandas()
    )
    print(results[["id", "category", "name", "price"]])
    
    # Example 2: OR conditions
    print("\n2. OR conditions (multiple categories):")
    results = (
        table.search(query_vector)
        .where("category = 'electronics' OR category = 'books'", prefilter=True)
        .limit(5)
        .to_pandas()
    )
    print(results[["id", "category", "name"]])
    
    # Example 3: Range queries
    print("\n3. Range query (high-rated products):")
    results = (
        table.search(query_vector)
        .where("rating >= 4.0", prefilter=True)
        .limit(5)
        .to_pandas()
    )
    print(results[["id", "name", "rating"]])
    
    # Example 4: Complex conditions
    print("\n4. Complex conditions:")
    results = (
        table.search(query_vector)
        .where("category = 'clothing' AND price BETWEEN 50 AND 200 AND rating > 3.5", prefilter=True)
        .limit(5)
        .to_pandas()
    )
    print(results[["id", "category", "name", "price", "rating"]])


def main():
    """Main function to demonstrate prefiltered search."""
    print("=== LanceDB Prefiltered Vector Search Demo ===\n")
    
    # Create sample data
    print("Creating sample data...")
    create_sample_data()
    
    # Generate a random query vector (128 dimensions)
    query_vector = np.random.randn(128).tolist()
    
    # Perform prefiltered search
    print("\n=== Basic Prefiltered Search ===")
    category = "electronics"
    results = search_with_prefilter(query_vector, category, k=5)
    
    print(f"\nTop 5 results for category '{category}':")
    print(results[["id", "category", "name", "price"]])
    
    # Compare prefilter vs postfilter
    demonstrate_prefilter_vs_postfilter(query_vector, "books", k=5)
    
    # Show advanced examples
    advanced_prefilter_examples()
    
    print("\n✓ Prefilter search complete")
    print("\nKey Benefits of Prefiltering:")
    print("1. Faster: Computes distances only for filtered subset")
    print("2. More efficient: Reduces computational overhead")
    print("3. Scalable: Performance improves with selective filters")
    print("4. Best practice: Use prefilter=True when possible")


if __name__ == "__main__":
    main()