I'll help you implement hybrid search with Full-Text Search (FTS) using LanceDB. Let me provide the complete solution.

```txt
# filepath: requirements.txt
pandas>=2.0.0
numpy>=1.24.0
lancedb>=0.5.0
pyarrow>=12.0.0
tantivy>=0.20.0
```

```python
# filepath: search.py
"""Hybrid search with Full-Text Search."""

import lancedb
import pandas as pd
import numpy as np
from typing import Optional


def setup_fts_index(table):
    """Create FTS index on table.
    
    Creates a full-text search index using BM25 algorithm
    for efficient text-based retrieval.
    
    Args:
        table: LanceDB table instance
    """
    try:
        # Create FTS index on the "text" column
        # This enables BM25 text search capabilities
        table.create_fts_index("text")
        print("FTS index created successfully on 'text' column")
    except Exception as e:
        print(f"Error creating FTS index: {e}")
        # Index might already exist, which is fine
        pass


def hybrid_search(
    table,
    query_text: str,
    query_vector: np.ndarray,
    k: int = 10
) -> pd.DataFrame:
    """Perform hybrid vector + text search.
    
    Combines vector similarity search with BM25 full-text search
    to leverage both semantic and keyword-based matching.
    
    Args:
        table: LanceDB table instance
        query_text: Text query for BM25 search
        query_vector: Vector embedding for similarity search
        k: Number of results to return
        
    Returns:
        DataFrame with hybrid search results
    """
    try:
        # Perform hybrid search combining vector similarity and text search
        # The results are automatically ranked using a combination of:
        # - Vector similarity scores
        # - BM25 text relevance scores
        results = (
            table.search(query_type="hybrid")
            .vector(query_vector)
            .text(query_text)
            .limit(k)
            .to_pandas()
        )
        
        print(f"Hybrid search returned {len(results)} results")
        return results
    
    except Exception as e:
        print(f"Error performing hybrid search: {e}")
        return pd.DataFrame()


def vector_search(
    table,
    query_vector: np.ndarray,
    k: int = 10,
    filter_condition: Optional[str] = None
) -> pd.DataFrame:
    """Perform pure vector similarity search.
    
    Args:
        table: LanceDB table instance
        query_vector: Vector embedding for similarity search
        k: Number of results to return
        filter_condition: Optional SQL-like filter (e.g., "category = 'tech'")
        
    Returns:
        DataFrame with vector search results
    """
    try:
        search_query = table.search(query_vector).limit(k)
        
        # Apply filter if provided
        if filter_condition:
            search_query = search_query.where(filter_condition)
        
        results = search_query.to_pandas()
        print(f"Vector search returned {len(results)} results")
        return results
    
    except Exception as e:
        print(f"Error performing vector search: {e}")
        return pd.DataFrame()


def text_search(
    table,
    query_text: str,
    k: int = 10
) -> pd.DataFrame:
    """Perform pure full-text search using BM25.
    
    Args:
        table: LanceDB table instance
        query_text: Text query for BM25 search
        k: Number of results to return
        
    Returns:
        DataFrame with text search results
    """
    try:
        # Perform BM25 full-text search
        results = (
            table.search(query_text, query_type="fts")
            .limit(k)
            .to_pandas()
        )
        
        print(f"Text search returned {len(results)} results")
        return results
    
    except Exception as e:
        print(f"Error performing text search: {e}")
        return pd.DataFrame()


def create_sample_data() -> pd.DataFrame:
    """Create sample data for demonstration."""
    data = {
        "id": [1, 2, 3, 4, 5],
        "text": [
            "Machine learning is a subset of artificial intelligence",
            "Deep learning uses neural networks with multiple layers",
            "Natural language processing enables computers to understand text",
            "Computer vision allows machines to interpret visual information",
            "Reinforcement learning trains agents through rewards and penalties"
        ],
        "vector": [
            np.random.randn(128).tolist() for _ in range(5)
        ],
        "category": ["AI", "AI", "NLP", "CV", "RL"]
    }
    return pd.DataFrame(data)


def main():
    """Main function demonstrating hybrid search capabilities."""
    try:
        # Connect to LanceDB
        db = lancedb.connect("./lancedb_data")
        print("Connected to LanceDB")
        
        # Create sample data
        sample_data = create_sample_data()
        
        # Create or open table
        table_name = "hybrid_search_demo"
        try:
            # Try to create new table
            table = db.create_table(table_name, sample_data, mode="overwrite")
            print(f"Created table '{table_name}' with {len(sample_data)} records")
        except Exception as e:
            # If table exists, open it
            table = db.open_table(table_name)
            print(f"Opened existing table '{table_name}'")
        
        # Setup FTS index
        setup_fts_index(table)
        
        # Example queries
        query_text = "neural networks and deep learning"
        query_vector = np.random.randn(128)  # In practice, use actual embeddings
        
        print("\n" + "="*60)
        print("1. HYBRID SEARCH (Vector + Text)")
        print("="*60)
        hybrid_results = hybrid_search(table, query_text, query_vector, k=3)
        if not hybrid_results.empty:
            print("\nTop results:")
            for idx, row in hybrid_results.iterrows():
                print(f"  {idx+1}. {row['text'][:60]}...")
                print(f"     Category: {row['category']}")
        
        print("\n" + "="*60)
        print("2. VECTOR SEARCH ONLY")
        print("="*60)
        vector_results = vector_search(table, query_vector, k=3)
        if not vector_results.empty:
            print(f"\nFound {len(vector_results)} results")
        
        print("\n" + "="*60)
        print("3. TEXT SEARCH ONLY (BM25)")
        print("="*60)
        text_results = text_search(table, query_text, k=3)
        if not text_results.empty:
            print("\nTop text matches:")
            for idx, row in text_results.iterrows():
                print(f"  {idx+1}. {row['text'][:60]}...")
        
        print("\n" + "="*60)
        print("4. FILTERED VECTOR SEARCH")
        print("="*60)
        filtered_results = vector_search(
            table, 
            query_vector, 
            k=3, 
            filter_condition="category = 'AI'"
        )
        if not filtered_results.empty:
            print(f"\nFound {len(filtered_results)} AI-related results")
        
        print("\n" + "="*60)
        print("Hybrid search complete")
        print("="*60)
        
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
```

This implementation provides:

1. **FTS Index Setup**: Creates a full-text search index on the "text" column using BM25 algorithm

2. **Hybrid Search**: Combines vector similarity and text search for best results
   - Uses `query_type="hybrid"`
   - Passes both vector and text queries
   - Automatically ranks results using combined scores

3. **Vector Search**: Pure similarity search with optional filtering
   - Supports SQL-like filter conditions
   - Returns top-k nearest neighbors

4. **Text Search**: Pure BM25 full-text search
   - Keyword-based retrieval
   - Good for exact phrase matching

5. **Error Handling**: Comprehensive try-catch blocks for robustness

6. **Demo**: Complete example with sample data showing all search types

The hybrid search is particularly powerful because it:
- Captures semantic similarity through vectors
- Captures keyword relevance through BM25
- Combines both signals for better ranking
- Works well when queries have both semantic and keyword components