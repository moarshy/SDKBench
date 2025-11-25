"""Vector similarity search implementation."""

import lancedb
import numpy as np
from sentence_transformers import SentenceTransformer

# Initialize
db = lancedb.connect("./my_lancedb")
model = SentenceTransformer("all-MiniLM-L6-v2")

def search_similar(query_text, k=20):
    """Search for similar documents."""
    # Open table
    table = db.open_table("documents")

    # Generate query embedding
    query_vector = model.encode(query_text).tolist()

    # Perform vector search
    results = table.search(query_vector).limit(k).to_pandas()

    return results

def main():
    """Test search functionality."""
    results = search_similar("machine learning", k=20)
    print(f"Found {len(results)} similar documents")
    for idx, row in results.iterrows():
        print(f"  - {row['text'][:50]}... (score: {row['_distance']:.3f})")

if __name__ == "__main__":
    main()
