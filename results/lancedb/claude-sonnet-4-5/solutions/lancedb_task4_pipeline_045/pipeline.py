# filepath: pipeline.py
"""Two-stage retrieval pipeline.

Build a complete pipeline using LanceDB for vector storage.
"""

import lancedb
from sentence_transformers import SentenceTransformer
import pandas as pd
from typing import List, Dict, Any
import pyarrow as pa
from pathlib import Path

# Initialize embedding model globally for reuse
MODEL_NAME = "all-MiniLM-L6-v2"
embedding_model = SentenceTransformer(MODEL_NAME)
EMBEDDING_DIM = 384  # Dimension for all-MiniLM-L6-v2

# Database configuration
DB_PATH = "./lancedb_pipeline"
TABLE_NAME = "documents"

# Initialize database connection
db = lancedb.connect(DB_PATH)

# Define document schema with vector field
schema = pa.schema([
    pa.field("id", pa.int64()),
    pa.field("text", pa.string()),
    pa.field("vector", pa.list_(pa.float32(), EMBEDDING_DIM)),
    pa.field("metadata", pa.string())
])


def ingest_documents(documents: List[Dict[str, Any]]) -> int:
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
        # Extract texts for batch embedding
        texts = [doc.get("text", "") for doc in documents]
        
        # Generate embeddings in batch for efficiency
        print(f"Generating embeddings for {len(texts)} documents...")
        embeddings = embedding_model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Prepare data for insertion
        data = []
        for idx, (doc, embedding) in enumerate(zip(documents, embeddings)):
            data.append({
                "id": idx,
                "text": doc.get("text", ""),
                "vector": embedding.tolist(),
                "metadata": doc.get("metadata", "")
            })
        
        # Create or overwrite table with documents
        # Using mode="overwrite" to replace existing data
        # For append mode, use mode="append"
        if TABLE_NAME in db.table_names():
            print(f"Table '{TABLE_NAME}' exists. Overwriting...")
            table = db.create_table(
                TABLE_NAME,
                data=data,
                mode="overwrite"
            )
        else:
            print(f"Creating new table '{TABLE_NAME}'...")
            table = db.create_table(
                TABLE_NAME,
                data=data
            )
        
        # Create index for faster search (optional but recommended)
        # IVF_PQ index for large datasets
        print("Creating vector index...")
        try:
            table.create_index(
                metric="cosine",
                num_partitions=max(2, len(data) // 100),
                num_sub_vectors=min(16, EMBEDDING_DIM // 4)
            )
        except Exception as e:
            print(f"Index creation skipped or failed: {e}")
        
        print(f"Successfully ingested {len(data)} documents")
        return len(data)
    
    except Exception as e:
        print(f"Error during document ingestion: {e}")
        raise


def search(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Search for relevant documents.

    Args:
        query: Search query text
        k: Number of results to return

    Returns:
        List of top-k results with text and scores
    """
    try:
        # Open the table
        table = db.open_table(TABLE_NAME)
        
        # Generate query embedding
        print(f"Generating query embedding for: '{query}'")
        query_embedding = embedding_model.encode(
            query,
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
                "score": float(row["_distance"]),  # LanceDB returns distance
                "metadata": row.get("metadata", "")
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
        return "No relevant context found to answer the query."
    
    # Format context for prompt
    context_text = "\n\n".join([
        f"[Document {i+1}] (Score: {doc['score']:.4f})\n{doc['text']}"
        for i, doc in enumerate(context)
    ])
    
    # Mock LLM response - in production, this would call an actual LLM
    response = f"""Based on the retrieved context, here's the answer to your query:

Query: {query}

Retrieved Context:
{context_text}

Answer: Based on the {len(context)} most relevant documents retrieved, the information suggests that {context[0]['text'].lower()} This is supported by additional context showing related concepts and details.

(Note: This is a mock response. In production, this would be generated by an LLM like GPT-4, Claude, or Llama.)
"""
    
    return response


def run_pipeline(query: str, k: int = 5) -> Dict[str, Any]:
    """Run the complete RAG pipeline.

    Args:
        query: User query
        k: Number of documents to retrieve

    Returns:
        Dictionary with retrieved documents and generated response
    """
    print(f"\n{'='*60}")
    print(f"Running RAG Pipeline")
    print(f"{'='*60}\n")
    
    try:
        # Stage 1: Search for relevant documents
        print("Stage 1: Retrieval")
        print("-" * 60)
        retrieved_docs = search(query, k=k)
        
        # Stage 2: Generate response with context
        print(f"\nStage 2: Generation")
        print("-" * 60)
        response = generate_response(query, retrieved_docs)
        
        return {
            "query": query,
            "retrieved_documents": retrieved_docs,
            "response": response,
            "num_retrieved": len(retrieved_docs)
        }
    
    except Exception as e:
        print(f"Pipeline error: {e}")
        raise


def main():
    """Example usage of the pipeline."""
    print("Initializing Two-Stage Retrieval Pipeline")
    print("=" * 60)
    
    # Sample documents with more comprehensive content
    sample_docs = [
        {
            "text": "LanceDB is a vector database for AI applications. It provides fast vector search and is designed for embedding-based retrieval.",
            "metadata": "intro"
        },
        {
            "text": "Vector search enables semantic similarity matching. It uses embeddings to find documents with similar meaning rather than exact keyword matches.",
            "metadata": "concept"
        },
        {
            "text": "RAG combines retrieval with generation for better answers. It retrieves relevant context and uses it to generate more accurate responses.",
            "metadata": "architecture"
        },
        {
            "text": "Embeddings are dense vector representations of text. They capture semantic meaning and enable similarity comparisons.",
            "metadata": "embeddings"
        },
        {
            "text": "LanceDB supports hybrid search combining vector and full-text search. This provides both semantic and keyword-based retrieval.",
            "metadata": "features"
        }
    ]
    
    # Ingest documents
    print("\n1. Ingesting Documents")
    print("-" * 60)
    num_ingested = ingest_documents(sample_docs)
    print(f"✓ Ingested {num_ingested} documents\n")
    
    # Run queries through pipeline
    queries = [
        "What is LanceDB?",
        "How does semantic search work?",
        "Explain RAG architecture"
    ]
    
    for query in queries:
        result = run_pipeline(query, k=3)
        
        print(f"\n{'='*60}")
        print("PIPELINE RESULT")
        print(f"{'='*60}")
        print(result["response"])
        print(f"\n✓ Retrieved {result['num_retrieved']} documents")
        print(f"{'='*60}\n")
    
    print("\n✓ Pipeline execution completed successfully!")


if __name__ == "__main__":
    main()