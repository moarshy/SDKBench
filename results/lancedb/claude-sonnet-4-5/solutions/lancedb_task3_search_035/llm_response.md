I'll help you implement a tuned search with nprobes and refine_factor parameters in LanceDB. These parameters are crucial for optimizing the trade-off between search accuracy and performance.

```txt
# filepath: requirements.txt
pandas>=2.0.0
numpy>=1.24.0
lancedb>=0.5.0
```

```python
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
        refine: Refine factor for re-ranking (higher = more accurate, slower)
    
    Returns:
        DataFrame with search results
    
    Notes:
        - nprobes: Controls how many partitions to search in IVF index
          Default is usually 20. Range: 1 to number of partitions
        - refine_factor: Re-ranks top (k * refine_factor) candidates
          Default is usually 1 (no refinement). Higher values improve accuracy
    
    Example:
        table.search(query_vector)
             .nprobes(20)
             .refine_factor(50)
             .limit(k)
             .to_pandas()
    """
    try:
        # Perform tuned search with nprobes and refine_factor
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


def create_sample_data(n_samples: int = 1000, n_dims: int = 128) -> pd.DataFrame:
    """Create sample data for demonstration."""
    data = {
        "id": range(n_samples),
        "vector": [np.random.randn(n_dims).tolist() for _ in range(n_samples)],
        "text": [f"Document {i}" for i in range(n_samples)],
        "category": [f"Category {i % 5}" for i in range(n_samples)]
    }
    return pd.DataFrame(data)


def compare_search_parameters(
    table: lancedb.table.Table,
    query_vector: List[float],
    k: int = 10
):
    """Compare different search parameter configurations."""
    
    print("\n" + "="*60)
    print("Comparing Search Parameter Configurations")
    print("="*60)
    
    # Configuration 1: Fast search (low accuracy)
    print("\n1. Fast Search (nprobes=5, refine_factor=1)")
    results_fast = search_tuned(table, query_vector, k=k, nprobes=5, refine=1)
    print(f"   Results: {len(results_fast)} rows")
    print(f"   Top distance: {results_fast['_distance'].iloc[0]:.4f}")
    
    # Configuration 2: Balanced search (default)
    print("\n2. Balanced Search (nprobes=20, refine_factor=10)")
    results_balanced = search_tuned(table, query_vector, k=k, nprobes=20, refine=10)
    print(f"   Results: {len(results_balanced)} rows")
    print(f"   Top distance: {results_balanced['_distance'].iloc[0]:.4f}")
    
    # Configuration 3: Accurate search (high accuracy)
    print("\n3. Accurate Search (nprobes=50, refine_factor=50)")
    results_accurate = search_tuned(table, query_vector, k=k, nprobes=50, refine=50)
    print(f"   Results: {len(results_accurate)} rows")
    print(f"   Top distance: {results_accurate['_distance'].iloc[0]:.4f}")
    
    print("\n" + "="*60)
    print("Note: Lower distances indicate better matches")
    print("Higher nprobes/refine_factor = more accurate but slower")
    print("="*60)


def main():
    """Main function demonstrating tuned search."""
    
    # Connect to LanceDB
    db = lancedb.connect("./lancedb_tuned_search")
    
    # Create sample data
    print("Creating sample data...")
    data = create_sample_data(n_samples=1000, n_dims=128)
    
    # Create table
    table_name = "documents"
    try:
        # Drop table if exists
        try:
            db.drop_table(table_name)
        except:
            pass
        
        # Create new table
        table = db.create_table(table_name, data)
        print(f"Created table '{table_name}' with {len(data)} documents")
        
        # Create IVF_PQ index for efficient search
        # This is necessary for nprobes to have an effect
        print("\nCreating IVF_PQ index...")
        table.create_index(
            metric="L2",
            num_partitions=50,  # Number of partitions for IVF
            num_sub_vectors=16   # Number of sub-vectors for PQ
        )
        print("Index created successfully")
        
    except Exception as e:
        print(f"Table already exists, opening it: {e}")
        table = db.open_table(table_name)
    
    # Create a query vector
    query_vector = np.random.randn(128).tolist()
    
    # Perform tuned search
    print("\n" + "="*60)
    print("Performing Tuned Search")
    print("="*60)
    
    k = 10
    nprobes = 20
    refine_factor = 50
    
    print(f"\nSearch parameters:")
    print(f"  - k (results): {k}")
    print(f"  - nprobes: {nprobes}")
    print(f"  - refine_factor: {refine_factor}")
    
    results = search_tuned(
        table=table,
        query_vector=query_vector,
        k=k,
        nprobes=nprobes,
        refine=refine_factor
    )
    
    print(f"\nSearch Results (Top {k}):")
    print("-" * 60)
    print(results[['id', 'text', 'category', '_distance']].to_string(index=False))
    
    # Compare different parameter configurations
    compare_search_parameters(table, query_vector, k=5)
    
    # Additional example: Search with filter
    print("\n" + "="*60)
    print("Tuned Search with Filter")
    print("="*60)
    
    filtered_results = (
        table.search(query_vector)
        .where("category = 'Category 1'", prefilter=True)
        .nprobes(20)
        .refine_factor(50)
        .limit(5)
        .to_pandas()
    )
    
    print(f"\nFiltered Results (Category 1 only):")
    print("-" * 60)
    print(filtered_results[['id', 'text', 'category', '_distance']].to_string(index=False))
    
    print("\n" + "="*60)
    print("Tuned search complete")
    print("="*60)
    
    # Performance tips
    print("\n📊 Performance Tuning Tips:")
    print("  • nprobes: Start with 20, increase for better accuracy")
    print("  • refine_factor: Use 10-50 for production workloads")
    print("  • Create IVF_PQ index for large datasets (>100k vectors)")
    print("  • Balance accuracy vs. latency based on your use case")
    print("  • Monitor query latency and adjust parameters accordingly")


if __name__ == "__main__":
    main()
```

This implementation provides:

1. **Tuned Search Function**: The `search_tuned()` function implements vector search with configurable `nprobes` and `refine_factor` parameters for optimizing the accuracy-performance trade-off.

2. **Parameter Explanation**:
   - **nprobes**: Controls how many partitions to search in an IVF (Inverted File) index. Higher values search more partitions, improving accuracy but increasing latency.
   - **refine_factor**: Re-ranks the top (k × refine_factor) candidates using exact distance calculations. Higher values improve accuracy by considering more candidates.

3. **Index Creation**: Creates an IVF_PQ index which is necessary for `nprobes` to have an effect. Without an index, these parameters are ignored.

4. **Parameter Comparison**: The `compare_search_parameters()` function demonstrates different configurations (fast, balanced, accurate) to show the trade-offs.

5. **Filtered Search**: Shows how to combine tuned search with filters for more specific queries.

6. **Best Practices**:
   - Start with default values (nprobes=20, refine_factor=10)
   - Increase for better accuracy when needed
   - Monitor query latency in production
   - Create appropriate indexes for large datasets

The code is production-ready with proper error handling, type hints, and comprehensive documentation.