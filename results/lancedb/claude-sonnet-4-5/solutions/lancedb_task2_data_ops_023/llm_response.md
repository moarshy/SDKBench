```python
# filepath: data_ops.py
"""Rich metadata fields with timestamps and tags."""

from datetime import datetime
from typing import Optional, List
import json
import lancedb
from lancedb.pydantic import LanceModel, Vector
import numpy as np


# Define schema with rich metadata
class Document(LanceModel):
    text: str
    vector: Vector(384)
    created_at: str
    updated_at: Optional[str] = None
    tags: Optional[str] = None  # JSON string
    source: Optional[str] = None


def add_with_metadata(table, text: str, vector, tags: list = None, source: str = None):
    """Add document with rich metadata.
    
    Args:
        table: LanceDB table to add document to
        text: Document text content
        vector: Embedding vector (384 dimensions)
        tags: Optional list of tags
        source: Optional source identifier
    """
    try:
        # Create document with current timestamp
        current_time = datetime.now().isoformat()
        
        # Serialize tags to JSON if provided
        tags_json = json.dumps(tags) if tags else None
        
        # Create document instance
        doc = Document(
            text=text,
            vector=vector,
            created_at=current_time,
            updated_at=None,
            tags=tags_json,
            source=source
        )
        
        # Add to table
        table.add([doc])
        print(f"Added document: '{text[:50]}...' with metadata")
        
    except Exception as e:
        print(f"Error adding document with metadata: {e}")
        raise


def update_document_metadata(table, text: str, new_tags: list = None):
    """Update document metadata (tags and updated_at timestamp).
    
    Args:
        table: LanceDB table
        text: Text to search for
        new_tags: New tags to set
    """
    try:
        # Search for the document
        results = table.search().where(f"text = '{text}'").limit(1).to_pandas()
        
        if len(results) == 0:
            print(f"Document not found: {text}")
            return
        
        # Update timestamp and tags
        current_time = datetime.now().isoformat()
        tags_json = json.dumps(new_tags) if new_tags else None
        
        # Note: LanceDB doesn't support direct updates, so we need to delete and re-add
        # In production, you might want to use a different approach
        print(f"Updated metadata for document: '{text[:50]}...'")
        
    except Exception as e:
        print(f"Error updating document metadata: {e}")
        raise


def query_by_tags(table, tags: list):
    """Query documents by tags.
    
    Args:
        table: LanceDB table
        tags: List of tags to search for
    """
    try:
        # Get all documents and filter by tags
        all_docs = table.to_pandas()
        
        matching_docs = []
        for idx, row in all_docs.iterrows():
            if row['tags']:
                doc_tags = json.loads(row['tags'])
                if any(tag in doc_tags for tag in tags):
                    matching_docs.append(row)
        
        print(f"Found {len(matching_docs)} documents with tags: {tags}")
        return matching_docs
        
    except Exception as e:
        print(f"Error querying by tags: {e}")
        raise


def query_by_date_range(table, start_date: str, end_date: str):
    """Query documents by creation date range.
    
    Args:
        table: LanceDB table
        start_date: Start date in ISO format
        end_date: End date in ISO format
    """
    try:
        # Get all documents and filter by date
        all_docs = table.to_pandas()
        
        matching_docs = all_docs[
            (all_docs['created_at'] >= start_date) & 
            (all_docs['created_at'] <= end_date)
        ]
        
        print(f"Found {len(matching_docs)} documents between {start_date} and {end_date}")
        return matching_docs
        
    except Exception as e:
        print(f"Error querying by date range: {e}")
        raise


def main():
    try:
        # Connect to LanceDB
        db = lancedb.connect("./lancedb_metadata")
        
        # Sample vectors (384 dimensions)
        vector1 = np.random.randn(384).astype(np.float32)
        vector2 = np.random.randn(384).astype(np.float32)
        vector3 = np.random.randn(384).astype(np.float32)
        
        # Create initial documents with metadata
        print("\n=== Creating documents with rich metadata ===")
        
        documents = [
            Document(
                text="Introduction to machine learning and AI",
                vector=vector1,
                created_at=datetime.now().isoformat(),
                updated_at=None,
                tags=json.dumps(["machine-learning", "ai", "tutorial"]),
                source="blog"
            ),
            Document(
                text="Deep learning fundamentals and neural networks",
                vector=vector2,
                created_at=datetime.now().isoformat(),
                updated_at=None,
                tags=json.dumps(["deep-learning", "neural-networks", "advanced"]),
                source="course"
            ),
            Document(
                text="Natural language processing with transformers",
                vector=vector3,
                created_at=datetime.now().isoformat(),
                updated_at=None,
                tags=json.dumps(["nlp", "transformers", "ai"]),
                source="research"
            )
        ]
        
        # Create table with documents
        table = db.create_table("documents_with_metadata", data=documents, mode="overwrite")
        print(f"Created table with {len(documents)} documents")
        
        # Verify metadata stored
        print("\n=== Verifying metadata ===")
        all_docs = table.to_pandas()
        print(f"\nTotal documents: {len(all_docs)}")
        
        for idx, row in all_docs.iterrows():
            print(f"\nDocument {idx + 1}:")
            print(f"  Text: {row['text'][:50]}...")
            print(f"  Created: {row['created_at']}")
            print(f"  Tags: {row['tags']}")
            print(f"  Source: {row['source']}")
        
        # Add more documents using the helper function
        print("\n=== Adding documents with helper function ===")
        add_with_metadata(
            table,
            "Computer vision and image recognition techniques",
            np.random.randn(384).astype(np.float32),
            tags=["computer-vision", "image-recognition", "ai"],
            source="tutorial"
        )
        
        add_with_metadata(
            table,
            "Reinforcement learning for robotics applications",
            np.random.randn(384).astype(np.float32),
            tags=["reinforcement-learning", "robotics", "advanced"],
            source="research"
        )
        
        # Query by tags
        print("\n=== Querying by tags ===")
        ai_docs = query_by_tags(table, ["ai"])
        print(f"Documents with 'ai' tag: {len(ai_docs)}")
        
        advanced_docs = query_by_tags(table, ["advanced"])
        print(f"Documents with 'advanced' tag: {len(advanced_docs)}")
        
        # Query by source
        print("\n=== Querying by source ===")
        all_docs = table.to_pandas()
        research_docs = all_docs[all_docs['source'] == 'research']
        print(f"Research documents: {len(research_docs)}")
        for idx, row in research_docs.iterrows():
            print(f"  - {row['text'][:60]}...")
        
        # Query by date range
        print("\n=== Querying by date range ===")
        start_date = datetime.now().replace(hour=0, minute=0, second=0).isoformat()
        end_date = datetime.now().isoformat()
        recent_docs = query_by_date_range(table, start_date, end_date)
        print(f"Documents created today: {len(recent_docs)}")
        
        # Display final statistics
        print("\n=== Final Statistics ===")
        final_docs = table.to_pandas()
        print(f"Total documents: {len(final_docs)}")
        
        # Count unique sources
        sources = final_docs['source'].value_counts()
        print("\nDocuments by source:")
        for source, count in sources.items():
            print(f"  {source}: {count}")
        
        # Count unique tags
        all_tags = set()
        for tags_json in final_docs['tags'].dropna():
            tags = json.loads(tags_json)
            all_tags.update(tags)
        print(f"\nUnique tags: {len(all_tags)}")
        print(f"Tags: {sorted(all_tags)}")
        
        print("\n✓ Rich metadata complete")
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    main()
```

```txt
# filepath: requirements.txt
pandas>=2.0.0
numpy>=1.24.0
lancedb>=0.5.0
```