# filepath: search.py
"""Search with post-filtering."""

import lancedb
import numpy as np
import pandas as pd
from typing import List, Optional

def search_with_filter(query_vector: List[float], category: str, k: int = 10):
    """Search with post-filtering on category.

    Args:
        query_vector: Query vector for similarity search
        category: Category to filter by
        k: Number of results to return before filtering
    
    Returns:
        pandas.DataFrame: Filtered search results
    
    Note:
        Post-filtering happens AFTER k results are selected from vector search.
        This means if k=10 and only 3 results match the category filter,
        you'll get 3 results (not 10).
    """
    try:
        # Connect to the database
        db = lancedb.connect("./my_lancedb")
        
        # Open the table
        table = db.open_table("products")
        
        # Perform vector search first, then apply post-filter
        # The .where() clause is applied AFTER the top-k vector search results
        results = (
            table.search(query_vector)
            .limit(k)
            .where(f"category = '{category}'")
            .to_pandas()
        )
        
        return results
    
    except Exception as e:
        print(f"Error during search with filter: {e}")
        raise

def create_sample_data():
    """Create sample data for demonstration."""
    try:
        # Connect to database
        db = lancedb.connect("./my_lancedb")
        
        # Create sample data with vectors and categories
        data = {
            "id": list(range(1, 21)),
            "name": [f"Product {i}" for i in range(1, 21)],
            "category": ["Electronics"] * 7 + ["Clothing"] * 7 + ["Books"] * 6,
            "price": np.random.uniform(10, 500, 20).tolist(),
            "vector": [np.random.randn(128).tolist() for _ in range(20)]
        }
        
        df = pd.DataFrame(data)
        
        # Create table (drop if exists)
        try:
            db.drop_table("products")
        except:
            pass
        
        table = db.create_table("products", df)
        print(f"Created table with {len(df)} products")
        
        return table
    
    except Exception as e:
        print(f"Error creating sample data: {e}")
        raise

def demonstrate_post_filtering():
    """Demonstrate the difference between pre-filtering and post-filtering."""
    try:
        db = lancedb.connect("./my_lancedb")
        table = db.open_table("products")
        
        # Generate a random query vector
        query_vector = np.random.randn(128).tolist()
        
        print("\n" + "="*60)
        print("POST-FILTERING DEMONSTRATION")
        print("="*60)
        
        # Example 1: Post-filtering (filter AFTER top-k selection)
        print("\n1. Post-filtering (filter AFTER selecting top-10):")
        print("   - First, find top-10 nearest neighbors")
        print("   - Then, filter those 10 results by category")
        print("   - May return fewer than 10 results\n")
        
        results_post = (
            table.search(query_vector)
            .limit(10)
            .where("category = 'Electronics'")
            .to_pandas()
        )
        
        print(f"Results found: {len(results_post)}")
        if len(results_post) > 0:
            print(results_post[["id", "name", "category", "price", "_distance"]].head())
        
        # Example 2: Show all top-10 without filter for comparison
        print("\n2. Without filter (all top-10 results):")
        results_all = (
            table.search(query_vector)
            .limit(10)
            .to_pandas()
        )
        
        print(f"Results found: {len(results_all)}")
        print(results_all[["id", "name", "category", "price", "_distance"]].head(10))
        
        # Show category distribution in top-10
        print("\nCategory distribution in top-10 results:")
        print(results_all["category"].value_counts())
        
        return results_post
    
    except Exception as e:
        print(f"Error in demonstration: {e}")
        raise

def search_multiple_categories(query_vector: List[float], 
                               categories: List[str], 
                               k: int = 10):
    """Search with post-filtering on multiple categories.
    
    Args:
        query_vector: Query vector for similarity search
        categories: List of categories to filter by
        k: Number of results to return before filtering
    
    Returns:
        pandas.DataFrame: Filtered search results
    """
    try:
        db = lancedb.connect("./my_lancedb")
        table = db.open_table("products")
        
        # Build WHERE clause for multiple categories
        category_conditions = " OR ".join([f"category = '{cat}'" for cat in categories])
        
        results = (
            table.search(query_vector)
            .limit(k)
            .where(category_conditions)
            .to_pandas()
        )
        
        return results
    
    except Exception as e:
        print(f"Error during multi-category search: {e}")
        raise

def main():
    """Main function to demonstrate search with post-filtering."""
    try:
        # Create sample data
        print("Creating sample data...")
        create_sample_data()
        
        # Demonstrate post-filtering
        demonstrate_post_filtering()
        
        # Example: Search for Electronics only
        print("\n" + "="*60)
        print("SPECIFIC CATEGORY SEARCH")
        print("="*60)
        
        query_vector = np.random.randn(128).tolist()
        
        print("\nSearching for Electronics products...")
        electronics_results = search_with_filter(
            query_vector=query_vector,
            category="Electronics",
            k=10
        )
        
        print(f"\nFound {len(electronics_results)} Electronics products:")
        if len(electronics_results) > 0:
            print(electronics_results[["id", "name", "category", "price", "_distance"]])
        
        # Example: Search multiple categories
        print("\n" + "="*60)
        print("MULTIPLE CATEGORIES SEARCH")
        print("="*60)
        
        print("\nSearching for Electronics OR Books...")
        multi_results = search_multiple_categories(
            query_vector=query_vector,
            categories=["Electronics", "Books"],
            k=10
        )
        
        print(f"\nFound {len(multi_results)} products:")
        if len(multi_results) > 0:
            print(multi_results[["id", "name", "category", "price", "_distance"]])
        
        print("\n" + "="*60)
        print("Post-filter search complete")
        print("="*60)
        
        # Important notes
        print("\nIMPORTANT NOTES:")
        print("- Post-filtering applies AFTER vector search selects top-k results")
        print("- If k=10 but only 3 match the filter, you get 3 results")
        print("- For guaranteed k results, use pre-filtering or increase k")
        print("- Post-filtering is faster but may return fewer results")
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()