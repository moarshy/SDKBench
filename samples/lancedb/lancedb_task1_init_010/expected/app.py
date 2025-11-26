"""LanceDB with SourceField/VectorField auto-embedding schema."""

import lancedb
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector
from typing import Optional

# Initialize embedding model via registry
registry = EmbeddingFunctionRegistry.get_instance()
model = registry.get("sentence-transformers").create(name="all-MiniLM-L6-v2")

# Define schema with auto-embedding
class Document(LanceModel):
    text: str = model.SourceField()  # Text to embed
    vector: Vector(model.ndims()) = model.VectorField()  # Auto-generated
    metadata: Optional[str] = None

# Initialize database
db = lancedb.connect("./schema_db")

def create_table_with_schema(table_name: str):
    """Create table with auto-embedding schema."""
    # Use dict data - LanceDB will auto-embed when using the schema
    # Don't instantiate Document directly as it requires vector field
    data = [{"text": "Sample document", "metadata": None}]
    table = db.create_table(table_name, data, schema=Document, mode="overwrite")
    return table

def main():
    table = create_table_with_schema("documents")
    df = table.to_pandas()
    print(f"Created table with {len(df)} records")
    print(f"Vector dimension: {len(df['vector'].iloc[0])}")
    print("Schema with auto-embedding ready")

if __name__ == "__main__":
    main()
