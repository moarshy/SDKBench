"""Environment-based embedding model selection."""

import os
import lancedb
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector

def get_embedding_model():
    """Get embedding model based on environment."""
    registry = EmbeddingFunctionRegistry.get_instance()
    provider = os.environ.get("EMBEDDING_PROVIDER", "sentence-transformers")
    model_name = os.environ.get("MODEL_NAME", "all-MiniLM-L6-v2")

    if provider == "openai":
        return registry.get("openai").create(name=model_name)
    else:
        return registry.get("sentence-transformers").create(name=model_name)

# Initialize embedding model
model = get_embedding_model()

# Create document class with dynamic model
class Document(LanceModel):
    text: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()

# Initialize database
db = lancedb.connect("./env_db")

def main():
    provider = os.environ.get("EMBEDDING_PROVIDER", "sentence-transformers")
    print(f"Using {provider} with dimension {model.ndims()}")
    print("Environment-based embedding ready")

if __name__ == "__main__":
    main()
