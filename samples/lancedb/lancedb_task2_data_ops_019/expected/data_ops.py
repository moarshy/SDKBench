"""Auto-embedding with SourceField pattern."""

import lancedb
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector

# Initialize embedding model via registry
registry = EmbeddingFunctionRegistry.get_instance()
model = registry.get("sentence-transformers").create(name="all-MiniLM-L6-v2")

# Define schema with auto-embedding
class Document(LanceModel):
    text: str = model.SourceField()  # Auto-embed this field
    vector: Vector(model.ndims()) = model.VectorField()  # Generated

# Connect to database
db = lancedb.connect("./my_lancedb")

def ingest_documents(documents: list):
    """Ingest documents with automatic embedding."""
    # Use dict data with schema - LanceDB auto-embeds when using the schema
    # Don't instantiate Document directly as Pydantic requires all fields
    table = db.create_table("documents", documents, schema=Document, mode="overwrite")
    return table

def main():
    # Create documents WITHOUT vectors - they're auto-generated!
    documents = [
        {"text": "LanceDB is a vector database"},
        {"text": "Embeddings are generated automatically"},
        {"text": "No need to compute vectors manually"},
    ]
    table = ingest_documents(documents)
    df = table.to_pandas()
    print(f"Auto-embedding complete: {len(df)} records")
    print(f"Vector dimension: {len(df['vector'].iloc[0])}")

if __name__ == "__main__":
    main()
