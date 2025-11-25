"""Basic vector similarity search."""

import lancedb
from sentence_transformers import SentenceTransformer

# Initialize
db = lancedb.connect("./my_lancedb")
model = SentenceTransformer("all-MiniLM-L6-v2")

def search_similar(query_text: str, k: int = 5):
    """Search for similar documents."""
    table = db.open_table("documents")
    query_vector = model.encode(query_text).tolist()
    results = table.search(query_vector).limit(k).to_pandas()
    return results

def main():
    results = search_similar("machine learning", k=10)
    print(f"Found {len(results)} similar documents")
    for _, row in results.iterrows():
        print(f"  - {row['text'][:50]}... (distance: {row['_distance']:.3f})")

if __name__ == "__main__":
    main()
