# filepath: data_ops.py
"""Automatic timestamp handling."""

from datetime import datetime, timezone
from typing import Optional
import lancedb
from lancedb.pydantic import LanceModel, Vector
import numpy as np

# Define schema with timestamps
class Document(LanceModel):
    id: str
    text: str
    vector: Vector(384)
    created_at: str
    updated_at: Optional[str] = None

def get_current_timestamp() -> str:
    """Get current UTC timestamp as ISO string."""
    return datetime.now(timezone.utc).isoformat()

def create_document(text: str, vector) -> dict:
    """Create document with auto timestamp.
    
    Args:
        text: Document text content
        vector: Document embedding vector
        
    Returns:
        Dictionary with document data including timestamp
    """
    current_time = get_current_timestamp()
    
    # Generate a simple ID based on timestamp and text hash
    doc_id = f"doc_{hash(text + current_time) % 1000000}"
    
    return {
        "id": doc_id,
        "text": text,
        "vector": vector,
        "created_at": current_time,
        "updated_at": None
    }

def update_document(table, doc_id: str, updates: dict):
    """Update document with updated_at timestamp.
    
    Args:
        table: LanceDB table instance
        doc_id: Document ID to update
        updates: Dictionary of fields to update
        
    Returns:
        Updated document or None if not found
    """
    try:
        # Add updated_at timestamp to updates
        updates["updated_at"] = get_current_timestamp()
        
        # Search for the document by ID
        results = table.search().where(f"id = '{doc_id}'").limit(1).to_pandas()
        
        if len(results) == 0:
            print(f"Document with ID {doc_id} not found")
            return None
        
        # Get the existing document
        existing_doc = results.iloc[0].to_dict()
        
        # Update fields
        for key, value in updates.items():
            if key in existing_doc:
                existing_doc[key] = value
        
        # Delete old document and insert updated one
        table.delete(f"id = '{doc_id}'")
        table.add([existing_doc])
        
        print(f"Document {doc_id} updated at {updates['updated_at']}")
        return existing_doc
        
    except Exception as e:
        print(f"Error updating document: {e}")
        return None

def main():
    """Main function demonstrating timestamp handling."""
    try:
        # Connect to LanceDB
        db = lancedb.connect("./timestamp_demo")
        
        # Create sample documents with timestamps
        print("Creating documents with automatic timestamps...")
        
        # Generate sample vectors (384 dimensions)
        vector1 = np.random.randn(384).tolist()
        vector2 = np.random.randn(384).tolist()
        vector3 = np.random.randn(384).tolist()
        
        doc1 = create_document("First document about AI", vector1)
        doc2 = create_document("Second document about machine learning", vector2)
        doc3 = create_document("Third document about data science", vector3)
        
        print(f"\nCreated documents:")
        print(f"Doc 1 ID: {doc1['id']}, Created: {doc1['created_at']}")
        print(f"Doc 2 ID: {doc2['id']}, Created: {doc2['created_at']}")
        print(f"Doc 3 ID: {doc3['id']}, Created: {doc3['created_at']}")
        
        # Create table with documents
        documents = [doc1, doc2, doc3]
        
        # Drop table if exists
        try:
            db.drop_table("documents")
        except:
            pass
        
        table = db.create_table("documents", data=documents, schema=Document)
        print(f"\nCreated table with {len(documents)} documents")
        
        # Display all documents
        all_docs = table.search().limit(10).to_pandas()
        print("\nAll documents in table:")
        print(all_docs[['id', 'text', 'created_at', 'updated_at']])
        
        # Update a document
        print(f"\nUpdating document {doc1['id']}...")
        import time
        time.sleep(1)  # Small delay to show different timestamp
        
        updated_doc = update_document(
            table, 
            doc1['id'], 
            {"text": "Updated: First document about AI and ML"}
        )
        
        if updated_doc:
            print(f"Updated document:")
            print(f"  ID: {updated_doc['id']}")
            print(f"  Text: {updated_doc['text']}")
            print(f"  Created: {updated_doc['created_at']}")
            print(f"  Updated: {updated_doc['updated_at']}")
        
        # Verify the update
        print("\nVerifying update in table...")
        updated_results = table.search().where(f"id = '{doc1['id']}'").limit(1).to_pandas()
        
        if len(updated_results) > 0:
            result = updated_results.iloc[0]
            print(f"  Text: {result['text']}")
            print(f"  Created: {result['created_at']}")
            print(f"  Updated: {result['updated_at']}")
            
            # Verify timestamps are different
            if result['updated_at'] and result['updated_at'] != result['created_at']:
                print("\n✓ Timestamps correctly show creation and update times")
            else:
                print("\n✗ Warning: Timestamps may not be properly set")
        
        # Update another document
        print(f"\nUpdating document {doc2['id']}...")
        time.sleep(1)
        
        update_document(
            table,
            doc2['id'],
            {"text": "Updated: Second document about ML and deep learning"}
        )
        
        # Show final state of all documents
        print("\nFinal state of all documents:")
        final_docs = table.search().limit(10).to_pandas()
        print(final_docs[['id', 'text', 'created_at', 'updated_at']])
        
        # Count documents with updates
        updated_count = final_docs['updated_at'].notna().sum()
        print(f"\nDocuments with updates: {updated_count}/{len(final_docs)}")
        
        print("\n✓ Timestamp handling complete")
        
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()