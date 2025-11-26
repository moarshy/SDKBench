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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global configuration
DB_PATH = "./lancedb_data"
TABLE_NAME = "documents"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast and efficient model
EMBEDDING_DIM = 384  # Dimension for all-MiniLM-L6-v2

# Initialize embedding model (lazy loading)
_embedding_model: Optional[SentenceTransformer] = None

def get_embedding_model() -> SentenceTransformer:
    """Get or initialize the embedding model (singleton pattern)."""
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully")
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
        db_path = Path(DB_PATH)
        db_path.mkdir(parents=True, exist_ok=True)
        db = lancedb.connect(DB_PATH)
        logger.info(f"Connected to LanceDB at {DB_PATH}")
        return db
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def generate_embeddings(texts: List[str], batch_size: int = 32) -> np.ndarray:
    """Generate embeddings for a list of texts efficiently.
    
    Args:
        texts: List of text strings to embed
        batch_size: Batch size for embedding generation
        
    Returns:
        numpy array of embeddings
    """
    try:
        model = get_embedding_model()
        logger.info(f"Generating embeddings for {len(texts)} texts")
        
        # Generate embeddings in batches for efficiency
        embeddings = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 100,
            convert_to_numpy=True,
            normalize_embeddings=True  # Normalize for cosine similarity
        )
        
        logger.info(f"Generated embeddings with shape: {embeddings.shape}")
        return embeddings
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise

def ingest_documents(documents: List[Dict[str, Any]], batch_size: int = 100) -> int:
    """Ingest documents into the vector database.

    Args:
        documents: List of document dictionaries with 'text' field
        batch_size: Batch size for processing
        
    Returns:
        Number of documents ingested
        
    Raises:
        ValueError: If documents are invalid
        Exception: If ingestion fails
    """
    if not documents:
        logger.warning("No documents provided for ingestion")
        return 0
    
    # Validate documents
    for i, doc in enumerate(documents):
        if 'text' not in doc or not doc['text']:
            raise ValueError(f"Document at index {i} missing 'text' field")
    
    try:
        logger.info(f"Starting ingestion of {len(documents)} documents")
        
        # Extract texts for embedding
        texts = [doc['text'] for doc in documents]
        
        # Generate embeddings efficiently
        embeddings = generate_embeddings(texts, batch_size=batch_size)
        
        # Prepare data for LanceDB
        data = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            data.append({
                "id": i,
                "text": doc['text'],
                "vector": embedding.tolist(),
                "metadata": doc.get('metadata', '{}')
            })
        
        # Convert to pandas DataFrame for LanceDB
        df = pd.DataFrame(data)
        
        # Connect to database
        db = get_database()
        
        # Create or overwrite table
        if TABLE_NAME in db.table_names():
            logger.info(f"Table '{TABLE_NAME}' exists, appending data")
            table = db.open_table(TABLE_NAME)
            table.add(df)
        else:
            logger.info(f"Creating new table '{TABLE_NAME}'")
            table = db.create_table(TABLE_NAME, df)
        
        # Create index for faster search (IVF_PQ for production)
        try:
            logger.info("Creating vector index for optimized search")
            table.create_index(
                metric="cosine",
                num_partitions=max(2, len(documents) // 100),  # Adaptive partitioning
                num_sub_vectors=min(96, EMBEDDING_DIM // 4)  # Adaptive sub-vectors
            )
        except Exception as e:
            logger.warning(f"Index creation skipped or failed: {e}")
        
        logger.info(f"Successfully ingested {len(documents)} documents")
        return len(documents)
        
    except Exception as e:
        logger.error(f"Error during document ingestion: {e}")
        raise

def search(query: str, k: int = 5, score_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
    """Search for relevant documents using vector similarity.

    Args:
        query: Search query text
        k: Number of results to return
        score_threshold: Optional minimum similarity score (0-1)
        
    Returns:
        List of top-k results with text and scores
        
    Raises:
        ValueError: If query is empty
        Exception: If search fails
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    
    try:
        logger.info(f"Searching for: '{query}' (top {k} results)")
        
        # Generate query embedding
        query_embedding = generate_embeddings([query])[0]
        
        # Connect to database and open table
        db = get_database()
        
        if TABLE_NAME not in db.table_names():
            logger.warning(f"Table '{TABLE_NAME}' does not exist")
            return []
        
        table = db.open_table(TABLE_NAME)
        
        # Perform vector similarity search
        results = (
            table.search(query_embedding.tolist())
            .metric("cosine")
            .limit(k)
            .to_pandas()
        )
        
        # Format results
        formatted_results = []
        for _, row in results.iterrows():
            score = float(row.get('_distance', 0))
            # Convert distance to similarity score (cosine distance -> similarity)
            similarity = 1 - score
            
            # Apply score threshold if specified
            if score_threshold is not None and similarity < score_threshold:
                continue
            
            formatted_results.append({
                "id": int(row['id']),
                "text": row['text'],
                "score": similarity,
                "metadata": row.get('metadata', '{}')
            })
        
        logger.info(f"Found {len(formatted_results)} relevant documents")
        return formatted_results
        
    except Exception as e:
        logger.error(f"Error during search: {e}")
        raise

def generate_response(query: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate response using retrieved context.

    Args:
        query: User query
        context: Retrieved documents with text and scores
        
    Returns:
        Dictionary with generated response and metadata
    """
    try:
        logger.info(f"Generating response for query: '{query}'")
        
        if not context:
            return {
                "answer": "I don't have enough information to answer this question.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Format context for prompt
        context_text = "\n\n".join([
            f"[Source {i+1}] (Score: {doc['score']:.3f})\n{doc['text']}"
            for i, doc in enumerate(context)
        ])
        
        # Mock LLM response (in production, call actual LLM API)
        # This simulates a RAG response format
        prompt = f"""Based on the following context, answer the question.

Context:
{context_text}

Question: {query}

Answer:"""
        
        # Calculate confidence based on top result score
        confidence = context[0]['score'] if context else 0.0
        
        # Mock response (replace with actual LLM call in production)
        answer = f"Based on the retrieved context, here's what I found: {context[0]['text'][:200]}..."
        
        response = {
            "answer": answer,
            "sources": [
                {
                    "text": doc['text'],
                    "score": doc['score'],
                    "id": doc['id']
                }
                for doc in context
            ],
            "confidence": confidence,
            "num_sources": len(context),
            "prompt": prompt  # Include for debugging/logging
        }
        
        logger.info(f"Generated response with {len(context)} sources")
        return response
        
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        raise

def run_pipeline(query: str, k: int = 5, score_threshold: float = 0.3) -> Dict[str, Any]:
    """Run the complete RAG pipeline.
    
    Args:
        query: User query string
        k: Number of documents to retrieve
        score_threshold: Minimum similarity score for results
        
    Returns:
        Dictionary with answer, sources, and metadata
        
    Raises:
        ValueError: If query is invalid
        Exception: If pipeline fails
    """
    try:
        logger.info(f"Running RAG pipeline for query: '{query}'")
        
        # Step 1: Search for relevant documents
        search_results = search(query, k=k, score_threshold=score_threshold)
        
        # Step 2: Generate response with context
        response = generate_response(query, search_results)
        
        # Add pipeline metadata
        response['pipeline_metadata'] = {
            "query": query,
            "k": k,
            "score_threshold": score_threshold,
            "documents_retrieved": len(search_results)
        }
        
        logger.info("RAG pipeline completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise

def main():
    """Example usage of the pipeline."""
    try:
        # Sample documents with more diverse content
        sample_docs = [
            {
                "text": "LanceDB is a vector database for AI applications. It provides fast vector search and is optimized for machine learning workloads.",
                "metadata": '{"source": "documentation", "category": "database"}'
            },
            {
                "text": "Vector search enables semantic similarity matching. It uses embeddings to find similar items based on meaning rather than exact keywords.",
                "metadata": '{"source": "tutorial", "category": "search"}'
            },
            {
                "text": "RAG combines retrieval with generation for better answers. It retrieves relevant context and uses it to generate more accurate responses.",
                "metadata": '{"source": "guide", "category": "rag"}'
            },
            {
                "text": "Embeddings are numerical representations of text that capture semantic meaning. They enable machines to understand and compare text.",
                "metadata": '{"source": "documentation", "category": "embeddings"}'
            },
            {
                "text": "Sentence transformers are neural networks that generate high-quality embeddings for sentences and paragraphs.",
                "metadata": '{"source": "research", "category": "models"}'
            }
        ]

        # Ingest documents
        print("=" * 60)
        print("INGESTING DOCUMENTS")
        print("=" * 60)
        num_ingested = ingest_documents(sample_docs)
        print(f"✓ Ingested {num_ingested} documents successfully\n")

        # Test queries
        test_queries = [
            "What is LanceDB?",
            "How does vector search work?",
            "Explain RAG systems"
        ]

        for query in test_queries:
            print("=" * 60)
            print(f"QUERY: {query}")
            print("=" * 60)
            
            # Run query through pipeline
            result = run_pipeline(query, k=3, score_threshold=0.2)
            
            print(f"\nAnswer: {result['answer']}")
            print(f"\nConfidence: {result['confidence']:.3f}")
            print(f"\nTop Sources:")
            for i, source in enumerate(result['sources'][:3], 1):
                print(f"  {i}. [Score: {source['score']:.3f}] {source['text'][:100]}...")
            print()

        print("=" * 60)
        print("Pipeline ready and tested successfully!")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()