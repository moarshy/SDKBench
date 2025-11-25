# filepath: search.py
"""Search with LinearCombinationReranker."""

import lancedb
from lancedb.rerankers import LinearCombinationReranker
import numpy as np
import pandas as pd


def search_with_rerank(query_text: str, query_vector, k: int = 10):
    """Search with linear combination reranking.

    Args:
        query_text: Text query for full-text search
        query_vector: Vector embedding for vector search
        k: Number of results to return

    Returns:
        pandas.DataFrame: Reranked search results
    """
    try:
        # Connect to the database
        db = lancedb.connect("./my_lancedb")
        
        # Open the table (assuming it exists and has FTS index)
        table = db.open_table("documents")
        
        # Create LinearCombinationReranker with weight=0.7
        # weight=0.7 means 70% vector search, 30% text search
        reranker = LinearCombinationReranker(weight=0.7)
        
        # Perform hybrid search with reranking
        # The reranker combines vector similarity scores and text search scores
        results = (
            table.search(query=query_text, query_type="hybrid")
            .vector(query_vector)
            .limit(k)
            .rerank(reranker=reranker)
            .to_pandas()
        )
        
        return results
        
    except Exception as e:
        print(f"Error during search with reranking: {e}")
        raise


def setup_sample_data():
    """Setup sample data for demonstration."""
    try:
        # Connect to database
        db = lancedb.connect("./my_lancedb")
        
        # Create sample data with vectors and text
        data = [
            {
                "id": 1,
                "text": "Python is a high-level programming language",
                "vector": np.random.randn(128).tolist(),
                "category": "programming"
            },
            {
                "id": 2,
                "text": "Machine learning uses algorithms to learn patterns",
                "vector": np.random.randn(128).tolist(),
                "category": "ai"
            },
            {
                "id": 3,
                "text": "LanceDB is a vector database for AI applications",
                "vector": np.random.randn(128).tolist(),
                "category": "database"
            },
            {
                "id": 4,
                "text": "Deep learning is a subset of machine learning",
                "vector": np.random.randn(128).tolist(),
                "category": "ai"
            },
            {
                "id": 5,
                "text": "Python libraries like pandas help with data analysis",
                "vector": np.random.randn(128).tolist(),
                "category": "programming"
            }
        ]
        
        # Create table
        if "documents" in db.table_names():
            db.drop_table("documents")
        
        table = db.create_table("documents", data)
        
        # Create full-text search index on the text column
        table.create_fts_index("text")
        
        print("Sample data setup complete")
        return table
        
    except Exception as e:
        print(f"Error setting up sample data: {e}")
        raise


def main():
    """Main function to demonstrate linear combination reranking."""
    try:
        # Setup sample data
        print("Setting up sample data...")
        setup_sample_data()
        
        # Create a query
        query_text = "machine learning algorithms"
        query_vector = np.random.randn(128).tolist()
        
        print(f"\nSearching for: '{query_text}'")
        print("Using LinearCombinationReranker with weight=0.7")
        print("(70% vector similarity, 30% text relevance)\n")
        
        # Perform search with reranking
        results = search_with_rerank(
            query_text=query_text,
            query_vector=query_vector,
            k=5
        )
        
        # Display results
        print("Reranked search results:")
        print("=" * 80)
        
        if not results.empty:
            for idx, row in results.iterrows():
                print(f"\nRank {idx + 1}:")
                print(f"  ID: {row['id']}")
                print(f"  Text: {row['text']}")
                print(f"  Category: {row['category']}")
                if '_relevance_score' in row:
                    print(f"  Relevance Score: {row['_relevance_score']:.4f}")
        else:
            print("No results found")
        
        print("\n" + "=" * 80)
        print("Reranked search complete")
        
        # Demonstrate different weight values
        print("\n\nDemonstrating different reranker weights:")
        print("=" * 80)
        
        for weight in [0.3, 0.5, 0.7, 0.9]:
            print(f"\nWeight={weight} ({int(weight*100)}% vector, {int((1-weight)*100)}% text):")
            
            db = lancedb.connect("./my_lancedb")
            table = db.open_table("documents")
            reranker = LinearCombinationReranker(weight=weight)
            
            results = (
                table.search(query=query_text, query_type="hybrid")
                .vector(query_vector)
                .limit(3)
                .rerank(reranker=reranker)
                .to_pandas()
            )
            
            for idx, row in results.iterrows():
                print(f"  {idx + 1}. {row['text'][:50]}...")
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    main()