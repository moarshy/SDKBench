I'll help you set up LanceDB with OpenAI embeddings via the registry. Let me provide the complete solution.

```txt
# filepath: requirements.txt
pandas>=2.0.0
numpy>=1.24.0
lancedb>=0.5.0
openai>=1.0.0
```

```python
# filepath: app.py
"""LanceDB with OpenAI embeddings via EmbeddingFunctionRegistry."""

import os
import lancedb
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector

# Get registry instance and create OpenAI embedding model
registry = EmbeddingFunctionRegistry.get_instance()
model = registry.get("openai").create(name="text-embedding-3-small")

# Define Document schema with SourceField and VectorField
class Document(LanceModel):
    text: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()

def get_database():
    """Initialize database with OpenAI embeddings.

    Returns:
        lancedb.DBConnection: Connected database instance
    
    Raises:
        ValueError: If OPENAI_API_KEY is not set
        Exception: If connection fails
    """
    # Ensure OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError(
            "OPENAI_API_KEY environment variable must be set. "
            "Get your API key from https://platform.openai.com/api-keys"
        )
    
    try:
        # Connect to LanceDB (creates directory if it doesn't exist)
        db = lancedb.connect("./lancedb_data")
        print(f"✓ Connected to LanceDB at ./lancedb_data")
        return db
    except Exception as e:
        raise Exception(f"Failed to connect to LanceDB: {str(e)}")

def main():
    """Main function to initialize database and create table."""
    try:
        # Initialize database
        db = get_database()
        
        # Create table with Document schema
        # Drop existing table if it exists for clean initialization
        table_name = "documents"
        
        if table_name in db.table_names():
            print(f"✓ Table '{table_name}' already exists")
            table = db.open_table(table_name)
        else:
            # Create empty table with schema
            table = db.create_table(
                table_name,
                schema=Document,
                mode="overwrite"
            )
            print(f"✓ Created table '{table_name}' with OpenAI embeddings")
        
        # Verify the setup with a test document
        test_data = [
            {"text": "LanceDB is a vector database for AI applications"},
            {"text": "OpenAI provides powerful embedding models"}
        ]
        
        # Add test documents (embeddings will be generated automatically)
        table.add(test_data)
        print(f"✓ Added {len(test_data)} test documents")
        
        # Verify we can query
        count = table.count_rows()
        print(f"✓ Table contains {count} documents")
        
        print("\n✅ OpenAI embedding pipeline ready")
        print(f"   - Database: ./lancedb_data")
        print(f"   - Table: {table_name}")
        print(f"   - Embedding model: text-embedding-3-small")
        print(f"   - Vector dimensions: {model.ndims()}")
        
        return db, table
        
    except ValueError as e:
        print(f"❌ Configuration error: {str(e)}")
        raise
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
```

This solution provides:

1. **Complete imports**: All necessary LanceDB components including the embedding registry
2. **OpenAI integration**: Uses the registry to create an OpenAI embedding function with `text-embedding-3-small` model
3. **Schema definition**: `Document` class with automatic embedding generation via `SourceField()` and `VectorField()`
4. **Robust connection handling**: 
   - Checks for `OPENAI_API_KEY` environment variable
   - Creates database directory if it doesn't exist
   - Proper error handling with informative messages
5. **Table initialization**: Creates table with the Document schema and adds test data
6. **Verification**: Confirms the setup works by adding and counting documents

To use this:
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-..."

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The embeddings will be automatically generated when you add documents to the table, and you can perform vector similarity searches on them.