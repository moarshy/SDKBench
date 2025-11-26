"""Search with IVF-PQ index."""

import lancedb
from lancedb.pydantic import LanceModel, Vector
from sentence_transformers import SentenceTransformer
import numpy as np

db = lancedb.connect("./my_lancedb")
model = SentenceTransformer("all-MiniLM-L6-v2")

class Document(LanceModel):
    text: str
    vector: Vector(384)

def _ensure_sample_data():
    """Ensure sample data exists for testing."""
    if "documents" not in db.table_names():
        # Create sample data with vectors
        sample_texts = [
            "Machine learning is transforming AI",
            "Deep learning uses neural networks",
            "Natural language processing advances",
            "Python is great for data science",
            "Vector databases enable semantic search",
        ]
        data = [
            Document(text=text, vector=model.encode(text).tolist())
            for text in sample_texts
        ]
        db.create_table("documents", data, mode="overwrite")

def create_ivf_pq_index(table):
    """Create IVF-PQ index for fast search."""
    table.create_index(
        metric="cosine",
        num_partitions=256,
        num_sub_vectors=96
    )

def search_indexed(query_text: str, k: int = 10, nprobes: int = 20):
    """Search using IVF-PQ index."""
    _ensure_sample_data()
    table = db.open_table("documents")
    query_vector = model.encode(query_text).tolist()

    # Index is used automatically, nprobes controls search breadth
    results = (
        table.search(query_vector)
        .nprobes(nprobes)
        .limit(k)
        .to_pandas()
    )
    return results

def main():
    _ensure_sample_data()
    results = search_indexed("machine learning", k=10)
    print(f"Indexed search found {len(results)} results")

if __name__ == "__main__":
    main()
