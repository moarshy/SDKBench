"""Search with prefiltering (more efficient)."""

import lancedb
from sentence_transformers import SentenceTransformer

db = lancedb.connect("./my_lancedb")
model = SentenceTransformer("all-MiniLM-L6-v2")

def search_with_prefilter(query_text: str, category: str, k: int = 10):
    """Search with prefiltering for efficiency."""
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
    results = search_with_prefilter("machine learning", "tech", k=5)
    print(f"Found {len(results)} results in 'tech' category")

if __name__ == "__main__":
    main()
