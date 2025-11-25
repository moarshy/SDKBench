"""FastAPI production RAG service.

Complete pipeline using LanceDB for vector storage.
"""

import lancedb
import pandas as pd
from lancedb.pydantic import LanceModel, Vector
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

# Initialize embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Define document schema
class Document(LanceModel):
    text: str
    vector: Vector(384)  # Dimension for all-MiniLM-L6-v2
    metadata: str = ""

# Initialize database
db = lancedb.connect("./rag_pipeline_db")

def ingest_documents(documents: List[Dict[str, Any]]) -> int:
    """Ingest documents into the vector database.

    Args:
        documents: List of document dictionaries with 'text' field

    Returns:
        Number of documents ingested
    """
    # Generate embeddings
    texts = [doc["text"] for doc in documents]
    embeddings = model.encode(texts).tolist()

    # Prepare data for insertion
    data = [
        Document(
            text=doc["text"],
            vector=emb,
            metadata=doc.get("metadata", "")
        )
        for doc, emb in zip(documents, embeddings)
    ]

    # Create or overwrite table
    table = db.create_table("documents", data, mode="overwrite")

    return len(data)

def search(query: str, k: int = 5) -> pd.DataFrame:
    """Search for relevant documents.

    Args:
        query: Search query text
        k: Number of results to return

    Returns:
        DataFrame with search results
    """
    # Generate query embedding
    query_vector = model.encode(query).tolist()

    # Open table and search
    table = db.open_table("documents")
    results = table.search(query_vector).limit(k).to_pandas()

    return results

def generate_response(query: str, context: List[Dict]) -> str:
    """Generate response using retrieved context.

    Args:
        query: User query
        context: Retrieved documents

    Returns:
        Generated response string
    """
    # Format context
    context_text = "\n".join([f"- {doc['text']}" for doc in context])

    # Mock LLM response (in production, call actual LLM)
    response = f"Based on the retrieved information:\n{context_text}\n\nAnswer: This is a response to '{query}' using the above context."

    return response

def run_pipeline(query: str, k: int = 3) -> str:
    """Run the complete RAG pipeline.

    Args:
        query: User query
        k: Number of documents to retrieve

    Returns:
        Generated response
    """
    # Step 1: Retrieve relevant documents
    results = search(query, k=k)

    # Step 2: Convert to list of dicts
    context = results.to_dict('records')

    # Step 3: Generate response
    response = generate_response(query, context)

    return response

def main():
    """Example usage of the pipeline."""
    # Sample documents
    sample_docs = [
        {"text": "LanceDB is a vector database for AI applications.", "metadata": "overview"},
        {"text": "Vector search enables semantic similarity matching.", "metadata": "feature"},
        {"text": "RAG combines retrieval with generation for better answers.", "metadata": "concept"},
        {"text": "Embeddings convert text into numerical vectors.", "metadata": "concept"},
        {"text": "LanceDB supports multiple embedding models.", "metadata": "feature"}
    ]

    # Ingest documents
    count = ingest_documents(sample_docs)
    print(f"Ingested {count} documents")

    # Run query through pipeline
    query = "What is LanceDB?"
    response = run_pipeline(query)

    print(f"\nQuery: {query}")
    print(f"\nResponse:\n{response}")

if __name__ == "__main__":
    main()
