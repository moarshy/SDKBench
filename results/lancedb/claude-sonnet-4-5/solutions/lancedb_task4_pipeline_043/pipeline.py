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

# Initialize the embedding model globally
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
EMBEDDING_DIM = 384  # Dimension for all-MiniLM-L6-v2

# Database configuration
DB_PATH = "./lancedb_data"
TABLE_NAME = "documents"

# Initialize database connection
db = None
table = None

def initialize_db():
    """Initialize the LanceDB connection and table."""
    global db, table
    
    # Create database directory if it doesn't exist
    Path(DB_PATH).mkdir(parents=True, exist_ok=True)
    
    # Connect to LanceDB
    db = lancedb.connect(DB_PATH)
    
    print(f"Database initialized at {DB_PATH}")
    return db

def get_or_create_table():
    """Get existing table or create a new one."""
    global db, table
    
    if db is None:
        initialize_db()
    
    try:
        # Try to open existing table
        table = db.open_table(TABLE_NAME)
        print(f"Opened existing table '{TABLE_NAME}' with {len(table)} documents")
    except Exception:
        # Table doesn't exist, will be created during first ingestion
        print(f"Table '{TABLE_NAME}' will be created on first ingestion")
        table = None
    
    return table

def generate_embeddings(texts: List[str]) -> np.ndarray:
    """Generate embeddings for a list of texts.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        numpy array of embeddings
    """
    embeddings = EMBEDDING_MODEL.encode(
        texts,
        show_progress_bar=True,
        batch_size=32,
        convert_to_numpy=True
    )
    return embeddings

def ingest_documents(documents: List[Dict[str, str]]) -> int:
    """Ingest documents into the vector database.

    Args:
        documents: List of document dictionaries with 'text' field

    Returns:
        Number of documents ingested
    """
    global db, table
    
    if not documents:
        print("No documents to ingest")
        return 0
    
    if db is None:
        initialize_db()
    
    # Extract texts and generate embeddings
    texts = [doc['text'] for doc in documents]
    print(f"Generating embeddings for {len(texts)} documents...")
    embeddings = generate_embeddings(texts)
    
    # Prepare data with embeddings
    data = []
    for i, doc in enumerate(documents):
        record = {
            'text': doc['text'],
            'vector': embeddings[i].tolist(),
            'id': i
        }
        # Add any additional metadata from the document
        for key, value in doc.items():
            if key != 'text':
                record[key] = value
        data.append(record)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    try:
        if table is None:
            # Create new table
            table = db.create_table(TABLE_NAME, data=df, mode="overwrite")
            print(f"Created new table '{TABLE_NAME}' with {len(df)} documents")
        else:
            # Add to existing table
            table.add(df)
            print(f"Added {len(df)} documents to existing table")
    except Exception as e:
        print(f"Error during ingestion: {e}")
        # Try to recreate table if there's a schema mismatch
        table = db.create_table(TABLE_NAME, data=df, mode="overwrite")
        print(f"Recreated table '{TABLE_NAME}' with {len(df)} documents")
    
    return len(documents)

def search(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Search for relevant documents.

    Args:
        query: Search query text
        k: Number of results to return

    Returns:
        List of top-k results with text and scores
    """
    global table
    
    if table is None:
        get_or_create_table()
    
    if table is None:
        print("No documents in database. Please ingest documents first.")
        return []
    
    # Generate query embedding
    print(f"Searching for: '{query}'")
    query_embedding = generate_embeddings([query])[0]
    
    try:
        # Perform vector similarity search
        results = (
            table.search(query_embedding.tolist())
            .limit(k)
            .to_pandas()
        )
        
        # Convert results to list of dictionaries
        search_results = []
        for _, row in results.iterrows():
            result = {
                'text': row['text'],
                'score': float(row['_distance']) if '_distance' in row else None,
                'id': row['id'] if 'id' in row else None
            }
            # Add any additional metadata
            for col in results.columns:
                if col not in ['text', 'vector', '_distance', 'id']:
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
        f"[Document {i+1}] {doc['text']}"
        for i, doc in enumerate(context)
    ])
    
    # Mock LLM response (in production, this would call an actual LLM)
    response = f"""Based on the retrieved context, here's the answer to your query:

Query: {query}

Relevant Context:
{context_text}

Answer: Based on the {len(context)} most relevant documents, I found information related to your query. The documents discuss topics including vector databases, semantic search, and retrieval-augmented generation (RAG) systems.

(Note: This is a mock response. In production, this would be generated by an LLM like GPT-4, Claude, or Llama.)
"""
    
    return response

def run_pipeline(query: str, k: int = 5) -> Dict[str, Any]:
    """Run the complete RAG pipeline.

    Args:
        query: User query
        k: Number of documents to retrieve

    Returns:
        Dictionary with query, context, and response
    """
    print(f"\n{'='*60}")
    print(f"Running RAG Pipeline")
    print(f"{'='*60}")
    
    # Step 1: Search for relevant documents
    print("\n[Step 1] Retrieving relevant documents...")
    context = search(query, k=k)
    
    if not context:
        return {
            'query': query,
            'context': [],
            'response': "No relevant documents found. Please ingest documents first."
        }
    
    # Step 2: Generate response with context
    print("\n[Step 2] Generating response...")
    response = generate_response(query, context)
    
    # Step 3: Return complete result
    result = {
        'query': query,
        'context': context,
        'response': response,
        'num_results': len(context)
    }
    
    print(f"\n[Complete] Pipeline finished successfully")
    return result

def batch_ingest(documents: List[Dict[str, str]], batch_size: int = 100) -> int:
    """Ingest documents in batches for better performance.
    
    Args:
        documents: List of document dictionaries
        batch_size: Number of documents per batch
        
    Returns:
        Total number of documents ingested
    """
    total_ingested = 0
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        print(f"\nProcessing batch {i//batch_size + 1} ({len(batch)} documents)...")
        count = ingest_documents(batch)
        total_ingested += count
    
    return total_ingested

def main():
    """Example usage of the pipeline."""
    print("="*60)
    print("LanceDB RAG Pipeline Demo")
    print("="*60)
    
    # Sample documents
    sample_docs = [
        {"text": "LanceDB is a vector database for AI applications.", "category": "database"},
        {"text": "Vector search enables semantic similarity matching.", "category": "search"},
        {"text": "RAG combines retrieval with generation for better answers.", "category": "rag"},
        {"text": "Embeddings convert text into numerical vectors.", "category": "embeddings"},
        {"text": "Sentence transformers are neural networks for creating embeddings.", "category": "embeddings"},
        {"text": "Semantic search finds documents by meaning, not just keywords.", "category": "search"},
        {"text": "LanceDB supports both vector and full-text search.", "category": "database"},
        {"text": "RAG systems improve LLM responses with relevant context.", "category": "rag"},
    ]
    
    # Initialize database
    print("\n[1] Initializing database...")
    initialize_db()
    
    # Ingest documents
    print("\n[2] Ingesting documents...")
    num_ingested = ingest_documents(sample_docs)
    print(f"✓ Successfully ingested {num_ingested} documents")
    
    # Example queries
    queries = [
        "What is LanceDB?",
        "How does semantic search work?",
        "Tell me about RAG systems"
    ]
    
    # Run queries through pipeline
    print("\n[3] Running example queries...")
    for query in queries:
        result = run_pipeline(query, k=3)
        
        print(f"\n{'='*60}")
        print(f"Query: {result['query']}")
        print(f"{'='*60}")
        print(f"\nTop {result['num_results']} Results:")
        for i, doc in enumerate(result['context'], 1):
            score = doc.get('score', 'N/A')
            print(f"\n  {i}. {doc['text']}")
            print(f"     Score: {score}")
        
        print(f"\n{'-'*60}")
        print("Response:")
        print(f"{'-'*60}")
        print(result['response'])
    
    print("\n" + "="*60)
    print("Pipeline demo completed successfully!")
    print("="*60)

if __name__ == "__main__":
    main()