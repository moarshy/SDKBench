```python
# filepath: requirements.txt
pandas>=2.0.0
numpy>=1.24.0
lancedb>=0.5.0
```

```python
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
        vector: Document embedding vector
        metadata: Dictionary of metadata to store as JSON
    
    Raises:
        ValueError: If metadata cannot be serialized to JSON
        Exception: If document cannot be added to table
    """
    try:
        # Serialize metadata to JSON string
        metadata_json = json.dumps(metadata)
        
        # Create document
        document = Document(
            text=text,
            vector=vector,
            metadata_json=metadata_json
        )
        
        # Add to table
        table.add([document])
        print(f"Added document: '{text[:50]}...' with metadata")
        
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to serialize metadata to JSON: {e}")
    except Exception as e:
        raise Exception(f"Failed to add document to table: {e}")


def get_metadata(row) -> dict:
    """Parse JSON metadata from row.

    Args:
        row: A row from LanceDB table query results
    
    Returns:
        Dictionary containing parsed metadata, or empty dict if parsing fails
    
    Raises:
        ValueError: If metadata_json field is invalid JSON
    """
    try:
        # Get metadata_json field
        metadata_json = row.get('metadata_json') or row.get('metadata_json', None)
        
        # Handle case where metadata_json might be accessed as attribute
        if metadata_json is None and hasattr(row, 'metadata_json'):
            metadata_json = row.metadata_json
        
        # Return empty dict if no metadata
        if metadata_json is None or metadata_json == '':
            return {}
        
        # Parse JSON
        metadata = json.loads(metadata_json)
        
        return metadata
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in metadata_json field: {e}")
    except Exception as e:
        print(f"Warning: Could not parse metadata: {e}")
        return {}


def main():
    """Main function demonstrating JSON metadata storage."""
    try:
        # Connect to LanceDB
        db = lancedb.connect("./lancedb_json_metadata")
        
        # Create table with schema
        table_name = "documents_with_json"
        
        # Drop table if exists for clean demo
        try:
            db.drop_table(table_name)
        except:
            pass
        
        # Create empty table with schema
        table = db.create_table(table_name, schema=Document)
        
        print("Created table with JSON metadata support\n")
        
        # Add documents with nested metadata
        documents = [
            {
                "text": "Machine learning is a subset of artificial intelligence",
                "vector": np.random.rand(384).tolist(),
                "metadata": {
                    "author": "John Doe",
                    "category": "AI",
                    "tags": ["machine learning", "AI", "technology"],
                    "published_date": "2024-01-15",
                    "stats": {
                        "views": 1500,
                        "likes": 250,
                        "shares": 45
                    }
                }
            },
            {
                "text": "Deep learning uses neural networks with multiple layers",
                "vector": np.random.rand(384).tolist(),
                "metadata": {
                    "author": "Jane Smith",
                    "category": "Deep Learning",
                    "tags": ["deep learning", "neural networks", "AI"],
                    "published_date": "2024-02-20",
                    "stats": {
                        "views": 2300,
                        "likes": 380,
                        "shares": 67
                    }
                }
            },
            {
                "text": "Natural language processing enables computers to understand human language",
                "vector": np.random.rand(384).tolist(),
                "metadata": {
                    "author": "Bob Johnson",
                    "category": "NLP",
                    "tags": ["NLP", "language", "AI", "text processing"],
                    "published_date": "2024-03-10",
                    "stats": {
                        "views": 1800,
                        "likes": 290,
                        "shares": 52
                    }
                }
            }
        ]
        
        # Add documents to table
        print("Adding documents with nested JSON metadata:")
        for doc in documents:
            add_with_json_metadata(
                table,
                doc["text"],
                doc["vector"],
                doc["metadata"]
            )
        
        print(f"\nTotal documents in table: {table.count_rows()}\n")
        
        # Query and parse metadata
        print("Querying documents and parsing metadata:\n")
        
        # Get all documents
        results = table.search().limit(10).to_pandas()
        
        for idx, row in results.iterrows():
            print(f"Document {idx + 1}:")
            print(f"  Text: {row['text'][:60]}...")
            
            # Parse metadata
            metadata = get_metadata(row)
            
            if metadata:
                print(f"  Author: {metadata.get('author', 'Unknown')}")
                print(f"  Category: {metadata.get('category', 'Unknown')}")
                print(f"  Tags: {', '.join(metadata.get('tags', []))}")
                print(f"  Published: {metadata.get('published_date', 'Unknown')}")
                
                # Access nested metadata
                stats = metadata.get('stats', {})
                if stats:
                    print(f"  Stats: {stats.get('views', 0)} views, "
                          f"{stats.get('likes', 0)} likes, "
                          f"{stats.get('shares', 0)} shares")
            else:
                print("  No metadata available")
            
            print()
        
        # Demonstrate vector search with metadata
        print("Performing vector search and accessing metadata:\n")
        query_vector = np.random.rand(384).tolist()
        search_results = table.search(query_vector).limit(2).to_pandas()
        
        for idx, row in search_results.iterrows():
            print(f"Result {idx + 1}:")
            print(f"  Text: {row['text'][:60]}...")
            
            metadata = get_metadata(row)
            if metadata:
                print(f"  Category: {metadata.get('category', 'Unknown')}")
                print(f"  Tags: {', '.join(metadata.get('tags', []))}")
            print()
        
        print("JSON metadata complete")
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    main()
```

This solution implements a complete JSON metadata storage pattern for LanceDB with the following features:

1. **Schema Definition**: Uses `LanceModel` with a `metadata_json` field to store JSON as a string
2. **Add Function**: Serializes Python dictionaries to JSON strings and stores them with documents
3. **Get Function**: Parses JSON strings back to Python dictionaries with proper error handling
4. **Nested Metadata**: Supports complex nested structures (dictionaries within dictionaries, lists, etc.)
5. **Error Handling**: Comprehensive try-catch blocks for JSON serialization/deserialization errors
6. **Demo**: Shows adding documents with rich metadata including nested stats, tags, and other fields
7. **Query Support**: Demonstrates both regular queries and vector search while accessing metadata

The implementation handles edge cases like missing metadata, invalid JSON, and provides clear error messages for debugging.