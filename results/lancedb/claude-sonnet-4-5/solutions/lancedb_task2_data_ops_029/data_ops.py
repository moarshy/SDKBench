# filepath: data_ops.py
"""Multi-table schema with relationships."""

from typing import Optional, List, Dict, Any
import lancedb
from lancedb.pydantic import LanceModel, Vector
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer


# Define multiple related schemas
class User(LanceModel):
    """User schema with basic information."""
    user_id: str
    name: str
    email: str


class Document(LanceModel):
    """Document schema with vector embeddings and user reference."""
    doc_id: str
    text: str
    vector: Vector(384)  # Dimension for sentence-transformers/all-MiniLM-L6-v2
    user_id: str  # Foreign key to User


def create_related_tables(db: lancedb.DBConnection) -> tuple:
    """Create multiple related tables.
    
    Args:
        db: LanceDB connection
        
    Returns:
        Tuple of (users_table, documents_table)
        
    Raises:
        Exception: If table creation fails
    """
    try:
        # Create users table
        users_table = db.create_table(
            "users",
            schema=User,
            mode="overwrite"
        )
        print("✓ Created users table")
        
        # Create documents table with user_id reference
        documents_table = db.create_table(
            "documents",
            schema=Document,
            mode="overwrite"
        )
        print("✓ Created documents table")
        
        return users_table, documents_table
        
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        raise


def insert_sample_data(
    users_table,
    documents_table,
    embedding_model: SentenceTransformer
) -> None:
    """Insert sample data into related tables.
    
    Args:
        users_table: Users table
        documents_table: Documents table
        embedding_model: Model for generating embeddings
    """
    try:
        # Insert sample users
        users_data = [
            {"user_id": "u1", "name": "Alice Smith", "email": "alice@example.com"},
            {"user_id": "u2", "name": "Bob Johnson", "email": "bob@example.com"},
            {"user_id": "u3", "name": "Carol White", "email": "carol@example.com"}
        ]
        users_table.add(users_data)
        print(f"✓ Inserted {len(users_data)} users")
        
        # Insert sample documents with embeddings
        documents_text = [
            {"doc_id": "d1", "text": "Introduction to machine learning and AI", "user_id": "u1"},
            {"doc_id": "d2", "text": "Deep learning with neural networks", "user_id": "u1"},
            {"doc_id": "d3", "text": "Natural language processing techniques", "user_id": "u2"},
            {"doc_id": "d4", "text": "Computer vision and image recognition", "user_id": "u2"},
            {"doc_id": "d5", "text": "Reinforcement learning algorithms", "user_id": "u3"}
        ]
        
        # Generate embeddings for documents
        texts = [doc["text"] for doc in documents_text]
        embeddings = embedding_model.encode(texts)
        
        # Combine text data with embeddings
        documents_data = []
        for doc, embedding in zip(documents_text, embeddings):
            documents_data.append({
                "doc_id": doc["doc_id"],
                "text": doc["text"],
                "vector": embedding.tolist(),
                "user_id": doc["user_id"]
            })
        
        documents_table.add(documents_data)
        print(f"✓ Inserted {len(documents_data)} documents with embeddings")
        
    except Exception as e:
        print(f"✗ Error inserting data: {e}")
        raise


def join_query(
    db: lancedb.DBConnection,
    user_id: str
) -> pd.DataFrame:
    """Query documents with user info (simulated join).
    
    Args:
        db: LanceDB connection
        user_id: User ID to query documents for
        
    Returns:
        DataFrame with combined user and document information
        
    Raises:
        Exception: If query fails
    """
    try:
        # Open tables
        users_table = db.open_table("users")
        documents_table = db.open_table("documents")
        
        # Get user info
        users_df = users_table.to_pandas()
        user_info = users_df[users_df["user_id"] == user_id]
        
        if user_info.empty:
            print(f"✗ User {user_id} not found")
            return pd.DataFrame()
        
        # Get documents for user_id
        documents_df = documents_table.to_pandas()
        user_documents = documents_df[documents_df["user_id"] == user_id]
        
        if user_documents.empty:
            print(f"✓ No documents found for user {user_id}")
            return pd.DataFrame()
        
        # Perform join (merge)
        result = user_documents.merge(
            user_info[["user_id", "name", "email"]],
            on="user_id",
            how="left"
        )
        
        print(f"✓ Found {len(result)} documents for user {user_id}")
        return result
        
    except Exception as e:
        print(f"✗ Error in join query: {e}")
        raise


def vector_search_with_user(
    db: lancedb.DBConnection,
    query_text: str,
    embedding_model: SentenceTransformer,
    limit: int = 3
) -> pd.DataFrame:
    """Perform vector search and include user information.
    
    Args:
        db: LanceDB connection
        query_text: Text to search for
        embedding_model: Model for generating query embedding
        limit: Number of results to return
        
    Returns:
        DataFrame with search results and user information
    """
    try:
        # Open tables
        users_table = db.open_table("users")
        documents_table = db.open_table("documents")
        
        # Generate query embedding
        query_vector = embedding_model.encode(query_text)
        
        # Perform vector search
        results = (
            documents_table
            .search(query_vector)
            .limit(limit)
            .to_pandas()
        )
        
        if results.empty:
            print("✓ No search results found")
            return pd.DataFrame()
        
        # Get user information
        users_df = users_table.to_pandas()
        
        # Join with user info
        results_with_users = results.merge(
            users_df[["user_id", "name", "email"]],
            on="user_id",
            how="left"
        )
        
        print(f"✓ Found {len(results_with_users)} relevant documents")
        return results_with_users
        
    except Exception as e:
        print(f"✗ Error in vector search: {e}")
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
        doc_counts = documents_df.groupby("user_id").size().reset_index(name="document_count")
        
        # Join with user info
        stats = users_df.merge(doc_counts, on="user_id", how="left")
        stats["document_count"] = stats["document_count"].fillna(0).astype(int)
        
        print("✓ Generated user statistics")
        return stats
        
    except Exception as e:
        print(f"✗ Error generating statistics: {e}")
        raise


def main():
    """Main function demonstrating multi-table operations."""
    print("=" * 60)
    print("Multi-table Schema with Relationships Demo")
    print("=" * 60)
    
    try:
        # Initialize embedding model
        print("\n1. Loading embedding model...")
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("✓ Model loaded")
        
        # Connect to database
        print("\n2. Connecting to database...")
        db = lancedb.connect("./lancedb_multi_table")
        print("✓ Connected to database")
        
        # Create related tables
        print("\n3. Creating related tables...")
        users_table, documents_table = create_related_tables(db)
        
        # Insert related data
        print("\n4. Inserting sample data...")
        insert_sample_data(users_table, documents_table, model)
        
        # Query with join - get all documents for a user
        print("\n5. Querying documents for user 'u1'...")
        user_docs = join_query(db, "u1")
        if not user_docs.empty:
            print("\nDocuments for Alice Smith:")
            for _, row in user_docs.iterrows():
                print(f"  - {row['doc_id']}: {row['text']}")
                print(f"    Email: {row['email']}")
        
        # Vector search with user info
        print("\n6. Performing vector search with user info...")
        query = "neural networks and deep learning"
        print(f"Query: '{query}'")
        search_results = vector_search_with_user(db, query, model, limit=3)
        if not search_results.empty:
            print("\nTop results:")
            for idx, row in search_results.iterrows():
                print(f"  {idx + 1}. {row['text']}")
                print(f"     Author: {row['name']} ({row['email']})")
                print(f"     Distance: {row.get('_distance', 'N/A'):.4f}")
        
        # Get user statistics
        print("\n7. Generating user statistics...")
        stats = get_user_statistics(db)
        print("\nUser Statistics:")
        print(stats[["name", "email", "document_count"]].to_string(index=False))
        
        # Query documents for another user
        print("\n8. Querying documents for user 'u2'...")
        user_docs_2 = join_query(db, "u2")
        if not user_docs_2.empty:
            print("\nDocuments for Bob Johnson:")
            for _, row in user_docs_2.iterrows():
                print(f"  - {row['doc_id']}: {row['text']}")
        
        print("\n" + "=" * 60)
        print("Multi-table operations complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error in main: {e}")
        raise


if __name__ == "__main__":
    main()