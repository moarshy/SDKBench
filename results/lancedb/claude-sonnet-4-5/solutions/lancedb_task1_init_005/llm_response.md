```txt
# filepath: requirements.txt
pandas>=2.0.0
numpy>=1.24.0
lancedb>=0.5.0
sentence-transformers>=2.2.0
```

```python
# filepath: app.py
"""LanceDB with Sentence Transformers via EmbeddingFunctionRegistry."""

import lancedb
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector

# Get registry instance and create sentence-transformers model
registry = EmbeddingFunctionRegistry.get_instance()
model = registry.get("sentence-transformers").create(name="all-MiniLM-L6-v2")

# Define Document schema with auto-embedding
class Document(LanceModel):
    text: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()

def get_database():
    """Initialize database with sentence transformer embeddings.

    Returns:
        lancedb.DBConnection: Connected database instance
    """
    try:
        # Connect to LanceDB (creates directory if it doesn't exist)
        db = lancedb.connect("./lancedb_data")
        return db
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise

def main():
    """Main function to initialize and test the database."""
    try:
        # Initialize database
        db = get_database()
        print(f"✓ Database connected successfully at: {db.uri}")
        
        # Test embedding generation
        test_text = "This is a test document for sentence transformers"
        print(f"\n✓ Testing embedding generation...")
        print(f"  Model: all-MiniLM-L6-v2")
        print(f"  Vector dimensions: {model.ndims()}")
        print(f"  Test text: '{test_text}'")
        
        # Create a test table to verify everything works
        table_name = "test_documents"
        
        # Check if table exists and drop it for clean test
        if table_name in db.table_names():
            db.drop_table(table_name)
            print(f"  Dropped existing '{table_name}' table")
        
        # Create table with schema
        table = db.create_table(
            table_name,
            schema=Document,
            mode="overwrite"
        )
        print(f"✓ Created table '{table_name}' with Document schema")
        
        # Add test document
        table.add([Document(text=test_text)])
        print(f"✓ Added test document (embedding auto-generated)")
        
        # Verify the document was added
        count = table.count_rows()
        print(f"✓ Table contains {count} document(s)")
        
        print("\n✓ Sentence transformer pipeline ready")
        print(f"✓ All systems operational!")
        
    except Exception as e:
        print(f"✗ Error during initialization: {e}")
        raise

if __name__ == "__main__":
    main()
```