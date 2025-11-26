# filepath: data_ops.py
"""Upsert/update existing data."""

import lancedb
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import pyarrow as pa


def upsert_documents(db: lancedb.DBConnection, table_name: str, documents: List[Dict[str, Any]]) -> None:
    """Upsert documents (update if exists, insert if not).
    
    Args:
        db: LanceDB connection
        table_name: Name of the table
        documents: List of documents to upsert
        
    Raises:
        ValueError: If documents list is empty or invalid
        Exception: If upsert operation fails
    """
    if not documents:
        raise ValueError("Documents list cannot be empty")
    
    try:
        # Convert documents to DataFrame
        df = pd.DataFrame(documents)
        
        # Check if table exists
        table_names = db.table_names()
        
        if table_name in table_names:
            # Table exists - use merge_insert for upsert
            table = db.open_table(table_name)
            
            # merge_insert will update existing records and insert new ones
            # based on the primary key (typically 'id')
            table.merge_insert("id") \
                .when_matched_update_all() \
                .when_not_matched_insert_all() \
                .execute(df)
            
            print(f"Upserted {len(documents)} documents to table '{table_name}'")
        else:
            # Table doesn't exist - create it
            db.create_table(table_name, df)
            print(f"Created table '{table_name}' with {len(documents)} documents")
            
    except Exception as e:
        print(f"Error during upsert: {str(e)}")
        raise


def update_document(table: lancedb.table.Table, doc_id: str, updates: Dict[str, Any]) -> bool:
    """Update specific document by ID.
    
    Args:
        table: LanceDB table instance
        doc_id: Document ID to update
        updates: Dictionary of field updates
        
    Returns:
        bool: True if update successful, False otherwise
        
    Raises:
        ValueError: If doc_id or updates are invalid
    """
    if not doc_id:
        raise ValueError("Document ID cannot be empty")
    
    if not updates:
        raise ValueError("Updates dictionary cannot be empty")
    
    try:
        # Search for the document by ID
        results = table.search().where(f"id = '{doc_id}'").limit(1).to_pandas()
        
        if results.empty:
            print(f"Document with ID '{doc_id}' not found")
            return False
        
        # Get the existing document
        existing_doc = results.iloc[0].to_dict()
        
        # Apply updates
        for key, value in updates.items():
            existing_doc[key] = value
        
        # Create a DataFrame with the updated document
        updated_df = pd.DataFrame([existing_doc])
        
        # Use merge_insert to update the document
        table.merge_insert("id") \
            .when_matched_update_all() \
            .execute(updated_df)
        
        print(f"Successfully updated document '{doc_id}'")
        return True
        
    except Exception as e:
        print(f"Error updating document: {str(e)}")
        return False


def batch_update_documents(table: lancedb.table.Table, updates: List[Dict[str, Any]]) -> int:
    """Batch update multiple documents.
    
    Args:
        table: LanceDB table instance
        updates: List of documents with updates (must include 'id' field)
        
    Returns:
        int: Number of documents successfully updated
    """
    if not updates:
        raise ValueError("Updates list cannot be empty")
    
    try:
        # Verify all updates have an 'id' field
        for update in updates:
            if 'id' not in update:
                raise ValueError("All updates must include an 'id' field")
        
        # Convert to DataFrame
        updates_df = pd.DataFrame(updates)
        
        # Perform batch update using merge_insert
        table.merge_insert("id") \
            .when_matched_update_all() \
            .when_not_matched_insert_all() \
            .execute(updates_df)
        
        print(f"Successfully batch updated {len(updates)} documents")
        return len(updates)
        
    except Exception as e:
        print(f"Error during batch update: {str(e)}")
        raise


def delete_document(table: lancedb.table.Table, doc_id: str) -> bool:
    """Delete a specific document by ID.
    
    Args:
        table: LanceDB table instance
        doc_id: Document ID to delete
        
    Returns:
        bool: True if deletion successful, False otherwise
    """
    try:
        # Delete using SQL-like syntax
        table.delete(f"id = '{doc_id}'")
        print(f"Successfully deleted document '{doc_id}'")
        return True
        
    except Exception as e:
        print(f"Error deleting document: {str(e)}")
        return False


def main():
    """Demonstrate upsert and update operations."""
    
    # Connect to LanceDB
    db = lancedb.connect("./lancedb_data")
    table_name = "documents"
    
    print("=== Initial Data Creation ===")
    # Create initial documents with vectors
    initial_documents = [
        {
            "id": "doc1",
            "text": "Machine learning is a subset of artificial intelligence",
            "vector": np.random.rand(128).tolist(),
            "category": "AI",
            "score": 0.85
        },
        {
            "id": "doc2",
            "text": "Deep learning uses neural networks",
            "vector": np.random.rand(128).tolist(),
            "category": "AI",
            "score": 0.90
        },
        {
            "id": "doc3",
            "text": "Natural language processing enables text understanding",
            "vector": np.random.rand(128).tolist(),
            "category": "NLP",
            "score": 0.88
        }
    ]
    
    # Initial insert
    upsert_documents(db, table_name, initial_documents)
    
    # Open the table
    table = db.open_table(table_name)
    
    print("\n=== Display Initial Data ===")
    df = table.to_pandas()
    print(df[["id", "text", "category", "score"]])
    
    print("\n=== Single Document Update ===")
    # Update a single document
    update_document(table, "doc1", {
        "text": "Machine learning is a powerful subset of artificial intelligence",
        "score": 0.92
    })
    
    print("\n=== Upsert with New and Updated Documents ===")
    # Upsert: update existing and add new documents
    upsert_data = [
        {
            "id": "doc2",  # Existing - will be updated
            "text": "Deep learning uses multi-layer neural networks",
            "vector": np.random.rand(128).tolist(),
            "category": "Deep Learning",
            "score": 0.95
        },
        {
            "id": "doc4",  # New - will be inserted
            "text": "Computer vision enables image recognition",
            "vector": np.random.rand(128).tolist(),
            "category": "CV",
            "score": 0.87
        }
    ]
    
    upsert_documents(db, table_name, upsert_data)
    
    print("\n=== Batch Update ===")
    # Batch update multiple documents
    batch_updates = [
        {"id": "doc1", "score": 0.93},
        {"id": "doc3", "score": 0.91}
    ]
    
    batch_update_documents(table, batch_updates)
    
    print("\n=== Final Data State ===")
    df_final = table.to_pandas()
    print(df_final[["id", "text", "category", "score"]])
    
    print("\n=== Delete Document ===")
    delete_document(table, "doc4")
    
    print("\n=== Data After Deletion ===")
    df_after_delete = table.to_pandas()
    print(df_after_delete[["id", "text", "category", "score"]])
    
    print("\nUpsert and update operations complete!")


if __name__ == "__main__":
    main()