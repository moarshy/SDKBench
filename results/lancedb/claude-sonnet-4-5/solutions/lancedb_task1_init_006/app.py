# filepath: app.py
"""Environment-based embedding model selection."""

import os
import lancedb
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector

def get_embedding_model():
    """Get embedding model based on environment.

    Returns:
        Embedding model instance based on environment configuration.
    
    Raises:
        ValueError: If required environment variables are not set or provider is invalid.
    """
    # Read environment variables
    provider = os.getenv("EMBEDDING_PROVIDER", "sentence-transformers")
    model_name = os.getenv("MODEL_NAME")
    
    # Validate provider
    if provider not in ["openai", "sentence-transformers"]:
        raise ValueError(
            f"Invalid EMBEDDING_PROVIDER: {provider}. "
            "Must be 'openai' or 'sentence-transformers'"
        )
    
    # Set default model names if not specified
    if not model_name:
        if provider == "openai":
            model_name = "text-embedding-ada-002"
        else:  # sentence-transformers
            model_name = "all-MiniLM-L6-v2"
    
    # Get embedding function registry
    registry = EmbeddingFunctionRegistry.get_instance()
    
    try:
        # Create model based on provider
        if provider == "openai":
            # For OpenAI, we need an API key
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI provider")
            
            model = registry.get("openai").create(
                name=model_name,
                api_key=api_key
            )
        else:  # sentence-transformers
            model = registry.get("sentence-transformers").create(
                name=model_name
            )
        
        print(f"✓ Loaded {provider} model: {model_name}")
        return model
        
    except Exception as e:
        raise RuntimeError(f"Failed to create embedding model: {str(e)}")

def create_document_class(model):
    """Create document class with dynamic model.

    Args:
        model: Embedding model instance from get_embedding_model()
    
    Returns:
        LanceModel subclass configured with the embedding model.
    """
    class Document(LanceModel):
        """Document schema with text and vector embedding."""
        text: str = model.SourceField()
        vector: Vector(model.ndims()) = model.VectorField()
        
        # Optional metadata fields
        metadata: dict = {}
    
    return Document

def main():
    """Initialize LanceDB with environment-based embedding model."""
    try:
        # Get embedding model from environment
        print("Initializing embedding model...")
        model = get_embedding_model()
        
        # Create document schema
        print("Creating document schema...")
        Document = create_document_class(model)
        
        # Initialize database
        db_path = os.getenv("LANCEDB_PATH", "./lancedb_data")
        print(f"Connecting to database at: {db_path}")
        
        db = lancedb.connect(db_path)
        print(f"✓ Connected to LanceDB at {db_path}")
        
        # Create or open a test table to verify connection
        table_name = "documents"
        
        # Check if table exists
        existing_tables = db.table_names()
        
        if table_name in existing_tables:
            print(f"✓ Table '{table_name}' already exists")
            table = db.open_table(table_name)
            print(f"  Table has {len(table)} rows")
        else:
            print(f"Creating new table '{table_name}'...")
            # Create table with schema
            table = db.create_table(
                table_name,
                schema=Document,
                mode="overwrite"
            )
            print(f"✓ Created table '{table_name}'")
        
        # Verify we can perform basic operations
        print("\nVerifying database operations...")
        print(f"  Database URI: {db.uri}")
        print(f"  Available tables: {db.table_names()}")
        
        print("\n" + "="*50)
        print("Environment-based embedding ready")
        print("="*50)
        print(f"Provider: {os.getenv('EMBEDDING_PROVIDER', 'sentence-transformers')}")
        print(f"Model: {os.getenv('MODEL_NAME', 'default')}")
        print(f"Database: {db_path}")
        print("="*50)
        
        return db, table, Document
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {str(e)}")
        raise

if __name__ == "__main__":
    main()