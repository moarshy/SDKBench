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

# Initialize database
db = lancedb.connect("./openai_db")

def get_database():
    """Initialize database with OpenAI embeddings."""
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable required")
    return db

def main():
    print(f"OpenAI embedding dimension: {model.ndims()}")
    print("OpenAI embedding pipeline ready")

if __name__ == "__main__":
    main()
