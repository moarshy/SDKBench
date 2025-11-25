I'll help you set up LanceDB with auto-embedding schema. Let me provide the complete solution.

```txt
# filepath: requirements.txt
pandas>=2.0.0
numpy>=1.24.0
lancedb>=0.5.0
sentence-transformers>=2.2.0
pyarrow>=12.0.0
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
        # Check if table already exists
        if table_name in db.table_names():
            print(f"Table '{table_name}' already exists, opening existing table")
            return db.open_table(table_name)
        
        # Create table with Document schema
        # The schema will automatically embed text into vectors on insert
        table = db.create_table(
            table_name,
            schema=Document,
            mode="create"
        )
        
        print(f"Table '{table_name}' created successfully with auto-embedding schema")
        print(f"Vector dimensions: {model.ndims()}")
        
        return table
    
    except Exception as e:
        print(f"Error creating table: {e}")
        raise

def main():
    """Main function to initialize LanceDB with auto-embedding schema."""
    try:
        # Connect to database (creates directory if it doesn't exist)
        db_path = "./my_lancedb"
        print(f"Connecting to LanceDB at: {db_path}")
        
        db = lancedb.connect(db_path)
        print("✓ Database connection established")
        
        # Create table with schema
        table_name = "documents"
        table = create_table_with_schema(db, table_name)
        print(f"✓ Table '{table_name}' ready with auto-embedding")
        
        # Verify the schema
        print(f"\nTable schema:")
        print(f"  - text: str (source field for embedding)")
        print(f"  - vector: Vector({model.ndims()}) (auto-generated)")
        print(f"  - metadata: Optional[str]")
        
        # Test with sample data
        print("\nTesting auto-embedding with sample data...")
        sample_data = [
            {"text": "LanceDB is a vector database", "metadata": "intro"},
            {"text": "It supports auto-embedding", "metadata": "feature"}
        ]
        
        table.add(sample_data)
        print(f"✓ Added {len(sample_data)} documents (vectors auto-generated)")
        
        # Verify data was inserted
        count = table.count_rows()
        print(f"✓ Total documents in table: {count}")
        
        print("\nSchema with auto-embedding ready")
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()
```

This solution provides:

1. **Complete imports**: All necessary LanceDB components including `EmbeddingFunctionRegistry`, `LanceModel`, and `Vector`

2. **Embedding model initialization**: Uses the sentence-transformers registry to create an embedding model (BAAI/bge-small-en-v1.5)

3. **Auto-embedding schema**: 
   - `text` field marked as `SourceField()` - the source text to embed
   - `vector` field marked as `VectorField()` - automatically populated with embeddings
   - Optional `metadata` field for additional information

4. **Table creation**: 
   - Checks if table exists before creating
   - Creates table with the Document schema
   - Handles errors appropriately

5. **Database connection**: 
   - Connects to `./my_lancedb` directory
   - Creates directory if it doesn't exist
   - Verifies connection works

6. **Testing**: Includes sample data insertion to verify auto-embedding works correctly

The auto-embedding feature means you only need to provide the `text` field when inserting data - the `vector` field will be automatically generated using the embedding model!