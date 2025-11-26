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
        Exception: If database connection fails
    """
    # Ensure OPENAI_API_KEY is set
    if not os.environ.get("OPENAI_API_KEY"):
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
            print(f"✓ Created table '{table_name}' with OpenAI embedding schema")
        
        # Verify the schema
        print(f"✓ Table schema: {table.schema}")
        print(f"✓ Embedding model: text-embedding-3-small (dimensions: {model.ndims()})")
        print("\nOpenAI embedding pipeline ready")
        
        return db, table
        
    except ValueError as e:
        print(f"✗ Configuration error: {str(e)}")
        raise
    except Exception as e:
        print(f"✗ Initialization error: {str(e)}")
        raise

if __name__ == "__main__":
    main()