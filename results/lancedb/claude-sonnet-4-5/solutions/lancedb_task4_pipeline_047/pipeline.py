# filepath: pipeline.py
"""Full hybrid search RAG pipeline.

Build a complete pipeline using LanceDB for vector storage.
"""

import lancedb
from sentence_transformers import SentenceTransformer
import pandas as pd
from typing import List, Dict, Any
import pyarrow as pa
from datetime import datetime

# Initialize embedding model globally for efficiency
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
EMBEDDING_DIM = 384  # Dimension for all-MiniLM-L6-v2

# Define document schema with vector field
schema = pa.schema([
    pa.field("id", pa.int64()),
    pa.field("text", pa.utf8()),
    pa.field("vector", pa.list_(pa.float32(), EMBEDDING_DIM)),
    pa.field("timestamp", pa.timestamp('us')),
    pa.field("metadata", pa.string())
])

# Initialize database connection
db = lancedb.connect("./lancedb_rag")
TABLE_NAME = "documents"

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts.
    
    Args:
        texts: List of text strings
        
    Returns:
        List of embedding vectors
    """
    embeddings = embedding_model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()

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
        texts = [doc.get('text', '') for doc in documents]
        
        # Generate embeddings for all documents in batch
        print(f"Generating embeddings for {len(texts)} documents...")
        embeddings = generate_embeddings(texts)
        
        # Prepare data with schema
        data = []
        for idx, (doc, embedding) in enumerate(zip(documents, embeddings)):
            data.append({
                "id": idx,
                "text": doc.get('text', ''),
                "vector": embedding,
                "timestamp": datetime.now(),
                "metadata": doc.get('metadata', '')
            })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Create or overwrite table
        try:
            # Try to open existing table
            table = db.open_table(TABLE_NAME)
            # Add new documents to existing table
            table.add(df)
            print(f"Added {len(documents)} documents to existing table")
        except Exception:
            # Create new table if it doesn't exist
            table = db.create_table(TABLE_NAME, df, mode="overwrite")
            print(f"Created new table with {len(documents)} documents")
        
        # Create full-text search index for hybrid search
        try:
            table.create_fts_index("text", replace=True)
            print("Created full-text search index")
        except Exception as e:
            print(f"Note: FTS index creation skipped: {e}")
        
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
        # Open table
        table = db.open_table(TABLE_NAME)
        
        if search_type == "vector":
            # Generate query embedding
            print(f"Performing vector search for: '{query}'")
            query_embedding = generate_embeddings([query])[0]
            
            # Perform vector similarity search
            results = (
                table.search(query_embedding)
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
            query_embedding = generate_embeddings([query])[0]
            
            try:
                results = (
                    table.search(query, query_type="hybrid")
                    .vector(query_embedding)
                    .limit(k)
                    .to_pandas()
                )
            except Exception as e:
                # Fallback to vector search if hybrid not available
                print(f"Hybrid search not available, using vector search: {e}")
                results = (
                    table.search(query_embedding)
                    .limit(k)
                    .to_pandas()
                )
        else:
            raise ValueError(f"Unknown search type: {search_type}")
        
        # Convert results to list of dictionaries
        output = []
        for _, row in results.iterrows():
            output.append({
                "text": row["text"],
                "score": row.get("_distance", row.get("score", 0.0)),
                "id": row.get("id", -1)
            })
        
        print(f"Found {len(output)} results")
        return output
        
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
    # Format context for prompt
    context_text = "\n\n".join([
        f"[Document {i+1}] {doc['text']}"
        for i, doc in enumerate(context)
    ])
    
    # Mock LLM response (in production, this would call an actual LLM)
    response = f"""Based on the retrieved context, here's the answer to your query:

Query: {query}

Retrieved Context:
{context_text}

Answer: Based on the {len(context)} most relevant documents, {context[0]['text'] if context else 'no relevant information was found.'}

(Note: This is a mock response. In production, this would be generated by an LLM like GPT-4, Claude, or Llama.)
"""
    
    return response

def run_pipeline(query: str, k: int = 5, search_type: str = "vector") -> Dict[str, Any]:
    """Run the complete RAG pipeline.

    Args:
        query: User query
        k: Number of documents to retrieve
        search_type: Type of search to perform

    Returns:
        Dictionary with query, context, and response
    """
    print(f"\n{'='*60}")
    print(f"Running RAG Pipeline")
    print(f"{'='*60}")
    
    # Step 1: Search for relevant documents
    print(f"\nStep 1: Retrieving relevant documents...")
    context = search(query, k=k, search_type=search_type)
    
    # Step 2: Generate response with context
    print(f"\nStep 2: Generating response...")
    response = generate_response(query, context)
    
    # Return complete pipeline output
    return {
        "query": query,
        "context": context,
        "response": response,
        "num_results": len(context)
    }

def main():
    """Example usage of the pipeline."""
    print("Initializing RAG Pipeline with LanceDB...")
    
    # Sample documents
    sample_docs = [
        {
            "text": "LanceDB is a vector database for AI applications.",
            "metadata": "intro"
        },
        {
            "text": "Vector search enables semantic similarity matching.",
            "metadata": "concept"
        },
        {
            "text": "RAG combines retrieval with generation for better answers.",
            "metadata": "architecture"
        },
        {
            "text": "Embeddings convert text into numerical vectors for similarity comparison.",
            "metadata": "technical"
        },
        {
            "text": "Hybrid search combines vector similarity with keyword matching for improved results.",
            "metadata": "advanced"
        },
        {
            "text": "LanceDB supports full-text search and vector search in a single query.",
            "metadata": "features"
        }
    ]

    # Ingest documents
    print("\n" + "="*60)
    print("Ingesting Documents")
    print("="*60)
    num_ingested = ingest_documents(sample_docs)
    print(f"\nSuccessfully ingested {num_ingested} documents")

    # Example queries
    queries = [
        "What is LanceDB?",
        "How does vector search work?",
        "Explain RAG architecture"
    ]

    # Run queries through pipeline
    for query in queries:
        result = run_pipeline(query, k=3, search_type="vector")
        print(f"\n{result['response']}")
        print(f"\nRetrieved {result['num_results']} documents")
        print("="*60)

    print("\n✓ Pipeline ready and tested successfully!")

if __name__ == "__main__":
    main()