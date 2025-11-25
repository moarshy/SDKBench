# filepath: app.py
"""LanceDB with dynamic vector dimension from embedding model."""

import lancedb
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector

def create_model_and_schema(model_name: str):
    """Create embedding model and schema with dynamic dimension.

    Args:
        model_name: Name of embedding model

    Returns:
        tuple: (embedding_model, schema_class)
    """
    # Get the embedding function registry instance
    registry = EmbeddingFunctionRegistry.get_instance()
    
    # Get the sentence-transformers embedding function and create model
    model = registry.get("sentence-transformers").create(name=model_name)
    
    # Get the dynamic dimension from the model
    vector_dim = model.ndims()
    
    # Create schema class with dynamic vector dimension
    class Document(LanceModel):
        text: str = model.SourceField()
        vector: Vector(vector_dim) = model.VectorField()
    
    return model, Document, vector_dim

def main():
    """Initialize LanceDB with dynamic vector dimensions."""
    try:
        # Create database connection
        db = lancedb.connect("./my_lancedb")
        print(f"✓ Connected to LanceDB at: ./my_lancedb")
        
        # Create model and schema with dynamic dimension
        # Using a small model for demonstration
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        print(f"\n✓ Loading embedding model: {model_name}")
        
        model, DocumentSchema, vector_dim = create_model_and_schema(model_name)
        print(f"✓ Model loaded successfully")
        print(f"✓ Dynamic vector dimension: {vector_dim}")
        
        # Create a sample table to verify everything works
        table_name = "documents"
        
        # Sample data
        sample_data = [
            {"text": "LanceDB is a vector database"},
            {"text": "It supports dynamic dimensions"},
            {"text": "Embeddings are generated automatically"}
        ]
        
        # Create table with the dynamic schema
        table = db.create_table(
            table_name,
            schema=DocumentSchema,
            mode="overwrite"
        )
        print(f"✓ Created table: {table_name}")
        
        # Add data (embeddings will be generated automatically)
        table.add(sample_data)
        print(f"✓ Added {len(sample_data)} documents with auto-generated embeddings")
        
        # Verify the data
        count = table.count_rows()
        print(f"✓ Table contains {count} rows")
        
        # Perform a simple search to verify everything works
        query = "vector database"
        results = table.search(query).limit(2).to_pandas()
        print(f"\n✓ Search test successful - found {len(results)} results for '{query}'")
        print("\nTop result:")
        print(f"  Text: {results.iloc[0]['text']}")
        print(f"  Distance: {results.iloc[0]['_distance']:.4f}")
        
        print("\n" + "="*50)
        print("Dynamic vector dimension ready")
        print(f"Model: {model_name}")
        print(f"Vector dimension: {vector_dim}")
        print(f"Database path: ./my_lancedb")
        print("="*50)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        raise

if __name__ == "__main__":
    main()