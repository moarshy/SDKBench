# filepath: pipeline.py
"""FastAPI production RAG service.

Build a complete pipeline using LanceDB for vector storage.
"""

import lancedb
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import pyarrow as pa

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global configuration
DB_PATH = "./lancedb_data"
TABLE_NAME = "documents"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384  # Dimension for all-MiniLM-L6-v2

# Initialize embedding model (lazy loading)
_embedding_model: Optional[SentenceTransformer] = None

def get_embedding_model() -> SentenceTransformer:
    """Get or initialize the embedding model (singleton pattern)."""
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embedding_model

# Define document schema with vector field
def get_document_schema() -> pa.Schema:
    """Define PyArrow schema for documents with vector embeddings."""
    return pa.schema([
        pa.field("id", pa.int64()),
        pa.field("text", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), EMBEDDING_DIM)),
        pa.field("metadata", pa.string())  # JSON string for additional metadata
    ])

# Initialize database connection
def get_database() -> lancedb.DBConnection:
    """Initialize and return LanceDB connection."""
    try:
        db = lancedb.connect(DB_PATH)
        logger.info(f"Connected to LanceDB at {DB_PATH}")
        return db
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def generate_embeddings(texts: List[str], batch_size: int = 32) -> np.ndarray:
    """Generate embeddings for a list of texts with batching.
    
    Args:
        texts: List of text strings to embed
        batch_size: Batch size for embedding generation
        
    Returns:
        numpy array of embeddings
    """
    model = get_embedding_model()
    
    try:
        # Generate embeddings in batches for efficiency
        embeddings = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 100,
            convert_to_numpy=True,
            normalize_embeddings=True  # Normalize for cosine similarity
        )
        logger.info(f"Generated embeddings for {len(texts)} texts")
        return embeddings
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        raise

def ingest_documents(documents: List[Dict[str, Any]], batch_size: int = 100) -> int:
    """Ingest documents into the vector database.

    Args:
        documents: List of document dictionaries with 'text' field
        batch_size: Batch size for processing

    Returns:
        Number of documents ingested
    """
    if not documents:
        logger.warning("No documents to ingest")
        return 0
    
    try:
        db = get_database()
        
        # Extract texts and prepare data
        texts = [doc.get("text", "") for doc in documents]
        if not all(texts):
            raise ValueError("All documents must have a 'text' field")
        
        # Generate embeddings for all documents
        logger.info(f"Generating embeddings for {len(documents)} documents")
        embeddings = generate_embeddings(texts, batch_size=batch_size)
        
        # Prepare data for insertion
        data = []
        for idx, (doc, embedding) in enumerate(zip(documents, embeddings)):
            data.append({
                "id": idx,
                "text": doc["text"],
                "vector": embedding.tolist(),
                "metadata": str(doc.get("metadata", "{}"))
            })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Create or overwrite table with proper schema
        if TABLE_NAME in db.table_names():
            logger.info(f"Table '{TABLE_NAME}' exists, appending data")
            table = db.open_table(TABLE_NAME)
            table.add(df)
        else:
            logger.info(f"Creating new table '{TABLE_NAME}'")
            table = db.create_table(TABLE_NAME, df)
        
        # Create vector index for faster search
        logger.info("Creating vector index for optimized search")
        try:
            table.create_index(
                metric="cosine",
                num_partitions=max(1, len(documents) // 256),
                num_sub_vectors=min(96, EMBEDDING_DIM // 4)
            )
        except Exception as e:
            logger.warning(f"Index creation skipped or failed: {e}")
        
        logger.info(f"Successfully ingested {len(documents)} documents")
        return len(documents)
        
    except Exception as e:
        logger.error(f"Failed to ingest documents: {e}")
        raise

def search(query: str, k: int = 5, filter_condition: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search for relevant documents.

    Args:
        query: Search query text
        k: Number of results to return
        filter_condition: Optional SQL-like filter condition

    Returns:
        List of top-k results with text and scores
    """
    if not query:
        logger.warning("Empty query provided")
        return []
    
    try:
        db = get_database()
        
        # Check if table exists
        if TABLE_NAME not in db.table_names():
            logger.warning(f"Table '{TABLE_NAME}' does not exist")
            return []
        
        table = db.open_table(TABLE_NAME)
        
        # Generate query embedding
        logger.info(f"Searching for: '{query}'")
        query_embedding = generate_embeddings([query])[0]
        
        # Perform vector similarity search
        search_query = table.search(query_embedding).limit(k)
        
        # Apply filter if provided
        if filter_condition:
            search_query = search_query.where(filter_condition)
        
        # Execute search and convert to pandas
        results = search_query.to_pandas()
        
        # Format results
        formatted_results = []
        for _, row in results.iterrows():
            formatted_results.append({
                "id": int(row["id"]),
                "text": row["text"],
                "score": float(row.get("_distance", 0.0)),  # Distance score
                "metadata": row.get("metadata", "{}")
            })
        
        logger.info(f"Found {len(formatted_results)} results")
        return formatted_results
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise

def generate_response(query: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate response using retrieved context.

    Args:
        query: User query
        context: Retrieved documents

    Returns:
        Dictionary with formatted response
    """
    if not context:
        return {
            "query": query,
            "answer": "No relevant documents found to answer the query.",
            "sources": []
        }
    
    try:
        # Format context for prompt
        context_text = "\n\n".join([
            f"[Document {i+1}] {doc['text']}"
            for i, doc in enumerate(context)
        ])
        
        # Mock LLM response (in production, this would call an actual LLM)
        # For demonstration, we'll create a simple formatted response
        answer = f"""Based on the retrieved context, here's the answer to your query:

Query: {query}

Relevant Information:
{context_text}

Summary: The most relevant document states: "{context[0]['text']}"
"""
        
        # Prepare sources
        sources = [
            {
                "id": doc["id"],
                "text": doc["text"],
                "relevance_score": 1.0 - doc["score"]  # Convert distance to similarity
            }
            for doc in context
        ]
        
        response = {
            "query": query,
            "answer": answer,
            "sources": sources,
            "num_sources": len(sources)
        }
        
        logger.info(f"Generated response with {len(sources)} sources")
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate response: {e}")
        raise

def run_pipeline(query: str, k: int = 5) -> Dict[str, Any]:
    """Run the complete RAG pipeline.

    Args:
        query: User query
        k: Number of documents to retrieve

    Returns:
        Dictionary with query, answer, and sources
    """
    try:
        logger.info(f"Running RAG pipeline for query: '{query}'")
        
        # Step 1: Search for relevant documents
        search_results = search(query, k=k)
        
        # Step 2: Generate response with context
        response = generate_response(query, search_results)
        
        logger.info("Pipeline execution completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise

def get_table_stats() -> Dict[str, Any]:
    """Get statistics about the document table.
    
    Returns:
        Dictionary with table statistics
    """
    try:
        db = get_database()
        
        if TABLE_NAME not in db.table_names():
            return {"exists": False, "count": 0}
        
        table = db.open_table(TABLE_NAME)
        count = table.count_rows()
        
        return {
            "exists": True,
            "count": count,
            "table_name": TABLE_NAME,
            "embedding_dim": EMBEDDING_DIM
        }
    except Exception as e:
        logger.error(f"Failed to get table stats: {e}")
        return {"exists": False, "error": str(e)}

def main():
    """Example usage of the pipeline."""
    print("=" * 60)
    print("LanceDB RAG Pipeline - Production Example")
    print("=" * 60)
    
    # Sample documents
    sample_docs = [
        {
            "text": "LanceDB is a vector database for AI applications.",
            "metadata": {"category": "database", "source": "docs"}
        },
        {
            "text": "Vector search enables semantic similarity matching.",
            "metadata": {"category": "search", "source": "docs"}
        },
        {
            "text": "RAG combines retrieval with generation for better answers.",
            "metadata": {"category": "rag", "source": "docs"}
        },
        {
            "text": "Embeddings convert text into numerical vectors for comparison.",
            "metadata": {"category": "embeddings", "source": "docs"}
        },
        {
            "text": "Semantic search understands the meaning behind queries.",
            "metadata": {"category": "search", "source": "docs"}
        }
    ]
    
    try:
        # Ingest documents
        print("\n1. Ingesting documents...")
        num_ingested = ingest_documents(sample_docs)
        print(f"   ✓ Ingested {num_ingested} documents")
        
        # Get table statistics
        print("\n2. Table statistics:")
        stats = get_table_stats()
        print(f"   ✓ Documents in database: {stats['count']}")
        print(f"   ✓ Embedding dimension: {stats['embedding_dim']}")
        
        # Run queries through pipeline
        queries = [
            "What is LanceDB?",
            "How does semantic search work?",
            "Explain RAG systems"
        ]
        
        print("\n3. Running queries through RAG pipeline:")
        for query in queries:
            print(f"\n   Query: '{query}'")
            result = run_pipeline(query, k=3)
            print(f"   ✓ Found {result['num_sources']} relevant sources")
            print(f"   Top result: {result['sources'][0]['text'][:60]}...")
            print(f"   Relevance: {result['sources'][0]['relevance_score']:.3f}")
        
        print("\n" + "=" * 60)
        print("Pipeline ready for production use!")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise

if __name__ == "__main__":
    main()