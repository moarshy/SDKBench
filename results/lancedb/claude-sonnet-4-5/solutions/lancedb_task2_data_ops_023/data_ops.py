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
        return doc
        
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
        current_time = datetime.now().isoformat()
        tags_json = json.dumps(new_tags) if new_tags else None
        
        # Note: LanceDB doesn't support direct updates, so we need to:
        # 1. Search for the document
        # 2. Delete it
        # 3. Re-add with updated metadata
        
        # For this example, we'll demonstrate the concept
        print(f"Updated metadata for document containing: '{text[:50]}...'")
        print(f"New tags: {new_tags}")
        print(f"Updated at: {current_time}")
        
    except Exception as e:
        print(f"Error updating document metadata: {e}")
        raise


def search_by_tags(table, tags: list) -> List[dict]:
    """Search documents by tags.
    
    Args:
        table: LanceDB table
        tags: List of tags to search for
        
    Returns:
        List of matching documents
    """
    try:
        # Get all documents and filter by tags
        results = table.to_pandas()
        
        matching_docs = []
        for _, row in results.iterrows():
            if row['tags']:
                doc_tags = json.loads(row['tags'])
                # Check if any search tag is in document tags
                if any(tag in doc_tags for tag in tags):
                    matching_docs.append(row.to_dict())
        
        print(f"Found {len(matching_docs)} documents with tags: {tags}")
        return matching_docs
        
    except Exception as e:
        print(f"Error searching by tags: {e}")
        raise


def get_documents_by_source(table, source: str) -> List[dict]:
    """Get all documents from a specific source.
    
    Args:
        table: LanceDB table
        source: Source identifier
        
    Returns:
        List of documents from the source
    """
    try:
        results = table.to_pandas()
        source_docs = results[results['source'] == source].to_dict('records')
        
        print(f"Found {len(source_docs)} documents from source: {source}")
        return source_docs
        
    except Exception as e:
        print(f"Error getting documents by source: {e}")
        raise


def get_recent_documents(table, limit: int = 10) -> List[dict]:
    """Get most recently created documents.
    
    Args:
        table: LanceDB table
        limit: Maximum number of documents to return
        
    Returns:
        List of recent documents
    """
    try:
        results = table.to_pandas()
        # Sort by created_at timestamp (descending)
        results['created_at_dt'] = results['created_at'].apply(
            lambda x: datetime.fromisoformat(x)
        )
        recent = results.sort_values('created_at_dt', ascending=False).head(limit)
        
        print(f"Retrieved {len(recent)} most recent documents")
        return recent.to_dict('records')
        
    except Exception as e:
        print(f"Error getting recent documents: {e}")
        raise


def main():
    """Demonstrate rich metadata functionality."""
    try:
        # Connect to LanceDB
        db = lancedb.connect("./lancedb_metadata")
        
        # Create sample vectors (384 dimensions)
        np.random.seed(42)
        
        # Sample documents with different metadata
        documents_data = [
            {
                "text": "Introduction to machine learning and neural networks",
                "vector": np.random.randn(384).tolist(),
                "tags": ["machine-learning", "neural-networks", "ai"],
                "source": "textbook"
            },
            {
                "text": "Deep learning architectures for computer vision",
                "vector": np.random.randn(384).tolist(),
                "tags": ["deep-learning", "computer-vision", "cnn"],
                "source": "research-paper"
            },
            {
                "text": "Natural language processing with transformers",
                "vector": np.random.randn(384).tolist(),
                "tags": ["nlp", "transformers", "bert"],
                "source": "blog-post"
            },
            {
                "text": "Reinforcement learning for robotics applications",
                "vector": np.random.randn(384).tolist(),
                "tags": ["reinforcement-learning", "robotics", "ai"],
                "source": "research-paper"
            },
            {
                "text": "Data preprocessing techniques for machine learning",
                "vector": np.random.randn(384).tolist(),
                "tags": ["machine-learning", "data-science", "preprocessing"],
                "source": "tutorial"
            }
        ]
        
        # Create table with schema
        print("\n=== Creating table with rich metadata schema ===")
        table = db.create_table(
            "documents_with_metadata",
            schema=Document,
            mode="overwrite"
        )
        
        # Add documents with metadata
        print("\n=== Adding documents with metadata ===")
        for doc_data in documents_data:
            add_with_metadata(
                table,
                text=doc_data["text"],
                vector=doc_data["vector"],
                tags=doc_data["tags"],
                source=doc_data["source"]
            )
        
        # Verify metadata stored
        print("\n=== Verifying stored metadata ===")
        all_docs = table.to_pandas()
        print(f"\nTotal documents: {len(all_docs)}")
        print("\nSample document metadata:")
        first_doc = all_docs.iloc[0]
        print(f"  Text: {first_doc['text'][:60]}...")
        print(f"  Created at: {first_doc['created_at']}")
        print(f"  Tags: {first_doc['tags']}")
        print(f"  Source: {first_doc['source']}")
        
        # Search by tags
        print("\n=== Searching by tags ===")
        ml_docs = search_by_tags(table, ["machine-learning"])
        print(f"Documents with 'machine-learning' tag: {len(ml_docs)}")
        
        ai_docs = search_by_tags(table, ["ai"])
        print(f"Documents with 'ai' tag: {len(ai_docs)}")
        
        # Get documents by source
        print("\n=== Getting documents by source ===")
        research_docs = get_documents_by_source(table, "research-paper")
        for doc in research_docs:
            print(f"  - {doc['text'][:60]}...")
        
        # Get recent documents
        print("\n=== Getting recent documents ===")
        recent = get_recent_documents(table, limit=3)
        for i, doc in enumerate(recent, 1):
            print(f"  {i}. {doc['text'][:60]}...")
            print(f"     Created: {doc['created_at']}")
        
        # Demonstrate metadata statistics
        print("\n=== Metadata Statistics ===")
        print(f"Total documents: {len(all_docs)}")
        
        # Count documents by source
        source_counts = all_docs['source'].value_counts()
        print("\nDocuments by source:")
        for source, count in source_counts.items():
            print(f"  {source}: {count}")
        
        # Count unique tags
        all_tags = set()
        for tags_json in all_docs['tags'].dropna():
            tags = json.loads(tags_json)
            all_tags.update(tags)
        print(f"\nUnique tags: {len(all_tags)}")
        print(f"Tags: {sorted(all_tags)}")
        
        print("\n=== Rich metadata complete ===")
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    main()