# filepath: search.py
"""Tuned search with nprobes and refine_factor."""

import lancedb
import numpy as np
import pandas as pd
from typing import Optional, List

def search_tuned(
    table: lancedb.table.Table,
    query_vector: List[float],
    k: int = 10,
    nprobes: int = 20,
    refine: int = 50
) -> pd.DataFrame:
    """Search with tuned parameters.
    
    Args:
        table: LanceDB table to search
        query_vector: Query vector for similarity search
        k: Number of results to return
        nprobes: Number of probes for IVF index search (higher = more accurate, slower)
        refine: Refine factor for re-ranking precision (higher = more accurate, slower)
    
    Returns:
        DataFrame with search results
    
    Notes:
        - nprobes: Controls how many partitions to search in IVF index
          Default is usually 20. Range: 1 to number of partitions
        - refine_factor: Multiplier for initial candidates before re-ranking
          If refine=50 and k=10, fetches 500 candidates then re-ranks to top 10
    
    Example:
        table.search(query_vector)
             .nprobes(20)
             .refine_factor(50)
             .limit(k)
             .to_pandas()
    """
    try:
        results = (
            table.search(query_vector)
            .nprobes(nprobes)
            .refine_factor(refine)
            .limit(k)
            .to_pandas()
        )
        return results
    except Exception as e:
        print(f"Error during search: {e}")
        raise

def create_sample_data(num_vectors: int = 1000, dim: int = 128) -> pd.DataFrame:
    """Create sample data for demonstration."""
    data = {
        "id": range(num_vectors),
        "vector": [np.random.randn(dim).tolist() for _ in range(num_vectors)],
        "text": [f"Document {i}" for i in range(num_vectors)],
        "category": [f"cat_{i % 10}" for i in range(num_vectors)]
    }
    return pd.DataFrame(data)

def main():
    """Demonstrate tuned search with different parameter configurations."""
    
    # Connect to LanceDB
    db = lancedb.connect("./lancedb_data")
    
    # Create sample data
    print("Creating sample data...")
    data = create_sample_data(num_vectors=10000, dim=128)
    
    # Create table (drop if exists)
    table_name = "tuned_search_demo"
    try:
        db.drop_table(table_name)
    except:
        pass
    
    table = db.create_table(table_name, data)
    print(f"Created table with {len(data)} vectors")
    
    # Create an IVF_PQ index for efficient search
    # This is necessary for nprobes to have an effect
    print("\nCreating IVF_PQ index...")
    table.create_index(
        metric="L2",
        num_partitions=256,  # Number of partitions for IVF
        num_sub_vectors=16   # Number of sub-vectors for PQ
    )
    print("Index created successfully")
    
    # Generate a random query vector
    query_vector = np.random.randn(128).tolist()
    
    # Example 1: Fast search (lower accuracy)
    print("\n" + "="*60)
    print("Example 1: Fast Search (lower nprobes, lower refine)")
    print("="*60)
    results_fast = search_tuned(
        table=table,
        query_vector=query_vector,
        k=10,
        nprobes=5,      # Search fewer partitions
        refine=10       # Less re-ranking
    )
    print(f"Found {len(results_fast)} results")
    print(results_fast[['id', 'text', 'category', '_distance']].head())
    
    # Example 2: Balanced search (default parameters)
    print("\n" + "="*60)
    print("Example 2: Balanced Search (default parameters)")
    print("="*60)
    results_balanced = search_tuned(
        table=table,
        query_vector=query_vector,
        k=10,
        nprobes=20,     # Default: good balance
        refine=50       # Default: good balance
    )
    print(f"Found {len(results_balanced)} results")
    print(results_balanced[['id', 'text', 'category', '_distance']].head())
    
    # Example 3: High accuracy search (higher values)
    print("\n" + "="*60)
    print("Example 3: High Accuracy Search (higher nprobes, higher refine)")
    print("="*60)
    results_accurate = search_tuned(
        table=table,
        query_vector=query_vector,
        k=10,
        nprobes=50,     # Search more partitions
        refine=100      # More re-ranking
    )
    print(f"Found {len(results_accurate)} results")
    print(results_accurate[['id', 'text', 'category', '_distance']].head())
    
    # Compare distances to show accuracy improvement
    print("\n" + "="*60)
    print("Distance Comparison (lower is better)")
    print("="*60)
    print(f"Fast search avg distance:     {results_fast['_distance'].mean():.6f}")
    print(f"Balanced search avg distance: {results_balanced['_distance'].mean():.6f}")
    print(f"Accurate search avg distance: {results_accurate['_distance'].mean():.6f}")
    
    print("\n" + "="*60)
    print("Tuned search complete")
    print("="*60)
    print("\nKey Takeaways:")
    print("- nprobes: Controls IVF index search breadth (5-50 typical range)")
    print("- refine_factor: Controls re-ranking precision (10-100 typical range)")
    print("- Higher values = more accurate but slower")
    print("- Tune based on your accuracy/speed requirements")

if __name__ == "__main__":
    main()