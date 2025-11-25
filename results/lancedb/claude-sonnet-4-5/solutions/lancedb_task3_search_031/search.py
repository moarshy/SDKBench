# filepath: search.py
"""Basic vector similarity search."""

import lancedb
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Optional, List
import os

# Initialize embedding model globally for reuse
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def create_sample_data():
    """Create sample data for demonstration if database doesn't exist."""
    documents = [
        "Machine learning is a subset of artificial intelligence",
        "Deep learning uses neural networks with multiple layers",
        "Natural language processing helps computers understand human language",
        "Computer vision enables machines to interpret visual information",
        "Reinforcement learning trains agents through rewards and penalties",
        "Supervised learning uses labeled data for training",
        "Unsupervised learning finds patterns in unlabeled data",
        "Transfer learning applies knowledge from one task to another",
        "Python is a popular programming language for data science",
        "TensorFlow and PyTorch are deep learning frameworks"
    ]
    
    # Generate embeddings for documents
    embeddings = embedding_model.encode(documents)
    
    # Create DataFrame with documents and their embeddings
    data = pd.DataFrame({
        'text': documents,
        'vector': [emb.tolist() for emb in embeddings],
        'id': range(len(documents))
    })
    
    return data

def initialize_database(db_path: str = "./lancedb", table_name: str = "documents"):
    """Initialize database with sample data if it doesn't exist."""
    try:
        db = lancedb.connect(db_path)
        
        # Check if table exists
        try:
            table = db.open_table(table_name)
            print(f"Table '{table_name}' already exists with {len(table)} records")
            return db, table
        except Exception:
            # Table doesn't exist, create it with sample data
            print(f"Creating new table '{table_name}' with sample data...")
            data = create_sample_data()
            table = db.create_table(table_name, data, mode="overwrite")
            print(f"Created table with {len(table)} records")
            return db, table
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def search_similar(
    query_text: str, 
    k: int = 5,
    db_path: str = "./lancedb",
    table_name: str = "documents",
    filter_condition: Optional[str] = None
) -> pd.DataFrame:
    """Search for similar documents using vector similarity.

    Args:
        query_text: The text query to search for
        k: Number of results to return (default: 5)
        db_path: Path to the LanceDB database (default: "./lancedb")
        table_name: Name of the table to search (default: "documents")
        filter_condition: Optional SQL-like filter condition (e.g., "id > 5")

    Returns:
        pandas DataFrame with search results including text, similarity score, and metadata
    """
    try:
        # Connect to database and open table
        db = lancedb.connect(db_path)
        table = db.open_table(table_name)
        
        # Generate query embedding
        print(f"Generating embedding for query: '{query_text}'")
        query_vector = embedding_model.encode(query_text).tolist()
        
        # Perform vector similarity search
        search_query = table.search(query_vector).limit(k)
        
        # Apply filter if provided
        if filter_condition:
            search_query = search_query.where(filter_condition)
        
        # Execute search and convert to pandas DataFrame
        results = search_query.to_pandas()
        
        # Add distance as similarity score (lower distance = higher similarity)
        if '_distance' in results.columns:
            results['similarity_score'] = 1 / (1 + results['_distance'])
        
        print(f"Found {len(results)} results")
        return results
        
    except FileNotFoundError:
        print(f"Database not found at '{db_path}'. Initializing with sample data...")
        db, table = initialize_database(db_path, table_name)
        
        # Retry search after initialization
        query_vector = embedding_model.encode(query_text).tolist()
        search_query = table.search(query_vector).limit(k)
        
        if filter_condition:
            search_query = search_query.where(filter_condition)
            
        results = search_query.to_pandas()
        
        if '_distance' in results.columns:
            results['similarity_score'] = 1 / (1 + results['_distance'])
        
        print(f"Found {len(results)} results")
        return results
        
    except Exception as e:
        print(f"Error during search: {e}")
        raise

def search_with_metadata_filter(
    query_text: str,
    k: int = 5,
    min_id: Optional[int] = None
) -> pd.DataFrame:
    """Search with metadata filtering example.
    
    Args:
        query_text: The text query to search for
        k: Number of results to return
        min_id: Minimum ID value for filtering results
        
    Returns:
        pandas DataFrame with filtered search results
    """
    filter_condition = f"id >= {min_id}" if min_id is not None else None
    return search_similar(query_text, k=k, filter_condition=filter_condition)

def main():
    """Main function demonstrating various search capabilities."""
    print("=" * 60)
    print("LanceDB Vector Similarity Search Demo")
    print("=" * 60)
    
    # Initialize database with sample data if needed
    print("\n1. Initializing database...")
    initialize_database()
    
    # Basic search
    print("\n2. Basic vector similarity search:")
    print("-" * 60)
    results = search_similar("machine learning", k=10)
    print("\nTop results:")
    for idx, row in results.head(5).iterrows():
        score = row.get('similarity_score', 'N/A')
        print(f"  - {row['text']}")
        print(f"    Similarity: {score:.4f}" if isinstance(score, float) else f"    Similarity: {score}")
    
    # Search with fewer results
    print("\n3. Search with k=3:")
    print("-" * 60)
    results = search_similar("neural networks", k=3)
    print(f"Found {len(results)} results")
    for idx, row in results.iterrows():
        print(f"  - {row['text']}")
    
    # Search with filter
    print("\n4. Search with metadata filter (id >= 5):")
    print("-" * 60)
    results = search_with_metadata_filter("artificial intelligence", k=5, min_id=5)
    print(f"Found {len(results)} results (filtered)")
    for idx, row in results.iterrows():
        print(f"  - ID {row['id']}: {row['text']}")
    
    # Different query
    print("\n5. Search for 'programming languages':")
    print("-" * 60)
    results = search_similar("programming languages", k=5)
    for idx, row in results.head(3).iterrows():
        score = row.get('similarity_score', 'N/A')
        print(f"  - {row['text']}")
        print(f"    Similarity: {score:.4f}" if isinstance(score, float) else f"    Similarity: {score}")
    
    print("\n" + "=" * 60)
    print("Search demo completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()