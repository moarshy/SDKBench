# filepath: search.py
"""Search with IVF-PQ index."""

import lancedb
import numpy as np
import pandas as pd
from typing import Optional


def create_ivf_pq_index(table):
    """Create IVF-PQ index for fast search.

    IVF-PQ (Inverted File with Product Quantization) is a two-level index:
    - IVF: Coarse quantization using num_partitions clusters
    - PQ: Fine quantization using num_sub_vectors for compression
    
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
        print(f"IVF-PQ index created successfully with 256 partitions and 96 sub-vectors")
    except Exception as e:
        print(f"Error creating index: {e}")
        raise


def search_indexed(table, query_vector, k: int = 10, nprobes: Optional[int] = None):
    """Search using IVF-PQ index.

    The index is used automatically when available. The nprobes parameter
    controls the search-accuracy tradeoff:
    - Higher nprobes = more accurate but slower
    - Lower nprobes = faster but less accurate
    
    Args:
        table: LanceDB table with IVF-PQ index
        query_vector: Query vector (numpy array or list)
        k: Number of results to return
        nprobes: Number of partitions to search (default: sqrt(num_partitions))
    
    Returns:
        pandas.DataFrame with search results
    """
    try:
        # Convert query_vector to list if it's a numpy array
        if isinstance(query_vector, np.ndarray):
            query_vector = query_vector.tolist()
        
        # Perform search - index is used automatically
        search_query = table.search(query_vector).limit(k)
        
        # Set nprobes if specified (controls search breadth)
        # Higher nprobes = search more partitions = more accurate but slower
        if nprobes is not None:
            search_query = search_query.nprobes(nprobes)
        
        # Execute search and return results as DataFrame
        results = search_query.to_pandas()
        
        print(f"Search completed: found {len(results)} results")
        if nprobes:
            print(f"Used nprobes={nprobes} for search")
        
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
    dimension = 128
    num_vectors = 10000
    
    # Generate random vectors and metadata
    data = {
        "id": range(num_vectors),
        "vector": [np.random.randn(dimension).tolist() for _ in range(num_vectors)],
        "category": [f"cat_{i % 10}" for i in range(num_vectors)],
        "value": np.random.randint(0, 100, num_vectors).tolist()
    }
    
    df = pd.DataFrame(data)
    
    # Create table
    print("Creating table...")
    table_name = "ivf_pq_demo"
    
    # Drop table if it exists
    try:
        db.drop_table(table_name)
    except:
        pass
    
    table = db.create_table(table_name, df)
    print(f"Table created with {len(df)} vectors")
    
    # Create IVF-PQ index
    print("\nCreating IVF-PQ index...")
    create_ivf_pq_index(table)
    
    # Generate a query vector
    query_vector = np.random.randn(dimension)
    
    # Perform searches with different nprobes values
    print("\n" + "="*60)
    print("Search 1: Default nprobes (automatic)")
    print("="*60)
    results1 = search_indexed(table, query_vector, k=10)
    print(f"\nTop 3 results:")
    print(results1[["id", "category", "value", "_distance"]].head(3))
    
    print("\n" + "="*60)
    print("Search 2: Low nprobes (faster, less accurate)")
    print("="*60)
    results2 = search_indexed(table, query_vector, k=10, nprobes=10)
    print(f"\nTop 3 results:")
    print(results2[["id", "category", "value", "_distance"]].head(3))
    
    print("\n" + "="*60)
    print("Search 3: High nprobes (slower, more accurate)")
    print("="*60)
    results3 = search_indexed(table, query_vector, k=10, nprobes=50)
    print(f"\nTop 3 results:")
    print(results3[["id", "category", "value", "_distance"]].head(3))
    
    # Demonstrate filtered search
    print("\n" + "="*60)
    print("Search 4: With filter (category = 'cat_5')")
    print("="*60)
    filtered_results = (
        table.search(query_vector.tolist())
        .where("category = 'cat_5'")
        .limit(5)
        .nprobes(20)
        .to_pandas()
    )
    print(f"Found {len(filtered_results)} results in category 'cat_5'")
    print(filtered_results[["id", "category", "value", "_distance"]])
    
    print("\n" + "="*60)
    print("Indexed search complete")
    print("="*60)
    print("\nKey takeaways:")
    print("- IVF-PQ index enables fast approximate nearest neighbor search")
    print("- num_partitions controls coarse quantization (more = finer granularity)")
    print("- num_sub_vectors controls compression (more = better accuracy, larger index)")
    print("- nprobes controls search breadth (higher = more accurate, slower)")
    print("- Index is used automatically when available")


if __name__ == "__main__":
    main()