# filepath: data_ops.py
"""Handle token limits with chunking."""

import re
import lancedb
import tiktoken
import pandas as pd
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

MAX_TOKENS = 8192

def count_tokens(text: str, model: str = "cl100k_base") -> int:
    """Count tokens in text.
    
    Args:
        text: Input text to count tokens
        model: Tiktoken encoding model name
        
    Returns:
        Number of tokens in the text
    """
    try:
        encoding = tiktoken.get_encoding(model)
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        print(f"Error counting tokens: {e}")
        # Fallback to rough estimation (1 token ≈ 4 chars)
        return len(text) // 4


def chunk_text(text: str, max_tokens: int = MAX_TOKENS, model: str = "cl100k_base") -> List[str]:
    """Chunk text to fit token limit.
    
    Args:
        text: Input text to chunk
        max_tokens: Maximum tokens per chunk
        model: Tiktoken encoding model name
        
    Returns:
        List of text chunks, each under max_tokens
    """
    # Split text into sentences using regex
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    encoding = tiktoken.get_encoding(model)
    
    for sentence in sentences:
        # Count tokens in the sentence
        sentence_tokens = len(encoding.encode(sentence))
        
        # If single sentence exceeds max_tokens, split it further
        if sentence_tokens > max_tokens:
            # If we have accumulated content, save it first
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_tokens = 0
            
            # Split long sentence by words
            words = sentence.split()
            word_chunk = []
            word_tokens = 0
            
            for word in words:
                word_token_count = len(encoding.encode(word + ' '))
                
                if word_tokens + word_token_count > max_tokens:
                    if word_chunk:
                        chunks.append(' '.join(word_chunk))
                    word_chunk = [word]
                    word_tokens = word_token_count
                else:
                    word_chunk.append(word)
                    word_tokens += word_token_count
            
            if word_chunk:
                chunks.append(' '.join(word_chunk))
            continue
        
        # Check if adding this sentence would exceed the limit
        if current_tokens + sentence_tokens > max_tokens:
            # Save current chunk and start new one
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_tokens = sentence_tokens
        else:
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks


def ingest_with_chunking(
    db: lancedb.DBConnection,
    table_name: str,
    documents: List[Dict[str, Any]],
    max_tokens: int = MAX_TOKENS,
    embedding_model: str = "all-MiniLM-L6-v2"
) -> lancedb.table.Table:
    """Ingest documents with automatic chunking.
    
    Args:
        db: LanceDB connection
        table_name: Name of the table to create/append to
        documents: List of documents with 'text' and optional metadata
        max_tokens: Maximum tokens per chunk
        embedding_model: Sentence transformer model name
        
    Returns:
        LanceDB table object
    """
    try:
        # Initialize embedding model
        model = SentenceTransformer(embedding_model)
        
        # Process documents and create chunks
        chunked_data = []
        
        for doc_idx, doc in enumerate(documents):
            text = doc.get('text', '')
            metadata = {k: v for k, v in doc.items() if k != 'text'}
            
            # Count tokens
            token_count = count_tokens(text)
            
            if token_count <= max_tokens:
                # Document fits in one chunk
                chunks = [text]
            else:
                # Chunk the document
                chunks = chunk_text(text, max_tokens)
                print(f"Document {doc_idx} split into {len(chunks)} chunks")
            
            # Create entries for each chunk
            for chunk_idx, chunk in enumerate(chunks):
                # Generate embedding
                embedding = model.encode(chunk).tolist()
                
                entry = {
                    'text': chunk,
                    'vector': embedding,
                    'doc_id': doc_idx,
                    'chunk_id': chunk_idx,
                    'total_chunks': len(chunks),
                    'token_count': count_tokens(chunk),
                    **metadata
                }
                chunked_data.append(entry)
        
        # Convert to DataFrame
        df = pd.DataFrame(chunked_data)
        
        # Create or append to table
        try:
            # Try to open existing table
            table = db.open_table(table_name)
            # Append data
            table.add(df)
            print(f"Appended {len(chunked_data)} chunks to existing table '{table_name}'")
        except Exception:
            # Table doesn't exist, create new one
            table = db.create_table(table_name, df)
            print(f"Created table '{table_name}' with {len(chunked_data)} chunks")
        
        return table
        
    except Exception as e:
        print(f"Error during ingestion: {e}")
        raise


def main():
    """Main function to demonstrate token-aware ingestion."""
    try:
        # Create database connection
        db = lancedb.connect("./lancedb_data")
        
        # Create a long document that exceeds token limits
        long_text = """
        Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. 
        Leading AI textbooks define the field as the study of "intelligent agents": any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals.
        Colloquially, the term "artificial intelligence" is often used to describe machines (or computers) that mimic "cognitive" functions that humans associate with the human mind, such as "learning" and "problem solving".
        
        As machines become increasingly capable, tasks considered to require "intelligence" are often removed from the definition of AI, a phenomenon known as the AI effect.
        A quip in Tesler's Theorem says "AI is whatever hasn't been done yet." For instance, optical character recognition is frequently excluded from things considered to be AI, having become a routine technology.
        Modern machine capabilities generally classified as AI include successfully understanding human speech, competing at the highest level in strategic game systems (such as chess and Go), 
        autonomously operating cars, intelligent routing in content delivery networks, and military simulations.
        
        """ * 100  # Repeat to create a very long document
        
        # Create sample documents
        documents = [
            {
                'text': long_text,
                'title': 'Introduction to AI',
                'category': 'technology',
                'author': 'AI Researcher'
            },
            {
                'text': 'Machine learning is a subset of artificial intelligence that focuses on the development of algorithms and statistical models.',
                'title': 'Machine Learning Basics',
                'category': 'technology',
                'author': 'ML Expert'
            },
            {
                'text': 'Deep learning is a subset of machine learning that uses neural networks with multiple layers to progressively extract higher-level features from raw input.',
                'title': 'Deep Learning Overview',
                'category': 'technology',
                'author': 'DL Specialist'
            }
        ]
        
        # Check token counts
        print("Token counts before chunking:")
        for idx, doc in enumerate(documents):
            tokens = count_tokens(doc['text'])
            print(f"  Document {idx}: {tokens} tokens")
        
        # Ingest with automatic chunking
        table = ingest_with_chunking(
            db=db,
            table_name="chunked_documents",
            documents=documents,
            max_tokens=500  # Use smaller limit for demonstration
        )
        
        # Verify ingestion
        result_df = table.to_pandas()
        print(f"\nTotal chunks in table: {len(result_df)}")
        print(f"Columns: {result_df.columns.tolist()}")
        
        # Show chunk distribution
        print("\nChunk distribution by document:")
        for doc_id in result_df['doc_id'].unique():
            doc_chunks = result_df[result_df['doc_id'] == doc_id]
            print(f"  Document {doc_id}: {len(doc_chunks)} chunks")
            print(f"    Token range: {doc_chunks['token_count'].min()}-{doc_chunks['token_count'].max()}")
        
        # Test search on chunked data
        print("\nTesting search on chunked data...")
        query = "What is artificial intelligence?"
        model = SentenceTransformer("all-MiniLM-L6-v2")
        query_vector = model.encode(query).tolist()
        
        search_results = table.search(query_vector).limit(3).to_pandas()
        print(f"Top 3 search results:")
        for idx, row in search_results.iterrows():
            print(f"  {idx + 1}. Doc {row['doc_id']}, Chunk {row['chunk_id']}: {row['text'][:100]}...")
        
        print("\nToken-aware ingestion complete!")
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    main()