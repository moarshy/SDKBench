# filepath: pipeline.py
"""Multimodal CLIP search.

Build a complete pipeline using LanceDB for vector storage.
"""

import lancedb
from sentence_transformers import SentenceTransformer
import pandas as pd
from typing import List, Dict, Any, Optional
import os

# Initialize the CLIP model for multimodal embeddings
# Using a CLIP model that can handle both text and images
MODEL_NAME = "clip-ViT-B-32"
model = SentenceTransformer(MODEL_NAME)

# Database configuration
DB_PATH = "./lancedb_multimodal"
TABLE_NAME = "multimodal_documents"

# Initialize database connection
db = None
table = None

def get_db_connection():
    """Get or create database connection."""
    global db
    if db is None:
        db = lancedb.connect(DB_PATH)
    return db

def get_or_create_table():
    """Get existing table or create new one."""
    global table
    db = get_db_connection()
    
    try:
        table = db.open_table(TABLE_NAME)
    except Exception:
        # Table doesn't exist, will be created during first ingest
        table = None
    
    return table

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts using CLIP model.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of embedding vectors
    """
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()

def ingest_documents(documents: List[Dict[str, Any]]) -> int:
    """Ingest documents into the vector database.

    Args:
        documents: List of document dictionaries with 'text' field
                  Can also include 'metadata', 'id', 'image_path' fields

    Returns:
        Number of documents ingested
    """
    if not documents:
        return 0
    
    # Extract texts for embedding
    texts = [doc.get("text", "") for doc in documents]
    
    # Generate embeddings for all documents in batch
    embeddings = generate_embeddings(texts)
    
    # Prepare data for insertion
    data = []
    for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
        record = {
            "id": doc.get("id", f"doc_{i}"),
            "text": doc.get("text", ""),
            "vector": embedding,
            "metadata": doc.get("metadata", {}),
        }
        
        # Add optional fields
        if "image_path" in doc:
            record["image_path"] = doc["image_path"]
        if "title" in doc:
            record["title"] = doc["title"]
        if "source" in doc:
            record["source"] = doc["source"]
            
        data.append(record)
    
    # Convert to DataFrame for efficient insertion
    df = pd.DataFrame(data)
    
    # Get database connection
    db = get_db_connection()
    
    global table
    try:
        # Try to open existing table
        table = db.open_table(TABLE_NAME)
        # Add new documents to existing table
        table.add(df)
    except Exception:
        # Create new table if it doesn't exist
        table = db.create_table(TABLE_NAME, df)
    
    return len(documents)

def search(query: str, k: int = 5, filter_condition: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search for relevant documents using vector similarity.

    Args:
        query: Search query text
        k: Number of results to return
        filter_condition: Optional SQL-like filter condition

    Returns:
        List of top-k matching documents with scores
    """
    global table
    
    # Ensure table exists
    if table is None:
        table = get_or_create_table()
    
    if table is None:
        return []
    
    # Generate query embedding
    query_embedding = model.encode([query], convert_to_numpy=True)[0].tolist()
    
    # Perform vector similarity search
    search_query = table.search(query_embedding).limit(k)
    
    # Apply filter if provided
    if filter_condition:
        search_query = search_query.where(filter_condition)
    
    # Execute search and convert to pandas DataFrame
    results_df = search_query.to_pandas()
    
    # Convert results to list of dictionaries
    results = []
    for _, row in results_df.iterrows():
        result = {
            "id": row.get("id", ""),
            "text": row.get("text", ""),
            "score": float(row.get("_distance", 0.0)),
            "metadata": row.get("metadata", {}),
        }
        
        # Add optional fields if present
        if "title" in row:
            result["title"] = row["title"]
        if "source" in row:
            result["source"] = row["source"]
        if "image_path" in row:
            result["image_path"] = row["image_path"]
            
        results.append(result)
    
    return results

def generate_response(query: str, context: List[Dict[str, Any]]) -> str:
    """Generate response using retrieved context.

    Args:
        query: User query
        context: Retrieved documents

    Returns:
        Formatted response with context (mock LLM call)
    """
    if not context:
        return "No relevant documents found to answer the query."
    
    # Format context for prompt
    context_text = "\n\n".join([
        f"Document {i+1} (Score: {doc['score']:.4f}):\n{doc['text']}"
        for i, doc in enumerate(context)
    ])
    
    # Mock LLM response - in production, this would call an actual LLM
    response = f"""Based on the retrieved context, here's the answer to your query:

Query: {query}

Retrieved Context:
{context_text}

Answer: [This is a mock response. In production, an LLM would generate a comprehensive answer based on the context above.]

The most relevant document has a similarity score of {context[0]['score']:.4f}, indicating {'high' if context[0]['score'] < 0.5 else 'moderate'} relevance to your query.
"""
    
    return response

def run_pipeline(query: str, k: int = 5) -> Dict[str, Any]:
    """Run the complete RAG pipeline.

    Args:
        query: User query string
        k: Number of documents to retrieve

    Returns:
        Dictionary containing search results and generated response
    """
    # Step 1: Search for relevant documents
    search_results = search(query, k=k)
    
    # Step 2: Generate response with context
    response = generate_response(query, search_results)
    
    # Step 3: Return complete pipeline output
    return {
        "query": query,
        "retrieved_documents": search_results,
        "response": response,
        "num_results": len(search_results)
    }

def create_fts_index(column: str = "text"):
    """Create full-text search index for hybrid search capabilities.
    
    Args:
        column: Column name to index for full-text search
    """
    global table
    if table is None:
        table = get_or_create_table()
    
    if table is not None:
        try:
            table.create_fts_index(column)
            print(f"Full-text search index created on column: {column}")
        except Exception as e:
            print(f"Note: FTS index creation skipped - {e}")

def hybrid_search(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Perform hybrid search combining vector and full-text search.
    
    Args:
        query: Search query text
        k: Number of results to return
        
    Returns:
        List of top-k matching documents
    """
    global table
    
    if table is None:
        table = get_or_create_table()
    
    if table is None:
        return []
    
    # Generate query embedding for vector search
    query_embedding = model.encode([query], convert_to_numpy=True)[0].tolist()
    
    try:
        # Attempt hybrid search
        results_df = (
            table.search(query, query_type="hybrid")
            .limit(k)
            .to_pandas()
        )
    except Exception:
        # Fall back to vector-only search if hybrid not available
        results_df = table.search(query_embedding).limit(k).to_pandas()
    
    # Convert to list of dictionaries
    results = []
    for _, row in results_df.iterrows():
        result = {
            "id": row.get("id", ""),
            "text": row.get("text", ""),
            "score": float(row.get("_distance", 0.0)),
            "metadata": row.get("metadata", {}),
        }
        results.append(result)
    
    return results

def main():
    """Example usage of the pipeline."""
    print("=" * 60)
    print("Multimodal CLIP Search Pipeline with LanceDB")
    print("=" * 60)
    
    # Sample documents with rich metadata
    sample_docs = [
        {
            "id": "doc_1",
            "text": "LanceDB is a vector database for AI applications.",
            "title": "LanceDB Overview",
            "metadata": {"category": "database", "importance": "high"}
        },
        {
            "id": "doc_2",
            "text": "Vector search enables semantic similarity matching.",
            "title": "Vector Search Basics",
            "metadata": {"category": "search", "importance": "high"}
        },
        {
            "id": "doc_3",
            "text": "RAG combines retrieval with generation for better answers.",
            "title": "RAG Architecture",
            "metadata": {"category": "ai", "importance": "high"}
        },
        {
            "id": "doc_4",
            "text": "CLIP models can process both text and images for multimodal search.",
            "title": "CLIP Multimodal",
            "metadata": {"category": "ai", "importance": "medium"}
        },
        {
            "id": "doc_5",
            "text": "Embeddings are dense vector representations of data.",
            "title": "Understanding Embeddings",
            "metadata": {"category": "ml", "importance": "medium"}
        }
    ]
    
    # Ingest documents
    print("\n1. Ingesting documents...")
    num_ingested = ingest_documents(sample_docs)
    print(f"   ✓ Successfully ingested {num_ingested} documents")
    
    # Create full-text search index for hybrid capabilities
    print("\n2. Creating full-text search index...")
    create_fts_index("text")
    
    # Run query through pipeline
    print("\n3. Running search pipeline...")
    query = "How does vector search work?"
    print(f"   Query: '{query}'")
    
    result = run_pipeline(query, k=3)
    
    print(f"\n4. Search Results ({result['num_results']} documents retrieved):")
    for i, doc in enumerate(result['retrieved_documents'], 1):
        print(f"\n   Document {i}:")
        print(f"   - ID: {doc['id']}")
        print(f"   - Title: {doc.get('title', 'N/A')}")
        print(f"   - Score: {doc['score']:.4f}")
        print(f"   - Text: {doc['text'][:80]}...")
    
    print("\n5. Generated Response:")
    print("-" * 60)
    print(result['response'])
    
    # Demonstrate hybrid search
    print("\n6. Testing Hybrid Search...")
    hybrid_results = hybrid_search("database vector", k=2)
    print(f"   Found {len(hybrid_results)} results using hybrid search")
    for i, doc in enumerate(hybrid_results, 1):
        print(f"   {i}. {doc.get('title', doc['id'])}: {doc['text'][:60]}...")
    
    print("\n" + "=" * 60)
    print("Pipeline execution completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()