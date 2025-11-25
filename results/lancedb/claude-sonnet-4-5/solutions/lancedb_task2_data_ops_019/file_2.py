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
        Exception: For database operation errors
    """
    if not documents:
        raise ValueError("Documents list cannot be empty")
    
    # Validate that all documents have 'text' field
    for i, doc in enumerate(documents):
        if not isinstance(doc, dict) or 'text' not in doc:
            raise ValueError(f"Document at index {i} must be a dict with 'text' field")
    
    try:
        # Create table with Document schema
        # The embeddings will be automatically generated from the text field
        table = db.create_table(
            "documents",
            schema=Document,
            mode="overwrite"  # Overwrite if exists for demo purposes
        )
        
        # Add documents (vectors auto-generated!)
        table.add(documents)
        
        print(f"Successfully ingested {len(documents)} documents with auto-embeddings")
        return table
        
    except Exception as e:
        print(f"Error during document ingestion: {e}")
        raise

def main():
    """Main function demonstrating auto-embedding with SourceField."""
    try:
        # Connect to LanceDB
        db = lancedb.connect("./lancedb_data")
        
        # Create documents WITHOUT vectors - they will be auto-generated
        documents = [
            {"text": "LanceDB is a developer-friendly vector database for AI applications."},
            {"text": "Auto-embedding simplifies the process of vectorizing text data."},
            {"text": "SourceField automatically generates embeddings from text fields."},
            {"text": "Vector databases enable semantic search and similarity matching."},
            {"text": "Machine learning models can benefit from efficient vector storage."}
        ]
        
        print(f"Ingesting {len(documents)} documents...")
        
        # Ingest - embeddings generated automatically
        table = ingest_documents(db, documents)
        
        # Verify the data was ingested correctly
        count = table.count_rows()
        print(f"Table now contains {count} documents")
        
        # Display sample data to verify embeddings were created
        sample = table.to_pandas().head(2)
        print("\nSample documents (first 2):")
        for idx, row in sample.iterrows():
            print(f"\nDocument {idx + 1}:")
            print(f"  Text: {row['text'][:60]}...")
            print(f"  Vector dimensions: {len(row['vector'])}")
            print(f"  Vector sample (first 5 dims): {row['vector'][:5]}")
        
        # Demonstrate search capability
        print("\n--- Demonstrating Vector Search ---")
        query_text = "vector database for AI"
        print(f"Searching for: '{query_text}'")
        
        # Search using text (will be auto-embedded)
        results = table.search(query_text).limit(3).to_pandas()
        
        print("\nTop 3 results:")
        for idx, row in results.iterrows():
            print(f"\n{idx + 1}. {row['text']}")
            print(f"   Distance: {row['_distance']:.4f}")
        
        print("\nAuto-embedding complete!")
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()