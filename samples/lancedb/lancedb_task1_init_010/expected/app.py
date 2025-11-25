"""LanceDB with embedding model integration."""

import lancedb
from sentence_transformers import SentenceTransformer

# Initialize embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize database
db = lancedb.connect("./embeddings_db")

def get_embedding_model():
    """Get sentence transformer model."""
    return model

def init_embedding_db():
    """Initialize database ready for embeddings."""
    return db, model

def embed_text(text: str):
    """Generate embedding for text."""
    return model.encode(text).tolist()

def main():
    """Embedding-ready main."""
    db, model = init_embedding_db()
    # Test embedding
    test_vec = embed_text("test")
    print(f"Model dimension: {len(test_vec)}")
    print(f"Database tables: {db.table_names()}")
    print("Embedding pipeline ready")

if __name__ == "__main__":
    main()
