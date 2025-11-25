# filepath: pipeline.py
"""HYDE-enhanced RAG pipeline.

Build a complete pipeline using LanceDB for vector storage.
"""

import lancedb
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import pyarrow as pa

# Initialize embedding model (using a lightweight model for efficiency)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
EMBEDDING_DIM = 384  # Dimension for all-MiniLM-L6-v2

# Initialize database connection
db = lancedb.connect("./lancedb_data")
TABLE_NAME = "documents"

# Define document schema with vector field
schema = pa.schema([
    pa.field("id", pa.int64()),
    pa.field("text", pa.string()),
    pa.field("vector", pa.list_(pa.float32(), EMBEDDING_DIM)),
])


def generate_hypothetical_document(query: str) -> str:
    """Generate a hypothetical document for HYDE approach.
    
    In a production system, this would use an LLM to generate a hypothetical
    answer. For this implementation, we'll create a simple augmented query.
    
    Args:
        query: Original user query
        
    Returns:
        Hypothetical document text
    """
    # Mock HYDE generation - in production, use an LLM
    # This simulates what an ideal answer might look like
    hyde_prompt = f"""Based on the query: "{query}"
    
A comprehensive answer would include: {query}. This relates to vector databases, 
semantic search, and retrieval-augmented generation techniques."""
    
    return hyde_prompt


def ingest_documents(documents: List[Dict[str, str]]) -> int:
    """Ingest documents into the vector database.

    Args:
        documents: List of document dictionaries with 'text' field

    Returns:
        Number of documents ingested
    """
    if not documents:
        print("No documents to ingest")
        return 0
    
    try:
        # Extract texts for batch embedding generation
        texts = [doc["text"] for doc in documents]
        
        # Generate embeddings in batch for efficiency
        print(f"Generating embeddings for {len(texts)} documents...")
        embeddings = embedding_model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Prepare data with schema
        data = []
        for idx, (doc, embedding) in enumerate(zip(documents, embeddings)):
            data.append({
                "id": idx,
                "text": doc["text"],
                "vector": embedding.tolist()
            })
        
        # Create or overwrite table with documents
        print(f"Creating table '{TABLE_NAME}'...")
        db.create_table(
            TABLE_NAME,
            data=data,
            mode="overwrite",
            schema=schema
        )
        
        # Create an IVF-PQ index for efficient search on larger datasets
        table = db.open_table(TABLE_NAME)
        if len(data) >= 256:  # Only create index if we have enough data
            print("Creating vector index...")
            table.create_index(
                metric="cosine",
                num_partitions=max(2, len(data) // 128),
                num_sub_vectors=min(16, EMBEDDING_DIM // 8)
            )
        
        print(f"Successfully ingested {len(data)} documents")
        return len(data)
        
    except Exception as e:
        print(f"Error ingesting documents: {e}")
        raise


def search(query: str, k: int = 5, use_hyde: bool = True) -> List[Dict[str, Any]]:
    """Search for relevant documents using HYDE-enhanced retrieval.

    Args:
        query: Search query text
        k: Number of results to return
        use_hyde: Whether to use HYDE (Hypothetical Document Embeddings)

    Returns:
        List of top-k results with text and scores
    """
    try:
        # Open the table
        table = db.open_table(TABLE_NAME)
        
        # HYDE: Generate hypothetical document and use it for search
        if use_hyde:
            print("Using HYDE approach...")
            search_text = generate_hypothetical_document(query)
        else:
            search_text = query
        
        # Generate query embedding
        print(f"Generating query embedding...")
        query_embedding = embedding_model.encode(
            search_text,
            convert_to_numpy=True
        )
        
        # Perform vector similarity search
        print(f"Searching for top {k} results...")
        results = (
            table.search(query_embedding.tolist())
            .metric("cosine")
            .limit(k)
            .to_pandas()
        )
        
        # Format results
        formatted_results = []
        for _, row in results.iterrows():
            formatted_results.append({
                "id": int(row["id"]),
                "text": row["text"],
                "score": float(row["_distance"]) if "_distance" in row else 0.0
            })
        
        print(f"Found {len(formatted_results)} results")
        return formatted_results
        
    except Exception as e:
        print(f"Error during search: {e}")
        raise


def generate_response(query: str, context: List[Dict[str, Any]]) -> str:
    """Generate response using retrieved context.

    Args:
        query: User query
        context: Retrieved documents

    Returns:
        Formatted response (mock LLM call)
    """
    if not context:
        return "No relevant information found to answer the query."
    
    # Format context for prompt
    context_text = "\n\n".join([
        f"[Document {i+1}] (Score: {doc['score']:.4f})\n{doc['text']}"
        for i, doc in enumerate(context)
    ])
    
    # Mock LLM response generation
    # In production, this would call an actual LLM API
    response = f"""Based on the retrieved context, here's the answer to: "{query}"

Retrieved Context:
{context_text}

Answer:
Based on the most relevant documents retrieved, {context[0]['text']} 
This information directly addresses your query about {query.lower()}.

(Note: This is a mock response. In production, an LLM would generate a more sophisticated answer.)
"""
    
    return response


def run_pipeline(query: str, k: int = 5, use_hyde: bool = True) -> Dict[str, Any]:
    """Run the complete RAG pipeline.

    Args:
        query: User query
        k: Number of documents to retrieve
        use_hyde: Whether to use HYDE approach

    Returns:
        Dictionary with query, retrieved documents, and generated response
    """
    print(f"\n{'='*60}")
    print(f"Running RAG Pipeline for query: '{query}'")
    print(f"{'='*60}\n")
    
    try:
        # Step 1: Search for relevant documents
        print("Step 1: Retrieving relevant documents...")
        retrieved_docs = search(query, k=k, use_hyde=use_hyde)
        
        # Step 2: Generate response with context
        print("\nStep 2: Generating response...")
        response = generate_response(query, retrieved_docs)
        
        # Return complete pipeline result
        result = {
            "query": query,
            "retrieved_documents": retrieved_docs,
            "response": response,
            "num_retrieved": len(retrieved_docs)
        }
        
        print("\nPipeline execution completed successfully!")
        return result
        
    except Exception as e:
        print(f"Error in pipeline execution: {e}")
        raise


def main():
    """Example usage of the pipeline."""
    print("Initializing HYDE-enhanced RAG Pipeline with LanceDB\n")
    
    # Sample documents
    sample_docs = [
        {"text": "LanceDB is a vector database for AI applications."},
        {"text": "Vector search enables semantic similarity matching."},
        {"text": "RAG combines retrieval with generation for better answers."},
        {"text": "Embeddings convert text into numerical vectors for comparison."},
        {"text": "HYDE uses hypothetical documents to improve retrieval accuracy."},
        {"text": "Semantic search understands meaning beyond keyword matching."},
        {"text": "Vector databases store and query high-dimensional embeddings efficiently."},
        {"text": "Retrieval-augmented generation enhances LLM responses with relevant context."},
    ]
    
    # Ingest documents
    print("=" * 60)
    print("INGESTION PHASE")
    print("=" * 60 + "\n")
    num_ingested = ingest_documents(sample_docs)
    print(f"\n✓ Ingested {num_ingested} documents into LanceDB\n")
    
    # Run queries through pipeline
    queries = [
        "What is LanceDB?",
        "How does semantic search work?",
        "Explain RAG systems"
    ]
    
    for query in queries:
        # Run with HYDE
        result = run_pipeline(query, k=3, use_hyde=True)
        
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"\nQuery: {result['query']}")
        print(f"\nRetrieved {result['num_retrieved']} documents:")
        for i, doc in enumerate(result['retrieved_documents'], 1):
            print(f"\n  {i}. [Score: {doc['score']:.4f}] {doc['text']}")
        
        print(f"\n{'-'*60}")
        print("Generated Response:")
        print(f"{'-'*60}")
        print(result['response'])
        print("\n")
    
    print("=" * 60)
    print("Pipeline demonstration completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()