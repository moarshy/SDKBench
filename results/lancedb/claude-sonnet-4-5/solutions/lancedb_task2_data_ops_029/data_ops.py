# filepath: data_ops.py
"""Multi-table schema with relationships."""

from typing import Optional, List, Dict, Any
import lancedb
from lancedb.pydantic import LanceModel, Vector
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer


# Define User schema
class User(LanceModel):
    """User table schema."""
    user_id: str
    name: str
    email: str


# Define Document schema with user_id as foreign key
class Document(LanceModel):
    """Document table schema with vector embeddings."""
    doc_id: str
    text: str
    vector: Vector(384)  # 384 dimensions for sentence-transformers/all-MiniLM-L6-v2
    user_id: str  # Foreign key reference to User table


def create_related_tables(db: lancedb.DBConnection) -> tuple:
    """Create multiple related tables.
    
    Args:
        db: LanceDB connection
        
    Returns:
        Tuple of (users_table, documents_table)
    """
    try:
        # Create users table
        users_data = [
            {"user_id": "u1", "name": "Alice Smith", "email": "alice@example.com"},
            {"user_id": "u2", "name": "Bob Johnson", "email": "bob@example.com"},
            {"user_id": "u3", "name": "Carol Williams", "email": "carol@example.com"},
        ]
        
        # Drop existing tables if they exist
        try:
            db.drop_table("users")
        except Exception:
            pass
            
        try:
            db.drop_table("documents")
        except Exception:
            pass
        
        users_table = db.create_table("users", schema=User, mode="overwrite")
        users_table.add(users_data)
        
        # Create documents table with user_id reference
        # Initialize embedding model
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        documents_data = [
            {
                "doc_id": "d1",
                "text": "Introduction to machine learning and AI",
                "user_id": "u1"
            },
            {
                "doc_id": "d2",
                "text": "Deep learning with neural networks",
                "user_id": "u1"
            },
            {
                "doc_id": "d3",
                "text": "Natural language processing basics",
                "user_id": "u2"
            },
            {
                "doc_id": "d4",
                "text": "Computer vision and image recognition",
                "user_id": "u2"
            },
            {
                "doc_id": "d5",
                "text": "Reinforcement learning algorithms",
                "user_id": "u3"
            },
        ]
        
        # Generate embeddings for documents
        for doc in documents_data:
            embedding = model.encode(doc["text"])
            doc["vector"] = embedding.tolist()
        
        documents_table = db.create_table("documents", schema=Document, mode="overwrite")
        documents_table.add(documents_data)
        
        print(f"Created users table with {len(users_data)} records")
        print(f"Created documents table with {len(documents_data)} records")
        
        return users_table, documents_table
        
    except Exception as e:
        print(f"Error creating related tables: {e}")
        raise


def join_query(db: lancedb.DBConnection, user_id: str) -> pd.DataFrame:
    """Query documents with user info (simulated join).
    
    Args:
        db: LanceDB connection
        user_id: User ID to query documents for
        
    Returns:
        DataFrame with combined user and document information
    """
    try:
        # Open tables
        users_table = db.open_table("users")
        documents_table = db.open_table("documents")
        
        # Get user info
        users_df = users_table.to_pandas()
        user_info = users_df[users_df['user_id'] == user_id]
        
        if user_info.empty:
            print(f"No user found with user_id: {user_id}")
            return pd.DataFrame()
        
        # Get documents for this user
        documents_df = documents_table.to_pandas()
        user_documents = documents_df[documents_df['user_id'] == user_id]
        
        if user_documents.empty:
            print(f"No documents found for user_id: {user_id}")
            return pd.DataFrame()
        
        # Perform a manual join by merging dataframes
        result = user_documents.merge(
            user_info[['user_id', 'name', 'email']], 
            on='user_id', 
            how='left'
        )
        
        print(f"\nDocuments for user {user_id} ({user_info.iloc[0]['name']}):")
        print(f"Found {len(result)} documents")
        
        return result
        
    except Exception as e:
        print(f"Error performing join query: {e}")
        raise


def vector_search_with_user_info(
    db: lancedb.DBConnection, 
    query_text: str, 
    limit: int = 3
) -> pd.DataFrame:
    """Perform vector search and include user information.
    
    Args:
        db: LanceDB connection
        query_text: Text to search for
        limit: Maximum number of results
        
    Returns:
        DataFrame with search results and user information
    """
    try:
        # Initialize embedding model
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Generate query embedding
        query_vector = model.encode(query_text).tolist()
        
        # Open tables
        documents_table = db.open_table("documents")
        users_table = db.open_table("users")
        
        # Perform vector search
        results = documents_table.search(query_vector).limit(limit).to_pandas()
        
        # Get user information
        users_df = users_table.to_pandas()
        
        # Join with user info
        results_with_users = results.merge(
            users_df[['user_id', 'name', 'email']], 
            on='user_id', 
            how='left'
        )
        
        print(f"\nVector search results for: '{query_text}'")
        print(f"Found {len(results_with_users)} results")
        
        return results_with_users
        
    except Exception as e:
        print(f"Error performing vector search with user info: {e}")
        raise


def get_user_statistics(db: lancedb.DBConnection) -> pd.DataFrame:
    """Get statistics about documents per user.
    
    Args:
        db: LanceDB connection
        
    Returns:
        DataFrame with user statistics
    """
    try:
        users_table = db.open_table("users")
        documents_table = db.open_table("documents")
        
        users_df = users_table.to_pandas()
        documents_df = documents_table.to_pandas()
        
        # Count documents per user
        doc_counts = documents_df.groupby('user_id').size().reset_index(name='document_count')
        
        # Join with user info
        stats = users_df.merge(doc_counts, on='user_id', how='left')
        stats['document_count'] = stats['document_count'].fillna(0).astype(int)
        
        print("\nUser Statistics:")
        print(stats[['user_id', 'name', 'email', 'document_count']])
        
        return stats
        
    except Exception as e:
        print(f"Error getting user statistics: {e}")
        raise


def main():
    """Main function demonstrating multi-table operations."""
    try:
        # Connect to LanceDB
        db = lancedb.connect("./lancedb_multi_table")
        print("Connected to LanceDB")
        
        # Create related tables
        print("\n=== Creating Related Tables ===")
        users_table, documents_table = create_related_tables(db)
        
        # Query documents for a specific user
        print("\n=== Join Query: Documents for User u1 ===")
        user_docs = join_query(db, "u1")
        if not user_docs.empty:
            print(user_docs[['doc_id', 'text', 'name', 'email']])
        
        # Query documents for another user
        print("\n=== Join Query: Documents for User u2 ===")
        user_docs = join_query(db, "u2")
        if not user_docs.empty:
            print(user_docs[['doc_id', 'text', 'name', 'email']])
        
        # Perform vector search with user info
        print("\n=== Vector Search with User Info ===")
        search_results = vector_search_with_user_info(
            db, 
            "neural networks and deep learning", 
            limit=3
        )
        if not search_results.empty:
            print(search_results[['doc_id', 'text', 'name', '_distance']])
        
        # Get user statistics
        print("\n=== User Statistics ===")
        stats = get_user_statistics(db)
        
        # Demonstrate querying non-existent user
        print("\n=== Query Non-existent User ===")
        join_query(db, "u999")
        
        print("\n=== Multi-table operations complete ===")
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    main()