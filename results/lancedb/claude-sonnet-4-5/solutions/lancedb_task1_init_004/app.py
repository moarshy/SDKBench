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
    """
    # Ensure OPENAI_API_KEY is set
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError(
            "OPENAI_API_KEY environment variable must be set. "
            "Get your API key from https://platform.openai.com/api-keys"
        )
    
    # Connect to LanceDB (creates directory if it doesn't exist)
    db = lancedb.connect("./lancedb_data")
    
    return db

def main():
    """Main function to initialize database and create table."""
    try:
        # Initialize database
        db = get_database()
        print(f"✓ Connected to LanceDB at: {db.uri}")
        
        # Create table with Document schema
        # Using mode="overwrite" to recreate table if it exists
        table_name = "documents"
        
        # Check if table exists
        existing_tables = db.table_names()
        if table_name in existing_tables:
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
        
        print(f"✓ Table schema: {table.schema}")
        print("✓ OpenAI embedding pipeline ready")
        
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        return 1
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())