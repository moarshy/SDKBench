# filepath: search.py
"""Search with LinearCombinationReranker."""

import lancedb
from lancedb.rerankers import LinearCombinationReranker
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
import pandas as pd
from typing import List, Optional

# Get embedding model
model = get_registry().get("sentence-transformers").create(name="all-MiniLM-L6-v2")

class Document(LanceModel):
    """Document schema with vector and text fields."""
    text: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()
    category: Optional[str] = None

def setup_database():
    """Create and populate a sample database for testing."""
    # Connect to database
    db = lancedb.connect("./lancedb_rerank")
    
    # Sample data
    data = [
        {"text": "Python is a high-level programming language", "category": "programming"},
        {"text": "Machine learning uses algorithms to learn from data", "category": "ai"},
        {"text": "LanceDB is a vector database for AI applications", "category": "database"},
        {"text": "Neural networks are inspired by biological neurons", "category": "ai"},
        {"text": "Python has extensive libraries for data science", "category": "programming"},
        {"text": "Vector embeddings represent text in high-dimensional space", "category": "ai"},
        {"text": "Databases store and retrieve structured data efficiently", "category": "database"},
        {"text": "Deep learning is a subset of machine learning", "category": "ai"},
        {"text": "Python's syntax is clean and readable", "category": "programming"},
        {"text": "SQL databases use structured query language", "category": "database"},
    ]
    
    # Create table with full-text search index
    try:
        table = db.create_table("documents", schema=Document, mode="overwrite")
        table.add(data)
        
        # Create full-text search index for hybrid search
        table.create_fts_index("text", replace=True)
        
        return db, table
    except Exception as e:
        print(f"Error setting up database: {e}")
        raise

def search_with_rerank(
    table,
    query_text: str,
    query_vector=None,
    k: int = 10,
    weight: float = 0.7
):
    """Search with linear combination reranking.
    
    Args:
        table: LanceDB table to search
        query_text: Text query for full-text search
        query_vector: Optional pre-computed query vector
        k: Number of results to return
        weight: Weight for linear combination (0-1)
                Higher weight favors vector search over text search
    
    Returns:
        DataFrame with reranked search results
    
    The LinearCombinationReranker combines vector similarity scores
    and full-text search scores using the formula:
    final_score = weight * vector_score + (1 - weight) * text_score
    """
    try:
        # 1. Create LinearCombinationReranker with specified weight
        # weight=0.7 means 70% vector similarity, 30% text relevance
        reranker = LinearCombinationReranker(weight=weight)
        
        # 2. Perform hybrid search with reranking
        # Hybrid search combines vector similarity and full-text search
        if query_vector is None:
            # If no vector provided, use the text to generate one
            results = (
                table.search(query_text, query_type="hybrid")
                .rerank(reranker=reranker)
                .limit(k)
                .to_pandas()
            )
        else:
            # Use provided vector for vector search component
            results = (
                table.search(query_text, query_type="hybrid")
                .vector(query_vector)
                .rerank(reranker=reranker)
                .limit(k)
                .to_pandas()
            )
        
        # 3. Return reranked results
        # Results are sorted by the combined score
        return results
        
    except Exception as e:
        print(f"Error during search: {e}")
        raise

def search_with_different_weights(table, query_text: str, k: int = 5):
    """Demonstrate how different weights affect results."""
    print(f"\n{'='*80}")
    print(f"Query: '{query_text}'")
    print(f"{'='*80}\n")
    
    weights = [0.3, 0.5, 0.7, 0.9]
    
    for weight in weights:
        print(f"\n--- Weight: {weight} (Vector: {weight*100:.0f}%, Text: {(1-weight)*100:.0f}%) ---")
        results = search_with_rerank(
            table=table,
            query_text=query_text,
            k=k,
            weight=weight
        )
        
        if not results.empty:
            for idx, row in results.iterrows():
                score = row.get('_relevance_score', row.get('score', 'N/A'))
                print(f"{idx+1}. [{row['category']}] {row['text'][:60]}... (score: {score:.4f})")
        else:
            print("No results found")

def main():
    """Main function to demonstrate reranked search."""
    try:
        # Setup database with sample data
        print("Setting up database...")
        db, table = setup_database()
        
        # Example 1: Basic reranked search
        print("\n" + "="*80)
        print("Example 1: Basic Reranked Search")
        print("="*80)
        
        query = "Python programming language"
        results = search_with_rerank(
            table=table,
            query_text=query,
            k=5,
            weight=0.7
        )
        
        print(f"\nQuery: '{query}'")
        print(f"Top {len(results)} results with reranking (weight=0.7):\n")
        
        for idx, row in results.iterrows():
            score = row.get('_relevance_score', row.get('score', 'N/A'))
            print(f"{idx+1}. [{row['category']}] {row['text']}")
            print(f"   Score: {score:.4f}\n")
        
        # Example 2: Compare different weights
        print("\n" + "="*80)
        print("Example 2: Comparing Different Reranking Weights")
        print("="*80)
        
        search_with_different_weights(
            table=table,
            query_text="machine learning algorithms",
            k=3
        )
        
        # Example 3: Search with filter
        print("\n" + "="*80)
        print("Example 3: Reranked Search with Filter")
        print("="*80)
        
        query = "data and algorithms"
        reranker = LinearCombinationReranker(weight=0.6)
        
        results = (
            table.search(query, query_type="hybrid")
            .where("category = 'ai'", prefilter=True)
            .rerank(reranker=reranker)
            .limit(3)
            .to_pandas()
        )
        
        print(f"\nQuery: '{query}' (filtered to category='ai')")
        print(f"Results with reranking (weight=0.6):\n")
        
        for idx, row in results.iterrows():
            score = row.get('_relevance_score', row.get('score', 'N/A'))
            print(f"{idx+1}. [{row['category']}] {row['text']}")
            print(f"   Score: {score:.4f}\n")
        
        print("="*80)
        print("Reranked search complete")
        print("="*80)
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()