"""HYDE - Hypothetical Document Embeddings."""

import lancedb
from sentence_transformers import SentenceTransformer

db = lancedb.connect("./my_lancedb")
model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_hypothetical_answer(query: str) -> str:
    """Generate hypothetical answer using LLM (mock)."""
    # In production, use actual LLM
    # Here we simulate with a template
    return f"The answer to '{query}' involves understanding the key concepts and their relationships in the domain."

def hyde_search(query: str, k: int = 10):
    """Search using HYDE pattern."""
    table = db.open_table("documents")

    # Generate hypothetical answer
    hypothetical_answer = generate_hypothetical_answer(query)

    # Embed the hypothetical answer (not the query!)
    hyde_vector = model.encode(hypothetical_answer).tolist()

    # Search using hypothetical answer embedding
    results = table.search(hyde_vector).limit(k).to_pandas()
    return results

def main():
    results = hyde_search("What is machine learning?", k=10)
    print(f"HYDE search found {len(results)} results")

if __name__ == "__main__":
    main()
