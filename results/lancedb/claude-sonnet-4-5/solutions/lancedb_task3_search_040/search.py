# filepath: search.py
"""HYDE - Hypothetical Document Embeddings."""

import lancedb
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import os

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_hypothetical_answer(query: str) -> str:
    """Generate hypothetical answer using LLM.
    
    For this implementation, we'll use a mock LLM response.
    In production, replace with actual OpenAI/Anthropic API calls.
    
    Args:
        query: The user's question
        
    Returns:
        A hypothetical answer to the query
    """
    # Mock LLM response - in production, use:
    # from openai import OpenAI
    # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # response = client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": "You are a helpful assistant. Answer the question directly and concisely."},
    #         {"role": "user", "content": f"Answer this question: {query}"}
    #     ]
    # )
    # return response.choices[0].message.content
    
    # Mock responses for demonstration
    mock_responses = {
        "what is machine learning": "Machine learning is a subset of artificial intelligence that enables computers to learn from data and improve their performance without being explicitly programmed. It uses algorithms to identify patterns in data and make predictions or decisions.",
        "how does photosynthesis work": "Photosynthesis is the process by which plants convert light energy into chemical energy. Plants use chlorophyll to capture sunlight, then combine carbon dioxide from the air with water from the soil to produce glucose and oxygen.",
        "explain quantum computing": "Quantum computing is a type of computation that harnesses quantum mechanical phenomena like superposition and entanglement. Unlike classical computers that use bits (0 or 1), quantum computers use qubits that can exist in multiple states simultaneously, enabling them to solve certain problems exponentially faster."
    }
    
    # Return mock response or generate a generic one
    query_lower = query.lower().strip()
    if query_lower in mock_responses:
        return mock_responses[query_lower]
    else:
        return f"This is a hypothetical answer about {query}. It provides detailed information and context that would typically appear in a relevant document."


def create_sample_database(db_path: str = "./hyde_lancedb") -> lancedb.db.LanceDBConnection:
    """Create a sample database with documents for testing.
    
    Args:
        db_path: Path to the LanceDB database
        
    Returns:
        LanceDB connection object
    """
    # Sample documents about various topics
    documents = [
        {
            "id": 1,
            "text": "Machine learning is a branch of artificial intelligence focused on building systems that learn from data. These systems improve their performance over time without explicit programming. Common techniques include supervised learning, unsupervised learning, and reinforcement learning.",
            "category": "AI"
        },
        {
            "id": 2,
            "text": "Deep learning uses neural networks with multiple layers to process data. It has revolutionized fields like computer vision, natural language processing, and speech recognition. Deep learning models can automatically learn hierarchical representations of data.",
            "category": "AI"
        },
        {
            "id": 3,
            "text": "Photosynthesis occurs in plant cells, specifically in chloroplasts. The process has two main stages: light-dependent reactions and the Calvin cycle. During photosynthesis, plants absorb carbon dioxide and release oxygen as a byproduct.",
            "category": "Biology"
        },
        {
            "id": 4,
            "text": "Quantum computers leverage quantum mechanics principles to perform calculations. They use qubits which can be in superposition, representing both 0 and 1 simultaneously. This allows quantum computers to explore multiple solutions in parallel.",
            "category": "Physics"
        },
        {
            "id": 5,
            "text": "Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes (neurons) organized in layers. Each connection has a weight that adjusts during training to minimize prediction errors.",
            "category": "AI"
        },
        {
            "id": 6,
            "text": "Chlorophyll is the green pigment in plants that captures light energy during photosynthesis. It absorbs light most efficiently in the blue and red wavelengths, which is why plants appear green to our eyes.",
            "category": "Biology"
        },
        {
            "id": 7,
            "text": "Quantum entanglement is a phenomenon where particles become correlated in such a way that the quantum state of one particle cannot be described independently of the others. This property is fundamental to quantum computing and quantum cryptography.",
            "category": "Physics"
        }
    ]
    
    # Generate embeddings for all documents
    texts = [doc["text"] for doc in documents]
    embeddings = embedding_model.encode(texts)
    
    # Add embeddings to documents
    for doc, embedding in zip(documents, embeddings):
        doc["vector"] = embedding.tolist()
    
    # Create or connect to database
    db = lancedb.connect(db_path)
    
    # Create table (drop if exists)
    try:
        db.drop_table("documents")
    except Exception:
        pass
    
    table = db.create_table("documents", data=documents)
    
    print(f"Created database with {len(documents)} documents")
    return db


def hyde_search(
    query: str, 
    db: lancedb.db.LanceDBConnection,
    k: int = 10,
    use_hyde: bool = True
) -> pd.DataFrame:
    """Search using HYDE pattern.
    
    HYDE improves retrieval by:
    1. Generating a hypothetical answer to the query
    2. Embedding the hypothetical answer (not the query)
    3. Searching for documents similar to the hypothetical answer
    
    This works because the hypothetical answer is more similar to
    actual documents than the query itself.
    
    Args:
        query: The user's search query
        db: LanceDB connection
        k: Number of results to return
        use_hyde: If True, use HYDE; if False, use direct query embedding
        
    Returns:
        DataFrame with search results
    """
    try:
        # Open the documents table
        table = db.open_table("documents")
        
        if use_hyde:
            # Step 1: Generate hypothetical answer with LLM
            print(f"\n🔍 Original Query: {query}")
            hypothetical_answer = generate_hypothetical_answer(query)
            print(f"\n💡 Hypothetical Answer:\n{hypothetical_answer}")
            
            # Step 2: Embed the hypothetical answer (not the query!)
            search_text = hypothetical_answer
        else:
            # Direct search without HYDE
            print(f"\n🔍 Direct Query: {query}")
            search_text = query
        
        # Step 3: Generate embedding for search
        query_embedding = embedding_model.encode(search_text)
        
        # Step 4: Search using the embedding
        results = (
            table.search(query_embedding.tolist())
            .limit(k)
            .to_pandas()
        )
        
        # Calculate and display similarity scores
        if len(results) > 0:
            # Add distance as similarity score (lower distance = higher similarity)
            results['similarity'] = 1 / (1 + results['_distance'])
            
            print(f"\n📊 Top {min(k, len(results))} Results:")
            print("=" * 80)
            
            for idx, row in results.head(k).iterrows():
                print(f"\nRank {idx + 1} (Similarity: {row['similarity']:.4f})")
                print(f"Category: {row['category']}")
                print(f"Text: {row['text'][:150]}...")
                print("-" * 80)
        
        return results
        
    except Exception as e:
        print(f"Error during search: {e}")
        raise


def compare_hyde_vs_direct(query: str, db: lancedb.db.LanceDBConnection, k: int = 3):
    """Compare HYDE search vs direct query search.
    
    Args:
        query: The search query
        db: LanceDB connection
        k: Number of results to return
    """
    print("\n" + "=" * 80)
    print("COMPARISON: HYDE vs Direct Search")
    print("=" * 80)
    
    # HYDE search
    print("\n🎯 HYDE SEARCH (using hypothetical answer)")
    print("-" * 80)
    hyde_results = hyde_search(query, db, k=k, use_hyde=True)
    
    # Direct search
    print("\n\n🎯 DIRECT SEARCH (using original query)")
    print("-" * 80)
    direct_results = hyde_search(query, db, k=k, use_hyde=False)
    
    # Summary
    print("\n\n📈 SUMMARY")
    print("=" * 80)
    print("HYDE typically performs better because:")
    print("1. Hypothetical answers are more similar to actual documents")
    print("2. Queries are often short and lack context")
    print("3. Answer-to-answer matching is more effective than question-to-answer")
    print("=" * 80)


def main():
    """Main function to demonstrate HYDE search."""
    print("🚀 HYDE (Hypothetical Document Embeddings) Search Demo")
    print("=" * 80)
    
    # Create sample database
    db_path = "./hyde_lancedb"
    db = create_sample_database(db_path)
    
    # Example queries
    queries = [
        "what is machine learning",
        "how does photosynthesis work",
        "explain quantum computing"
    ]
    
    # Run HYDE search for each query
    for query in queries:
        print("\n\n" + "=" * 80)
        print(f"Query: {query}")
        print("=" * 80)
        
        results = hyde_search(query, db, k=3, use_hyde=True)
    
    # Compare HYDE vs Direct search
    print("\n\n" + "=" * 80)
    print("DETAILED COMPARISON")
    print("=" * 80)
    compare_hyde_vs_direct("what is machine learning", db, k=3)
    
    print("\n\n✅ HYDE search complete")
    print("\nTo use with real LLM:")
    print("1. Set OPENAI_API_KEY environment variable")
    print("2. Uncomment OpenAI client code in generate_hypothetical_answer()")
    print("3. Replace mock responses with actual API calls")


if __name__ == "__main__":
    main()