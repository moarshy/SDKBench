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
        # Check if table already exists and drop it for clean initialization
        if table_name in db.table_names():
            db.drop_table(table_name)
        
        # Create table with Document schema
        # The schema includes auto-embedding configuration
        table = db.create_table(
            table_name,
            schema=Document,
            mode="create"
        )
        
        print(f"Table '{table_name}' created with auto-embedding schema")
        print(f"Embedding dimension: {model.ndims()}")
        
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
        print(f"  - Source field: 'text' (will be auto-embedded)")
        print(f"  - Vector field: 'vector' (auto-generated, dim={model.ndims()})")
        print(f"  - Metadata field: 'metadata' (optional)")
        
        # Example: Insert sample data to demonstrate auto-embedding
        sample_data = [
            {"text": "LanceDB is a vector database", "metadata": "intro"},
            {"text": "Auto-embedding makes it easy to work with text", "metadata": "feature"},
        ]
        
        print("\nInserting sample data (vectors will be auto-generated)...")
        table.add(sample_data)
        print(f"✓ Inserted {len(sample_data)} documents")
        
        # Verify data was inserted
        count = table.count_rows()
        print(f"✓ Table now contains {count} rows")
        
        print("\nSchema with auto-embedding ready")
        
    except Exception as e:
        print(f"Error during initialization: {e}")
        raise

if __name__ == "__main__":
    main()
```

This solution provides:

1. **Complete imports**: All necessary LanceDB components including `EmbeddingFunctionRegistry`, `LanceModel`, and `Vector`

2. **Embedding model initialization**: Uses the sentence-transformers registry to create an embedding model (BAAI/bge-small-en-v1.5, a popular and efficient model)

3. **Auto-embedding schema**: The `Document` class uses:
   - `SourceField()`: Marks the text field as the source for embedding
   - `VectorField()`: Automatically generates embeddings from the source field
   - Optional metadata field for additional information

4. **Table creation**: The `create_table_with_schema()` function:
   - Checks for existing tables and drops them for clean initialization
   - Creates a new table with the auto-embedding schema
   - Returns the table object

5. **Database connection**: Properly connects to LanceDB with error handling

6. **Verification**: Includes sample data insertion to demonstrate that vectors are automatically generated from text

7. **Error handling**: Comprehensive try-catch blocks for robust operation

The auto-embedding feature means you only need to provide text data - LanceDB will automatically generate the vector embeddings using the configured model!