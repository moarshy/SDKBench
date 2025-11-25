"""LanceDB with dynamic vector dimension from embedding model."""

import lancedb
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector

def create_model_and_schema(model_name: str):
    """Create embedding model and schema with dynamic dimension."""
    registry = EmbeddingFunctionRegistry.get_instance()
    model = registry.get("sentence-transformers").create(name=model_name)

    # Vector dimension is dynamically determined from model
    class Document(LanceModel):
        text: str = model.SourceField()
        vector: Vector(model.ndims()) = model.VectorField()

    return model, Document

# Create with specific model
model, Document = create_model_and_schema("all-MiniLM-L6-v2")

# Initialize database
db = lancedb.connect("./dynamic_db")

def main():
    print(f"Model: all-MiniLM-L6-v2")
    print(f"Dynamic vector dimension: {model.ndims()}")

    # Test with different model
    model2, Doc2 = create_model_and_schema("all-mpnet-base-v2")
    print(f"all-mpnet-base-v2 dimension: {model2.ndims()}")

    print("Dynamic vector dimension ready")

if __name__ == "__main__":
    main()
