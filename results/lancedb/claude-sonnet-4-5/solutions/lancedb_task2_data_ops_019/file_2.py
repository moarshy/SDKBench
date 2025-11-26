"""Auto-embedding with SourceField pattern."""

import lancedb
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector

# Initialize embedding model via registry
registry = EmbeddingFunctionRegistry.get_instance()
model = registry.get("sentence-transformers").create(name="BAAI/bge-small-en-v1.5")

# Define schema with auto-embedding
class Document(LanceModel):
    text: str = model.SourceField()  # Auto-embed this field
    vector: Vector(model.ndims()) = model.VectorField()  # Generated automatically

def ingest_documents(db, documents: list):
    """Ingest documents with automatic embedding.
    
    Args:
        db: LanceDB connection
        documents: List of document dictionaries with 'text' field
        
    Returns:
        LanceDB table with embedded documents
        
    Raises:
        ValueError: If documents list is empty or invalid
        Exception: If table creation or data insertion fails
    """
    if not documents:
        raise ValueError("Documents list cannot be empty")
    
    # Validate that all documents have 'text' field
    for i, doc in enumerate(documents):
        if not isinstance(doc, dict) or 'text' not in doc:
            raise ValueError(f"Document at index {i} must be a dict with 'text' field")
    
    try:
        # Create table with Document schema
        # The table will automatically generate embeddings for the text field
        table = db.create_table(
            "documents",
            schema=Document,
            mode="overwrite"  # Overwrite if exists for demo purposes
        )
        
        # Add documents (vectors auto-generated!)
        table.add(documents)
        
        print(f"Successfully ingested {len(documents)} documents with auto-generated embeddings")
        return table
        
    except Exception as e:
        raise Exception(f"Failed to ingest documents: {str(e)}")

def main():
    """Main function demonstrating auto-embedding workflow."""
    try:
        # Connect to LanceDB
        db = lancedb.connect("./lancedb_data")
        
        # Create documents WITHOUT vectors - they will be generated automatically
        documents = [
            {"text": "LanceDB is a vector database for AI applications"},
            {"text": "Auto-embedding simplifies the workflow by generating vectors automatically"},
            {"text": "SourceField marks which field should be embedded"},
            {"text": "VectorField stores the generated embedding vectors"},
            {"text": "This pattern eliminates manual embedding generation"}
        ]
        
        print(f"Ingesting {len(documents)} documents...")
        
        # Ingest - embeddings generated automatically
        table = ingest_documents(db, documents)
        
        # Verify the data was inserted correctly
        result = table.to_pandas()
        print(f"\nTable contains {len(result)} rows")
        print(f"Vector dimension: {len(result['vector'].iloc[0])}")
        print("\nSample data:")
        print(result[['text']].head())
        
        # Demonstrate search capability
        print("\n--- Testing Vector Search ---")
        query_text = "vector database"
        
        # Search using the same embedding model
        search_results = (
            table.search(query_text)
            .limit(3)
            .to_pandas()
        )
        
        print(f"\nTop 3 results for query: '{query_text}'")
        for idx, row in search_results.iterrows():
            print(f"{idx + 1}. {row['text'][:60]}...")
        
        print("\nAuto-embedding complete")
        
    except ValueError as ve:
        print(f"Validation error: {ve}")
    except Exception as e:
        print(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()