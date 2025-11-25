"""Hybrid search with Full-Text Search."""

import lancedb
from sentence_transformers import SentenceTransformer

db = lancedb.connect("./my_lancedb")
model = SentenceTransformer("all-MiniLM-L6-v2")

def setup_fts_index(table):
    """Create FTS index on table."""
    table.create_fts_index("text")

def hybrid_search(query_text: str, k: int = 10):
    """Perform hybrid vector + text search."""
    table = db.open_table("documents")
    query_vector = model.encode(query_text).tolist()

    # Hybrid search combines BM25 + vector similarity
    results = (
        table.search(query_type="hybrid")
        .vector(query_vector)
        .text(query_text)
        .limit(k)
        .to_pandas()
    )
    return results

def main():
    results = hybrid_search("machine learning algorithms", k=10)
    print(f"Hybrid search found {len(results)} results")

if __name__ == "__main__":
    main()
