I'll help you set up the LanceDB initialization with environment-based model selection. Here's the complete solution:

```txt
# filepath: requirements.txt
pandas>=2.0.0
numpy>=1.24.0
lancedb>=0.5.0
sentence-transformers>=2.2.0
openai>=1.0.0
```

```python
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
    
    # Set default model names if not provided
    if not model_name:
        if provider == "openai":
            model_name = "text-embedding-ada-002"
        else:  # sentence-transformers
            model_name = "all-MiniLM-L6-v2"
    
    # Get embedding function registry
    registry = EmbeddingFunctionRegistry.get_instance()
    
    # Create model based on provider
    try:
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
        db_path = os.getenv("LANCEDB_PATH", "./lancedb")
        print(f"Connecting to database at: {db_path}")
        
        db = lancedb.connect(db_path)
        
        # Verify connection by listing tables
        existing_tables = db.table_names()
        print(f"✓ Database connected successfully")
        print(f"  Existing tables: {existing_tables if existing_tables else 'None'}")
        
        # Create a test table to verify everything works
        table_name = "documents"
        
        # Drop existing table if it exists (for clean initialization)
        if table_name in existing_tables:
            db.drop_table(table_name)
            print(f"  Dropped existing table: {table_name}")
        
        # Create new table with schema
        sample_data = [
            {"text": "LanceDB is a vector database"},
            {"text": "It supports hybrid search capabilities"}
        ]
        
        table = db.create_table(table_name, schema=Document, mode="overwrite")
        print(f"✓ Created table: {table_name}")
        
        # Add sample data
        table.add(sample_data)
        print(f"✓ Added {len(sample_data)} sample documents")
        
        # Verify data was added
        count = table.count_rows()
        print(f"  Table row count: {count}")
        
        print("\n" + "="*50)
        print("Environment-based embedding ready")
        print("="*50)
        print(f"Provider: {os.getenv('EMBEDDING_PROVIDER', 'sentence-transformers')}")
        print(f"Model: {os.getenv('MODEL_NAME', 'default')}")
        print(f"Database: {db_path}")
        print(f"Vector dimensions: {model.ndims()}")
        
    except ValueError as e:
        print(f"✗ Configuration error: {str(e)}")
        raise
    except RuntimeError as e:
        print(f"✗ Runtime error: {str(e)}")
        raise
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
```

## Key Features Implemented:

1. **Environment-Based Configuration**:
   - `EMBEDDING_PROVIDER`: Choose between "openai" or "sentence-transformers"
   - `MODEL_NAME`: Specify the model to use
   - `OPENAI_API_KEY`: Required for OpenAI provider
   - `LANCEDB_PATH`: Database location (defaults to "./lancedb")

2. **Embedding Model Selection**:
   - Uses `EmbeddingFunctionRegistry` to create models
   - Supports both OpenAI and sentence-transformers
   - Provides sensible defaults

3. **Dynamic Schema Creation**:
   - Creates `Document` class with `SourceField()` and `VectorField()`
   - Automatically determines vector dimensions from model

4. **Database Initialization**:
   - Connects to LanceDB
   - Creates a test table with sample data
   - Verifies connection and operations

5. **Error Handling**:
   - Validates environment variables
   - Provides clear error messages
   - Handles missing configurations gracefully

## Usage Examples:

**Using sentence-transformers (default)**:
```bash
python app.py
```

**Using OpenAI**:
```bash
export EMBEDDING_PROVIDER=openai
export MODEL_NAME=text-embedding-ada-002
export OPENAI_API_KEY=your-api-key
python app.py
```

**Custom database path**:
```bash
export LANCEDB_PATH=/path/to/db
python app.py
```