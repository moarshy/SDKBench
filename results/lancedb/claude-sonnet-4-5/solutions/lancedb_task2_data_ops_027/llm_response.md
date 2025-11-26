```txt
# filepath: requirements.txt
pandas>=2.0.0
numpy>=1.24.0
lancedb>=0.5.0
pylance>=0.9.0
```

```python
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
    try:
        # Get current UTC time
        current_time = get_current_timestamp()
        
        # Generate a simple ID based on timestamp
        doc_id = f"doc_{datetime.now(timezone.utc).timestamp()}"
        
        # Return document dict with timestamp
        return {
            "id": doc_id,
            "text": text,
            "vector": vector,
            "created_at": current_time,
            "updated_at": None
        }
    except Exception as e:
        raise ValueError(f"Error creating document: {str(e)}")

def update_document(table, doc_id: str, updates: dict):
    """Update document with updated_at timestamp.
    
    Args:
        table: LanceDB table instance
        doc_id: ID of document to update
        updates: Dictionary of fields to update
        
    Returns:
        Updated document
    """
    try:
        # Set updated_at to current time
        updates["updated_at"] = get_current_timestamp()
        
        # Get existing document
        results = table.search().where(f"id = '{doc_id}'").limit(1).to_pandas()
        
        if len(results) == 0:
            raise ValueError(f"Document with id '{doc_id}' not found")
        
        # Get the existing document data
        existing_doc = results.iloc[0].to_dict()
        
        # Apply updates while preserving other fields
        for key, value in updates.items():
            if key in existing_doc:
                existing_doc[key] = value
        
        # Delete old document and insert updated one
        table.delete(f"id = '{doc_id}'")
        table.add([existing_doc])
        
        return existing_doc
    except Exception as e:
        raise ValueError(f"Error updating document: {str(e)}")

def main():
    """Main function demonstrating timestamp handling."""
    try:
        # Connect to LanceDB
        db = lancedb.connect("./lancedb_timestamps")
        
        # Create sample vectors (384 dimensions)
        vector1 = np.random.randn(384).tolist()
        vector2 = np.random.randn(384).tolist()
        
        # Create documents with timestamps
        print("Creating documents with automatic timestamps...")
        doc1 = create_document("First document", vector1)
        doc2 = create_document("Second document", vector2)
        
        print(f"Document 1 created at: {doc1['created_at']}")
        print(f"Document 2 created at: {doc2['created_at']}")
        
        # Create table with documents
        table_name = "documents_with_timestamps"
        
        # Drop table if it exists
        try:
            db.drop_table(table_name)
        except:
            pass
        
        # Create new table
        table = db.create_table(table_name, data=[doc1, doc2], schema=Document)
        print(f"\nCreated table '{table_name}' with {len(table)} documents")
        
        # Display initial documents
        print("\nInitial documents:")
        df = table.to_pandas()
        for idx, row in df.iterrows():
            print(f"  ID: {row['id']}")
            print(f"  Text: {row['text']}")
            print(f"  Created: {row['created_at']}")
            print(f"  Updated: {row['updated_at']}")
            print()
        
        # Wait a moment to ensure different timestamp
        import time
        time.sleep(0.1)
        
        # Update first document
        print("Updating first document...")
        doc1_id = doc1['id']
        updated_doc = update_document(
            table, 
            doc1_id, 
            {"text": "Updated first document"}
        )
        
        print(f"Document updated at: {updated_doc['updated_at']}")
        
        # Verify timestamps
        print("\nFinal documents:")
        df = table.to_pandas()
        for idx, row in df.iterrows():
            print(f"  ID: {row['id']}")
            print(f"  Text: {row['text']}")
            print(f"  Created: {row['created_at']}")
            print(f"  Updated: {row['updated_at']}")
            
            # Verify timestamp format
            try:
                created = datetime.fromisoformat(row['created_at'])
                print(f"  ✓ Valid created_at timestamp")
                
                if row['updated_at']:
                    updated = datetime.fromisoformat(row['updated_at'])
                    print(f"  ✓ Valid updated_at timestamp")
                    
                    # Verify updated_at is after created_at
                    if updated > created:
                        print(f"  ✓ updated_at is after created_at")
            except Exception as e:
                print(f"  ✗ Invalid timestamp: {e}")
            print()
        
        print("Timestamp handling complete")
        
    except Exception as e:
        print(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()
```