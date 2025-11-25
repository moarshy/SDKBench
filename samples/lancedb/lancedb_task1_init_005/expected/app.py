"""LanceDB with Sentence Transformers via EmbeddingFunctionRegistry."""

import lancedb
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector

# Get registry instance and create sentence-transformers model
registry = EmbeddingFunctionRegistry.get_instance()
model = registry.get("sentence-transformers").create(name="all-MiniLM-L6-v2")

# Define Document schema with auto-embedding
class Document(LanceModel):
    text: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()

# Initialize database
db = lancedb.connect("./st_db")

def get_database():
    """Initialize database with sentence transformer embeddings."""
    return db

def main():
    print(f"Sentence transformer dimension: {model.ndims()}")
    # Test auto-embedding by creating a table
    table = db.create_table("test", [Document(text="Hello world")], mode="overwrite")
    print(f"Created table with {len(table.to_pandas())} records")
    print("Sentence transformer pipeline ready")

if __name__ == "__main__":
    main()
