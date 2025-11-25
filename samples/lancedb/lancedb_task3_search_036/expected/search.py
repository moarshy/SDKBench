"""filtered_search search implementation."""

import lancedb
from sentence_transformers import SentenceTransformer

db = lancedb.connect("./my_lancedb")
model = SentenceTransformer("all-MiniLM-L6-v2")

def search(query_text: str, k: int = 10):
    """Perform vector search."""
    table = db.open_table("documents")
    query_vector = model.encode(query_text).tolist()
    results = table.search(query_vector).limit(k).to_pandas()
    return results

def main():
    results = search("test query", k=10)
    print(f"Found {len(results)} results")

if __name__ == "__main__":
    main()
