# filepath: pipeline.py
"""Full hybrid search RAG pipeline.

Build a complete pipeline using LanceDB for vector storage.
"""

import lancedb
from sentence_transformers import SentenceTransformer
import pandas as pd
from typing import List, Dict, Any
import pyarrow as pa

# Initialize embedding model globally for reuse
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
EMBEDDING_DIM = 384  # Dimension for all-MiniLM-L6-v2

# Define document schema with vector field
schema = pa.schema([
    pa.field("id", pa.int64()),
    pa.field("text", pa.string()),
    pa.field("vector", pa.list_(pa.float32(), EMBEDDING_DIM)),
    pa.field("metadata", pa.string())
])

# Initialize database connection
db = lancedb.connect("./lancedb_rag")
TABLE_NAME = "documents"

def ingest_documents(documents: List[Dict[str, str]]) -> int:
    """Ingest documents into the vector database.

    Args:
        documents: List of document dictionaries with 'text' field

    Returns:
        Number of documents ingested
    """
    try:
        if not documents:
            print("No documents to ingest")
            return 0
        
        # Extract texts for batch embedding
        texts = [doc["text"] for doc in documents]
        
        # Generate embeddings for all documents in batch
        print(f"Generating embeddings for {len(texts)} documents...")
        embeddings = embedding_model.encode(texts, show_progress_bar=True)
        
        # Prepare data with schema
        data = []
        for idx, (doc, embedding) in enumerate(zip(documents, embeddings)):
            data.append({
                "id": idx,
                "text": doc["text"],
                "vector": embedding.tolist(),
                "metadata": doc.get("metadata", "")
            })
        
        # Create or overwrite table with documents
        if TABLE_NAME in db.table_names():
            print(f"Table '{TABLE_NAME}' exists, adding documents...")
            table = db.open_table(TABLE_NAME)
            table.add(data)
        else:
            print(f"Creating new table '{TABLE_NAME}'...")
            table = db.create_table(TABLE_NAME, data=data, schema=schema)
        
        # Create full-text search index for hybrid search
        try:
            table.create_fts_index("text", replace=True)
            print("Full-text search index created")
        except Exception as e:
            print(f"FTS index creation skipped: {e}")
        
        print(f"Successfully ingested {len(documents)} documents")
        return len(documents)
    
    except Exception as e:
        print(f"Error ingesting documents: {e}")
        raise

def search(query: str, k: int = 5, search_type: str = "vector") -> List[Dict[str, Any]]:
    """Search for relevant documents.

    Args:
        query: Search query text
        k: Number of results to return
        search_type: Type of search - "vector", "fts", or "hybrid"

    Returns:
        List of top-k results with text and scores
    """
    try:
        # Open the table
        if TABLE_NAME not in db.table_names():
            print("No documents in database. Please ingest documents first.")
            return []
        
        table = db.open_table(TABLE_NAME)
        
        if search_type == "vector":
            # Generate query embedding
            print(f"Generating query embedding for: '{query}'")
            query_embedding = embedding_model.encode(query)
            
            # Perform vector similarity search
            results = (
                table.search(query_embedding.tolist())
                .limit(k)
                .to_pandas()
            )
        
        elif search_type == "fts":
            # Full-text search
            print(f"Performing full-text search for: '{query}'")
            results = (
                table.search(query, query_type="fts")
                .limit(k)
                .to_pandas()
            )
        
        elif search_type == "hybrid":
            # Hybrid search combining vector and full-text
            print(f"Performing hybrid search for: '{query}'")
            query_embedding = embedding_model.encode(query)
            results = (
                table.search(query, query_type="hybrid")
                .vector(query_embedding.tolist())
                .limit(k)
                .to_pandas()
            )
        
        else:
            raise ValueError(f"Invalid search_type: {search_type}")
        
        # Convert results to list of dictionaries
        if results.empty:
            print("No results found")
            return []
        
        search_results = []
        for _, row in results.iterrows():
            result = {
                "text": row["text"],
                "score": row.get("_distance", row.get("score", 0.0)),
                "id": row.get("id", -1)
            }
            search_results.append(result)
        
        print(f"Found {len(search_results)} results")
        return search_results
    
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
    try:
        if not context:
            return "I don't have enough information to answer that question."
        
        # Format context for prompt
        context_text = "\n\n".join([
            f"[Document {i+1}]: {doc['text']}"
            for i, doc in enumerate(context)
        ])
        
        # Mock LLM response (in production, this would call an actual LLM)
        response = f"""Based on the retrieved context, here's the answer to your query:

Query: {query}

Relevant Context:
{context_text}

Answer: Based on the {len(context)} most relevant documents, I can provide information related to your query. The documents discuss topics including vector databases, semantic search, and retrieval-augmented generation (RAG) systems.

(Note: This is a mock response. In production, this would be generated by an LLM like GPT-4, Claude, or Llama.)
"""
        
        return response
    
    except Exception as e:
        print(f"Error generating response: {e}")
        raise

def run_pipeline(query: str, k: int = 5, search_type: str = "hybrid") -> Dict[str, Any]:
    """Run the complete RAG pipeline.

    Args:
        query: User query
        k: Number of documents to retrieve
        search_type: Type of search to perform

    Returns:
        Dictionary with query, retrieved context, and generated response
    """
    try:
        print(f"\n{'='*60}")
        print(f"Running RAG Pipeline")
        print(f"{'='*60}")
        
        # Step 1: Search for relevant documents
        print(f"\nStep 1: Retrieving relevant documents...")
        context = search(query, k=k, search_type=search_type)
        
        if not context:
            return {
                "query": query,
                "context": [],
                "response": "No relevant documents found."
            }
        
        # Step 2: Generate response with context
        print(f"\nStep 2: Generating response...")
        response = generate_response(query, context)
        
        # Return complete pipeline result
        result = {
            "query": query,
            "context": context,
            "response": response,
            "num_documents_retrieved": len(context)
        }
        
        print(f"\nPipeline completed successfully!")
        return result
    
    except Exception as e:
        print(f"Error in pipeline: {e}")
        raise

def main():
    """Example usage of the pipeline."""
    print("Initializing RAG Pipeline with LanceDB")
    print("="*60)
    
    # Sample documents with more content
    sample_docs = [
        {
            "text": "LanceDB is a vector database for AI applications. It provides fast vector similarity search and supports hybrid search combining vector and full-text search.",
            "metadata": "intro"
        },
        {
            "text": "Vector search enables semantic similarity matching by comparing embeddings in high-dimensional space. This allows finding conceptually similar content.",
            "metadata": "vector_search"
        },
        {
            "text": "RAG (Retrieval-Augmented Generation) combines retrieval with generation for better answers. It retrieves relevant context before generating responses.",
            "metadata": "rag"
        },
        {
            "text": "Embeddings are dense vector representations of text that capture semantic meaning. Models like sentence-transformers create these embeddings.",
            "metadata": "embeddings"
        },
        {
            "text": "Hybrid search combines multiple search methods like vector similarity and keyword matching to improve retrieval quality and relevance.",
            "metadata": "hybrid"
        }
    ]
    
    # Step 1: Ingest documents
    print("\n1. Ingesting documents...")
    num_ingested = ingest_documents(sample_docs)
    print(f"   ✓ Ingested {num_ingested} documents\n")
    
    # Step 2: Run queries through pipeline
    queries = [
        "What is LanceDB?",
        "How does semantic search work?",
        "Explain RAG systems"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}: {query}")
        print(f"{'='*60}")
        
        # Run pipeline with hybrid search
        result = run_pipeline(query, k=3, search_type="hybrid")
        
        # Print results
        print(f"\n📊 Retrieved {result['num_documents_retrieved']} documents:")
        for j, doc in enumerate(result['context'], 1):
            print(f"\n  Document {j} (score: {doc['score']:.4f}):")
            print(f"  {doc['text'][:100]}...")
        
        print(f"\n💬 Generated Response:")
        print(result['response'])
        print("\n")
    
    # Demonstrate different search types
    print(f"\n{'='*60}")
    print("Comparing Search Types")
    print(f"{'='*60}")
    
    test_query = "vector database"
    
    for search_type in ["vector", "hybrid"]:
        print(f"\n🔍 {search_type.upper()} Search:")
        results = search(test_query, k=2, search_type=search_type)
        for i, doc in enumerate(results, 1):
            print(f"  {i}. {doc['text'][:80]}... (score: {doc['score']:.4f})")
    
    print("\n" + "="*60)
    print("Pipeline demonstration complete!")
    print("="*60)

if __name__ == "__main__":
    main()