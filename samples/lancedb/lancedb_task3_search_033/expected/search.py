"""Search with prefiltering (more efficient)."""

import lancedb
from sentence_transformers import SentenceTransformer
from lancedb.pydantic import LanceModel, Vector

db = lancedb.connect("./my_lancedb")
model = SentenceTransformer("all-MiniLM-L6-v2")

class Document(LanceModel):
    text: str
    category: str
    vector: Vector(384)

def _ensure_sample_data():
    """Ensure sample data exists for testing."""
    if "documents" not in db.table_names():
        # Create sample data
        sample_texts = [
            ("Machine learning is transforming AI", "tech"),
            ("Deep learning uses neural networks", "tech"),
            ("Natural language processing advances", "tech"),
            ("Python is great for data science", "programming"),
            ("Vector databases enable semantic search", "database"),
        ]
        data = [
            Document(text=text, category=cat, vector=model.encode(text).tolist())
            for text, cat in sample_texts
        ]
        db.create_table("documents", data, mode="overwrite")

def search_with_prefilter(query_text: str, category: str, k: int = 10):
    """Search with prefiltering for efficiency."""
    _ensure_sample_data()
    table = db.open_table("documents")
    query_vector = model.encode(query_text).tolist()

    # Prefilter=True filters BEFORE computing distances (faster!)
    results = (
        table.search(query_vector)
        .where(f"category = '{category}'", prefilter=True)
        .limit(k)
        .to_pandas()
    )
    return results

def main():
    _ensure_sample_data()
    results = search_with_prefilter("machine learning", "tech", k=5)
    print(f"Found {len(results)} results in 'tech' category")

if __name__ == "__main__":
    main()
