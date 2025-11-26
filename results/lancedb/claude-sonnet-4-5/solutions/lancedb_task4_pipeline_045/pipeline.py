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

# Initialize the embedding model globally for efficiency
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
        
        # Prepare data for ingestion
        data = []
        for idx, (doc, embedding) in enumerate(zip(documents, embeddings)):
            record = {
                "id": idx,
                "text": doc["text"],
                "vector": embedding.tolist(),
                "metadata": doc.get("metadata", "")
            }
            data.append(record)
        
        # Create or overwrite table with documents
        # Using mode="overwrite" to replace existing data
        # For append mode, use mode="append"
        if TABLE_NAME in db.table_names():
            print(f"Table '{TABLE_NAME}' exists. Overwriting...")
            table = db.create_table(TABLE_NAME, data=data, mode="overwrite")
        else:
            print(f"Creating new table '{TABLE_NAME}'...")
            table = db.create_table(TABLE_NAME, data=data)
        
        # Create a vector index for faster search
        # Using IVF_PQ index for efficient similarity search
        print("Creating vector index...")
        table.create_index(
            metric="cosine",
            num_partitions=max(2, len(data) // 10),  # Adaptive partitioning
            num_sub_vectors=min(16, EMBEDDING_DIM // 8)
        )
        
        print(f"Successfully ingested {len(data)} documents")
        return len(data)
    
    except Exception as e:
        print(f"Error during document ingestion: {e}")
        raise


def search(query: str, k: int = 5) -> pd.DataFrame:
    """Search for relevant documents.

    Args:
        query: Search query text
        k: Number of results to return

    Returns:
        DataFrame with top-k results including text and similarity scores
    """
    try:
        # Check if table exists
        if TABLE_NAME not in db.table_names():
            print(f"Table '{TABLE_NAME}' does not exist. Please ingest documents first.")
            return pd.DataFrame()
        
        # Open the table
        table = db.open_table(TABLE_NAME)
        
        # Generate query embedding
        print(f"Generating query embedding for: '{query}'")
        query_embedding = embedding_model.encode(
            query,
            convert_to_numpy=True
        )
        
        # Perform vector similarity search
        print(f"Searching for top-{k} similar documents...")
        results = (
            table.search(query_embedding.tolist())
            .metric("cosine")
            .limit(k)
            .to_pandas()
        )
        
        # Add similarity score (distance to similarity conversion)
        if not results.empty and '_distance' in results.columns:
            # For cosine distance, similarity = 1 - distance
            results['similarity'] = 1 - results['_distance']
        
        print(f"Found {len(results)} results")
        return results
    
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
        f"[Document {i+1}] (Similarity: {doc.get('similarity', 'N/A'):.3f})\n{doc['text']}"
        for i, doc in enumerate(context)
    ])
    
    # Mock LLM response generation
    # In production, this would call an actual LLM API
    response = f"""Query: {query}

Retrieved Context:
{context_text}

Generated Answer:
Based on the retrieved documents, here's what I found:
{context[0]['text']}

This information is most relevant to your query with a similarity score of {context[0].get('similarity', 'N/A'):.3f}.
"""
    
    return response


def run_pipeline(query: str, k: int = 5) -> Dict[str, Any]:
    """Run the complete RAG pipeline.

    Args:
        query: User query
        k: Number of documents to retrieve

    Returns:
        Dictionary containing search results and generated response
    """
    print(f"\n{'='*60}")
    print(f"Running pipeline for query: '{query}'")
    print(f"{'='*60}\n")
    
    try:
        # Stage 1: Search for relevant documents
        results_df = search(query, k=k)
        
        if results_df.empty:
            return {
                "query": query,
                "results": [],
                "response": "No documents found. Please ingest documents first."
            }
        
        # Convert results to list of dictionaries
        context = results_df.to_dict('records')
        
        # Stage 2: Generate response with context
        response = generate_response(query, context)
        
        return {
            "query": query,
            "results": context,
            "response": response,
            "num_results": len(context)
        }
    
    except Exception as e:
        print(f"Error in pipeline: {e}")
        return {
            "query": query,
            "results": [],
            "response": f"Pipeline error: {str(e)}",
            "error": str(e)
        }


def main():
    """Example usage of the pipeline."""
    print("Initializing Two-Stage Retrieval Pipeline")
    print(f"Database path: {DB_PATH}")
    print(f"Embedding model: {MODEL_NAME}")
    print(f"Embedding dimension: {EMBEDDING_DIM}\n")
    
    # Sample documents with more variety
    sample_docs = [
        {
            "text": "LanceDB is a vector database for AI applications. It provides fast similarity search and is optimized for machine learning workloads.",
            "metadata": "intro"
        },
        {
            "text": "Vector search enables semantic similarity matching. It allows finding documents based on meaning rather than exact keyword matches.",
            "metadata": "concept"
        },
        {
            "text": "RAG combines retrieval with generation for better answers. It retrieves relevant context and uses it to generate informed responses.",
            "metadata": "architecture"
        },
        {
            "text": "Embeddings are dense vector representations of text. They capture semantic meaning in a numerical format suitable for similarity search.",
            "metadata": "embeddings"
        },
        {
            "text": "LanceDB supports both vector and full-text search. This enables hybrid search strategies for improved retrieval accuracy.",
            "metadata": "features"
        }
    ]
    
    # Ingest documents
    print("\n--- Stage 1: Document Ingestion ---")
    num_ingested = ingest_documents(sample_docs)
    print(f"\nIngested {num_ingested} documents successfully\n")
    
    # Run queries through pipeline
    queries = [
        "What is LanceDB?",
        "How does semantic search work?",
        "Explain RAG architecture"
    ]
    
    print("\n--- Stage 2: Query Processing ---")
    for query in queries:
        result = run_pipeline(query, k=3)
        
        print(f"\nQuery: {result['query']}")
        print(f"Retrieved {result['num_results']} documents")
        print("\nTop Result:")
        if result['results']:
            top_result = result['results'][0]
            print(f"  Text: {top_result['text'][:100]}...")
            print(f"  Similarity: {top_result.get('similarity', 'N/A'):.3f}")
        print("\n" + "-" * 60)
    
    # Demonstrate detailed response for one query
    print("\n--- Stage 3: Detailed Response Generation ---")
    detailed_result = run_pipeline("What is vector search?", k=2)
    print(detailed_result['response'])
    
    print("\n" + "="*60)
    print("Pipeline demonstration complete!")
    print("="*60)


if __name__ == "__main__":
    main()