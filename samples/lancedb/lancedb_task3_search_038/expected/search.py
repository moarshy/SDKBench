"""Hybrid search with RRF reranking."""

import lancedb
from lancedb.rerankers import RRFReranker
from sentence_transformers import SentenceTransformer

db = lancedb.connect("./my_lancedb")
model = SentenceTransformer("all-MiniLM-L6-v2")

def search_with_rrf(query_text: str, k: int = 10):
    """Hybrid search with Reciprocal Rank Fusion."""
    table = db.open_table("documents")
    query_vector = model.encode(query_text).tolist()

    # RRF combines rankings from multiple retrievers
    reranker = RRFReranker()
    results = (
        table.search(query_type="hybrid")
        .vector(query_vector)
        .text(query_text)
        .rerank(reranker)
        .limit(k)
        .to_pandas()
    )
    return results

def main():
    results = search_with_rrf("deep learning neural networks", k=10)
    print(f"RRF search found {len(results)} results")

if __name__ == "__main__":
    main()
