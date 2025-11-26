# filepath: data_ops.py
"""JSON metadata storage pattern."""

import json
from typing import Optional
import lancedb
from lancedb.pydantic import LanceModel, Vector
import numpy as np


# Define schema with JSON metadata field
class Document(LanceModel):
    text: str
    vector: Vector(384)
    metadata_json: Optional[str] = None  # Store as JSON string


def add_with_json_metadata(table, text: str, vector, metadata: dict):
    """Add document with JSON metadata.

    Args:
        table: LanceDB table instance
        text: Document text content
        vector: Embedding vector (384 dimensions)
        metadata: Dictionary of metadata to store as JSON
    
    Raises:
        ValueError: If vector dimensions don't match schema
        json.JSONEncodeError: If metadata cannot be serialized
    """
    try:
        # Validate vector dimensions
        vector_array = np.array(vector)
        if vector_array.shape[0] != 384:
            raise ValueError(f"Vector must have 384 dimensions, got {vector_array.shape[0]}")
        
        # Serialize metadata to JSON string
        metadata_json_str = json.dumps(metadata)
        
        # Create document
        document = Document(
            text=text,
            vector=vector_array.tolist(),
            metadata_json=metadata_json_str
        )
        
        # Add to table
        table.add([document])
        print(f"Added document: '{text[:50]}...' with metadata")
        
    except json.JSONEncodeError as e:
        print(f"Error serializing metadata to JSON: {e}")
        raise
    except Exception as e:
        print(f"Error adding document: {e}")
        raise


def get_metadata(row) -> dict:
    """Parse JSON metadata from row.

    Args:
        row: A row from LanceDB query results
    
    Returns:
        Dictionary containing parsed metadata, or empty dict if parsing fails
    """
    try:
        # Get metadata_json field
        metadata_json_str = row.get('metadata_json') or row.get('metadata_json', None)
        
        # Handle case where metadata_json might be accessed as attribute
        if metadata_json_str is None and hasattr(row, 'metadata_json'):
            metadata_json_str = row.metadata_json
        
        # Return empty dict if no metadata
        if metadata_json_str is None or metadata_json_str == '':
            return {}
        
        # Parse JSON
        metadata_dict = json.loads(metadata_json_str)
        return metadata_dict
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON metadata: {e}")
        return {}
    except Exception as e:
        print(f"Error getting metadata: {e}")
        return {}


def main():
    """Main function demonstrating JSON metadata storage."""
    try:
        # Connect to LanceDB
        db = lancedb.connect("./lancedb_json_metadata")
        print("Connected to LanceDB")
        
        # Create table with schema
        table_name = "documents_with_json"
        
        # Drop table if exists (for clean demo)
        try:
            db.drop_table(table_name)
        except:
            pass
        
        # Create table
        table = db.create_table(table_name, schema=Document)
        print(f"Created table: {table_name}")
        
        # Add documents with nested metadata
        documents = [
            {
                "text": "Machine learning is a subset of artificial intelligence",
                "vector": np.random.rand(384).tolist(),
                "metadata": {
                    "author": "John Doe",
                    "category": "AI",
                    "tags": ["machine learning", "AI", "technology"],
                    "stats": {
                        "views": 1500,
                        "likes": 250
                    },
                    "published": "2024-01-15"
                }
            },
            {
                "text": "Deep learning uses neural networks with multiple layers",
                "vector": np.random.rand(384).tolist(),
                "metadata": {
                    "author": "Jane Smith",
                    "category": "Deep Learning",
                    "tags": ["deep learning", "neural networks", "AI"],
                    "stats": {
                        "views": 2300,
                        "likes": 450
                    },
                    "published": "2024-02-20"
                }
            },
            {
                "text": "Natural language processing enables computers to understand human language",
                "vector": np.random.rand(384).tolist(),
                "metadata": {
                    "author": "Bob Johnson",
                    "category": "NLP",
                    "tags": ["NLP", "language", "AI"],
                    "stats": {
                        "views": 1800,
                        "likes": 320
                    },
                    "published": "2024-03-10",
                    "featured": True
                }
            }
        ]
        
        # Add documents to table
        for doc in documents:
            add_with_json_metadata(
                table,
                doc["text"],
                doc["vector"],
                doc["metadata"]
            )
        
        print(f"\nAdded {len(documents)} documents with JSON metadata")
        
        # Query and parse metadata
        print("\n--- Querying documents ---")
        results = table.search(np.random.rand(384).tolist()).limit(3).to_pandas()
        
        print(f"\nFound {len(results)} documents:")
        for idx, row in results.iterrows():
            metadata = get_metadata(row)
            print(f"\n{idx + 1}. Text: {row['text'][:60]}...")
            print(f"   Author: {metadata.get('author', 'Unknown')}")
            print(f"   Category: {metadata.get('category', 'Unknown')}")
            print(f"   Tags: {', '.join(metadata.get('tags', []))}")
            print(f"   Views: {metadata.get('stats', {}).get('views', 0)}")
            print(f"   Likes: {metadata.get('stats', {}).get('likes', 0)}")
            if 'featured' in metadata:
                print(f"   Featured: {metadata['featured']}")
        
        # Demonstrate filtering by parsing metadata
        print("\n--- Filtering documents with high engagement ---")
        high_engagement_docs = []
        all_results = table.search(np.random.rand(384).tolist()).limit(10).to_pandas()
        
        for idx, row in all_results.iterrows():
            metadata = get_metadata(row)
            views = metadata.get('stats', {}).get('views', 0)
            if views > 1600:
                high_engagement_docs.append({
                    'text': row['text'],
                    'author': metadata.get('author'),
                    'views': views
                })
        
        print(f"Found {len(high_engagement_docs)} high-engagement documents:")
        for doc in high_engagement_docs:
            print(f"  - {doc['text'][:50]}... (Views: {doc['views']}, Author: {doc['author']})")
        
        print("\nJSON metadata complete")
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    main()