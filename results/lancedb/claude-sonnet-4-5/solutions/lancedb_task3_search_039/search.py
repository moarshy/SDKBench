# filepath: search.py
"""Search with IVF-PQ index."""

import lancedb
import numpy as np
import pandas as pd
from typing import Optional


def create_ivf_pq_index(table):
    """Create IVF-PQ index for fast search.

    IVF-PQ (Inverted File with Product Quantization) is a two-level index:
    - IVF: Partitions the vector space into clusters (num_partitions)
    - PQ: Compresses vectors using product quantization (num_sub_vectors)

    Args:
        table: LanceDB table to index
    """
    try:
        # Create IVF-PQ index with specified parameters
        table.create_index(
            metric="cosine",  # Distance metric (cosine, L2, dot)
            num_partitions=256,  # Number of IVF partitions (coarse quantization)
            num_sub_vectors=96  # Number of PQ sub-vectors (fine quantization)
        )
        print(f"IVF-PQ index created successfully")
        print(f"  - Metric: cosine")
        print(f"  - Partitions: 256 (controls coarse quantization)")
        print(f"  - Sub-vectors: 96 (controls fine quantization)")
    except Exception as e:
        print(f"Error creating index: {e}")
        raise


def search_indexed(table, query_vector, k: int = 10, nprobes: Optional[int] = None):
    """Search using IVF-PQ index.

    The index is used automatically when available. The nprobes parameter
    controls the search-accuracy tradeoff:
    - Lower nprobes = faster but less accurate
    - Higher nprobes = slower but more accurate

    Args:
        table: LanceDB table with IVF-PQ index
        query_vector: Query vector (numpy array or list)
        k: Number of results to return
        nprobes: Number of partitions to search (default: sqrt(num_partitions))

    Returns:
        pandas.DataFrame with search results
    """
    try:
        # Convert query vector to numpy array if needed
        if isinstance(query_vector, list):
            query_vector = np.array(query_vector, dtype=np.float32)
        
        # Perform search - index is used automatically
        search_query = table.search(query_vector).limit(k)
        
        # Set nprobes to control search breadth
        # Higher nprobes = more accurate but slower
        # Default is typically sqrt(num_partitions) ≈ 16 for 256 partitions
        if nprobes is not None:
            search_query = search_query.nprobes(nprobes)
        
        # Execute search and return results
        results = search_query.to_pandas()
        
        return results
    except Exception as e:
        print(f"Error during search: {e}")
        raise


def main():
    """Demonstrate IVF-PQ indexed search."""
    
    # Connect to LanceDB
    db = lancedb.connect("./lancedb_data")
    
    # Create sample data with vectors
    print("Creating sample data...")
    dimension = 384  # Vector dimension
    num_vectors = 10000
    
    # Generate random vectors and metadata
    data = {
        "id": range(num_vectors),
        "vector": [np.random.randn(dimension).astype(np.float32).tolist() 
                   for _ in range(num_vectors)],
        "text": [f"Document {i}" for i in range(num_vectors)],
        "category": [f"Category {i % 10}" for i in range(num_vectors)]
    }
    df = pd.DataFrame(data)
    
    # Create table
    print(f"Creating table with {num_vectors} vectors of dimension {dimension}...")
    table = db.create_table("indexed_vectors", df, mode="overwrite")
    
    # Create IVF-PQ index
    print("\nCreating IVF-PQ index...")
    create_ivf_pq_index(table)
    
    # Generate query vector
    query_vector = np.random.randn(dimension).astype(np.float32)
    
    # Search with different nprobes values
    print("\n" + "="*60)
    print("Searching with different nprobes values:")
    print("="*60)
    
    for nprobes in [1, 10, 20, 50]:
        print(f"\nSearch with nprobes={nprobes}:")
        results = search_indexed(table, query_vector, k=5, nprobes=nprobes)
        print(f"  Found {len(results)} results")
        print(f"  Top result: {results.iloc[0]['text']} (distance: {results.iloc[0]['_distance']:.4f})")
    
    # Default search (uses automatic nprobes)
    print(f"\n" + "="*60)
    print("Search with default nprobes (automatic):")
    print("="*60)
    results = search_indexed(table, query_vector, k=10)
    print(f"\nTop 10 results:")
    print(results[['id', 'text', 'category', '_distance']].to_string(index=False))
    
    # Search with filter
    print(f"\n" + "="*60)
    print("Search with filter (category = 'Category 5'):")
    print("="*60)
    filtered_results = (table.search(query_vector)
                        .where("category = 'Category 5'")
                        .limit(5)
                        .nprobes(20)
                        .to_pandas())
    print(filtered_results[['id', 'text', 'category', '_distance']].to_string(index=False))
    
    print("\n" + "="*60)
    print("Indexed search complete")
    print("="*60)
    print("\nKey takeaways:")
    print("  - IVF-PQ index enables fast approximate search on large datasets")
    print("  - num_partitions controls coarse quantization (more = finer partitioning)")
    print("  - num_sub_vectors controls fine quantization (more = better accuracy)")
    print("  - nprobes controls search breadth (higher = more accurate but slower)")
    print("  - Index is used automatically when available")


if __name__ == "__main__":
    main()