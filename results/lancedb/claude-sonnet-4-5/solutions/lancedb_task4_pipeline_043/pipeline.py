# filepath: pipeline.py
"""Flask RAG with Redis caching.

Build a complete pipeline using LanceDB for vector storage.
"""

import lancedb
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import os
from pathlib import Path

# Initialize the embedding model
MODEL_NAME = "all-MiniLM-L6-v2"
embedding_model = SentenceTransformer(MODEL_NAME)

# Database configuration
DB_PATH = "./lancedb_data"
TABLE_NAME = "documents"

# Initialize database connection
db = None
table = None

def initialize_db():
    """Initialize the LanceDB connection and create table if needed."""
    global db, table
    
    # Create database directory if it doesn't exist
    Path(DB_PATH).mkdir(parents=True, exist_ok=True)
    
    # Connect to LanceDB
    db = lancedb.connect(DB_PATH)
    
    print(f"Database initialized at {DB_PATH}")
    return db

def get_embedding_dimension():
    """Get the dimension of embeddings from the model."""
    sample_text = "sample"
    sample_embedding = embedding_model.encode(sample_text)
    return len(sample_embedding)

def ingest_documents(documents: List[Dict[str, str]]) -> int:
    """Ingest documents into the vector database.

    Args:
        documents: List of document dictionaries with 'text' field

    Returns:
        Number of documents ingested
    """
    global db, table
    
    if db is None:
        initialize_db()
    
    if not documents:
        print("No documents to ingest")
        return 0
    
    try:
        # Extract texts from documents
        texts = [doc["text"] for doc in documents]
        
        # Generate embeddings in batch for efficiency
        print(f"Generating embeddings for {len(texts)} documents...")
        embeddings = embedding_model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Prepare data for LanceDB
        data = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            record = {
                "id": i,
                "text": doc["text"],
                "vector": embedding.tolist(),
            }
            # Add any additional metadata from the document
            for key, value in doc.items():
                if key != "text":
                    record[key] = value
            data.append(record)
        
        # Create or overwrite table
        if TABLE_NAME in db.table_names():
            print(f"Table '{TABLE_NAME}' exists, dropping and recreating...")
            db.drop_table(TABLE_NAME)
        
        # Create table with the data
        table = db.create_table(TABLE_NAME, data=data)
        
        # Create an index for faster search (IVF_PQ index)
        # Only create index if we have enough documents
        if len(data) >= 256:
            print("Creating vector index for faster search...")
            table.create_index(
                metric="cosine",
                num_partitions=max(2, len(data) // 128),
                num_sub_vectors=min(96, get_embedding_dimension())
            )
        
        print(f"Successfully ingested {len(documents)} documents")
        return len(documents)
    
    except Exception as e:
        print(f"Error ingesting documents: {e}")
        raise

def search(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Search for relevant documents.

    Args:
        query: Search query text
        k: Number of results to return

    Returns:
        List of top-k relevant documents with scores
    """
    global db, table
    
    if db is None:
        initialize_db()
    
    if table is None:
        try:
            table = db.open_table(TABLE_NAME)
        except Exception as e:
            print(f"Error opening table: {e}")
            return []
    
    try:
        # Generate query embedding
        print(f"Searching for: '{query}'")
        query_embedding = embedding_model.encode(query, convert_to_numpy=True)
        
        # Perform vector similarity search
        results = (
            table.search(query_embedding.tolist())
            .metric("cosine")
            .limit(k)
            .to_pandas()
        )
        
        # Convert results to list of dictionaries
        search_results = []
        for _, row in results.iterrows():
            result = {
                "id": int(row["id"]),
                "text": row["text"],
                "score": float(row["_distance"]),  # Distance score (lower is better for cosine)
            }
            # Add any additional metadata
            for col in results.columns:
                if col not in ["id", "text", "vector", "_distance"]:
                    result[col] = row[col]
            search_results.append(result)
        
        print(f"Found {len(search_results)} results")
        return search_results
    
    except Exception as e:
        print(f"Error during search: {e}")
        return []

def generate_response(query: str, context: List[Dict[str, Any]]) -> str:
    """Generate response using retrieved context.

    Args:
        query: User query
        context: Retrieved documents

    Returns:
        Formatted response (mock LLM call)
    """
    if not context:
        return "I couldn't find any relevant information to answer your question."
    
    # Format context for prompt
    context_text = "\n\n".join([
        f"[Document {i+1}] (Relevance: {1 - doc['score']:.2f})\n{doc['text']}"
        for i, doc in enumerate(context)
    ])
    
    # Mock LLM response - in production, this would call an actual LLM
    response = f"""Based on the retrieved context, here's the answer to your query:

Query: {query}

Relevant Context:
{context_text}

Answer: Based on the {len(context)} most relevant documents, I can provide information related to your query. The documents discuss topics including vector databases, semantic search, and RAG systems. 

(Note: This is a mock response. In production, this would be generated by an LLM like GPT-4, Claude, or Llama using the context above.)
"""
    
    return response

def run_pipeline(query: str, k: int = 5) -> Dict[str, Any]:
    """Run the complete RAG pipeline.

    Args:
        query: User query
        k: Number of documents to retrieve

    Returns:
        Dictionary containing query, retrieved documents, and generated response
    """
    print("\n" + "="*60)
    print("Running RAG Pipeline")
    print("="*60)
    
    # Step 1: Search for relevant documents
    print("\n[Step 1] Retrieving relevant documents...")
    retrieved_docs = search(query, k=k)
    
    if not retrieved_docs:
        return {
            "query": query,
            "retrieved_documents": [],
            "response": "No relevant documents found.",
            "num_retrieved": 0
        }
    
    # Step 2: Generate response with context
    print("\n[Step 2] Generating response...")
    response = generate_response(query, retrieved_docs)
    
    # Step 3: Return complete pipeline result
    result = {
        "query": query,
        "retrieved_documents": retrieved_docs,
        "response": response,
        "num_retrieved": len(retrieved_docs)
    }
    
    print("\n[Step 3] Pipeline complete!")
    return result

def main():
    """Example usage of the pipeline."""
    print("Initializing RAG Pipeline with LanceDB")
    print("="*60)
    
    # Initialize database
    initialize_db()
    
    # Sample documents with more variety
    sample_docs = [
        {"text": "LanceDB is a vector database for AI applications.", "category": "database"},
        {"text": "Vector search enables semantic similarity matching.", "category": "search"},
        {"text": "RAG combines retrieval with generation for better answers.", "category": "rag"},
        {"text": "Embeddings convert text into numerical vectors.", "category": "embeddings"},
        {"text": "Sentence transformers are neural networks for generating embeddings.", "category": "models"},
        {"text": "Cosine similarity measures the angle between vectors.", "category": "metrics"},
        {"text": "LanceDB supports both vector and full-text search.", "category": "database"},
        {"text": "Retrieval augmented generation improves LLM accuracy.", "category": "rag"},
    ]
    
    # Ingest documents
    print("\n[Ingestion Phase]")
    num_ingested = ingest_documents(sample_docs)
    print(f"✓ Ingested {num_ingested} documents successfully")
    
    # Example queries
    queries = [
        "What is LanceDB?",
        "How does vector search work?",
        "Explain RAG systems",
    ]
    
    print("\n" + "="*60)
    print("Running Example Queries")
    print("="*60)
    
    for query in queries:
        result = run_pipeline(query, k=3)
        
        print(f"\n{'='*60}")
        print(f"Query: {result['query']}")
        print(f"{'='*60}")
        print(f"\nRetrieved {result['num_retrieved']} documents:")
        for i, doc in enumerate(result['retrieved_documents'], 1):
            print(f"\n  {i}. [Score: {1 - doc['score']:.3f}] {doc['text'][:80]}...")
        
        print(f"\n{'-'*60}")
        print("Generated Response:")
        print(f"{'-'*60}")
        print(result['response'][:300] + "...\n")
    
    print("\n" + "="*60)
    print("Pipeline ready for production use!")
    print("="*60)

if __name__ == "__main__":
    main()