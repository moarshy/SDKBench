I'll help you set up LanceDB with auto-embedding schema using SourceField and VectorField. Let me provide the complete solution.

```txt
# filepath: requirements.txt
pandas>=2.0.0
numpy>=1.24.0
lancedb>=0.5.0
sentence-transformers>=2.2.0
```

```python
# filepath: app.py
"""LanceDB with SourceField/VectorField auto-embedding schema."""

import lancedb
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector
from typing import Optional
import os

# Initialize embedding model via registry
registry = EmbeddingFunctionRegistry.get_instance()
model = registry.get("sentence-transformers").create(name="BAAI/bge-small-en-v1.5")

# Define schema with auto-embedding
class Document(LanceModel):
    text: str = model.SourceField()  # Text to embed
    vector: Vector(model.ndims()) = model.VectorField()  # Auto-generated
    metadata: Optional[str] = None

def create_table_with_schema(db, table_name: str):
    """Create table with auto-embedding schema.

    Args:
        db: LanceDB connection
        table_name: Name of the table to create

    Returns:
        LanceDB table with auto-embedding schema
    """
    try:
        # Drop table if it exists to ensure clean creation
        if table_name in db.table_names():
            db.drop_table(table_name)
        
        # Create table with Document schema
        # The schema will automatically embed text into vector on insert
        table = db.create_table(
            table_name,
            schema=Document,
            mode="create"
        )
        
        print(f"Table '{table_name}' created with auto-embedding schema")
        print(f"Vector dimensions: {model.ndims()}")
        
        return table
    
    except Exception as e:
        print(f"Error creating table: {e}")
        raise

def main():
    """Main function to initialize LanceDB with auto-embedding schema."""
    try:
        # Connect to database (creates directory if it doesn't exist)
        db_path = "./lancedb_data"
        print(f"Connecting to LanceDB at: {db_path}")
        
        db = lancedb.connect(db_path)
        print("✓ Database connection established")
        
        # Create table with schema
        table_name = "documents"
        table = create_table_with_schema(db, table_name)
        print(f"✓ Table '{table_name}' ready with auto-embedding")
        
        # Verify the schema
        print("\nSchema details:")
        print(f"  - Source field: 'text' (str)")
        print(f"  - Vector field: 'vector' ({model.ndims()} dimensions)")
        print(f"  - Metadata field: 'metadata' (Optional[str])")
        
        # Test with sample data
        print("\nTesting auto-embedding with sample data...")
        sample_data = [
            {"text": "LanceDB is a vector database", "metadata": "intro"},
            {"text": "It supports auto-embedding", "metadata": "feature"},
            {"text": "Built for AI applications", "metadata": "purpose"}
        ]
        
        table.add(sample_data)
        print(f"✓ Added {len(sample_data)} documents with auto-embedding")
        
        # Verify data was inserted
        count = table.count_rows()
        print(f"✓ Table now contains {count} rows")
        
        print("\nSchema with auto-embedding ready")
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()
```

This solution provides:

1. **Complete imports**: All necessary LanceDB components including `EmbeddingFunctionRegistry`, `LanceModel`, and `Vector`

2. **Embedding model initialization**: Uses the sentence-transformers registry to create an embedding model (BAAI/bge-small-en-v1.5, a popular small model)

3. **Auto-embedding schema**: 
   - `text` field marked as `SourceField()` - the source text to embed
   - `vector` field marked as `VectorField()` - automatically populated from text
   - `metadata` field for optional additional data

4. **Database connection**: Creates/opens a LanceDB database at `./lancedb_data`

5. **Table creation**: Creates a table with the auto-embedding schema

6. **Error handling**: Comprehensive try-catch blocks for robust operation

7. **Testing**: Includes sample data insertion to verify the auto-embedding works

8. **Verification**: Checks table creation and data insertion

The auto-embedding feature means that when you insert data with just the `text` field, LanceDB automatically generates the `vector` field using the configured embedding model. This simplifies the workflow significantly!