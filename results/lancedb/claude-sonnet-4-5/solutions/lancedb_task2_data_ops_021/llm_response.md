```txt
# filepath: requirements.txt
pandas>=2.0.0
numpy>=1.24.0
tiktoken>=0.5.0
lancedb>=0.5.0
sentence-transformers>=2.2.0
pyarrow>=12.0.0
```

```python
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
        text: Text to count tokens for
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
        # Fallback: rough estimate (1 token ≈ 4 chars)
        return len(text) // 4


def chunk_text(text: str, max_tokens: int = MAX_TOKENS, model: str = "cl100k_base") -> List[str]:
    """Chunk text to fit token limit.
    
    Splits text at sentence boundaries to ensure each chunk is under max_tokens.
    
    Args:
        text: Text to chunk
        max_tokens: Maximum tokens per chunk
        model: Tiktoken encoding model name
        
    Returns:
        List of text chunks, each under max_tokens
    """
    if not text or not text.strip():
        return []
    
    # Check if text is already under limit
    if count_tokens(text, model) <= max_tokens:
        return [text]
    
    # Split into sentences using regex (handles ., !, ?)
    sentence_pattern = r'(?<=[.!?])\s+'
    sentences = re.split(sentence_pattern, text)
    
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    encoding = tiktoken.get_encoding(model)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        sentence_tokens = len(encoding.encode(sentence))
        
        # If single sentence exceeds max_tokens, split by words
        if sentence_tokens > max_tokens:
            words = sentence.split()
            word_chunk = []
            word_tokens = 0
            
            for word in words:
                word_token_count = len(encoding.encode(word + " "))
                
                if word_tokens + word_token_count > max_tokens:
                    if word_chunk:
                        chunks.append(" ".join(word_chunk))
                    word_chunk = [word]
                    word_tokens = word_token_count
                else:
                    word_chunk.append(word)
                    word_tokens += word_token_count
            
            if word_chunk:
                chunks.append(" ".join(word_chunk))
            continue
        
        # Check if adding this sentence would exceed limit
        if current_tokens + sentence_tokens > max_tokens:
            # Save current chunk and start new one
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_tokens = sentence_tokens
        else:
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks


def ingest_with_chunking(
    db: lancedb.DBConnection,
    table_name: str,
    documents: List[Dict[str, Any]],
    text_field: str = "text",
    max_tokens: int = MAX_TOKENS,
    embedding_model: str = "all-MiniLM-L6-v2"
) -> lancedb.table.Table:
    """Ingest documents with automatic chunking.
    
    Args:
        db: LanceDB connection
        table_name: Name of table to create/append to
        documents: List of document dictionaries with text and metadata
        text_field: Field name containing text to chunk
        max_tokens: Maximum tokens per chunk
        embedding_model: SentenceTransformer model name
        
    Returns:
        LanceDB table with ingested chunks
    """
    try:
        # Initialize embedding model
        model = SentenceTransformer(embedding_model)
        
        # Process documents into chunks
        chunked_data = []
        
        for doc_idx, doc in enumerate(documents):
            if text_field not in doc:
                print(f"Warning: Document {doc_idx} missing '{text_field}' field, skipping")
                continue
            
            text = doc[text_field]
            chunks = chunk_text(text, max_tokens)
            
            print(f"Document {doc_idx}: {len(text)} chars -> {len(chunks)} chunks")
            
            # Create chunk records with embeddings
            for chunk_idx, chunk in enumerate(chunks):
                # Generate embedding
                embedding = model.encode(chunk).tolist()
                
                # Create chunk record with metadata
                chunk_record = {
                    "text": chunk,
                    "vector": embedding,
                    "doc_id": doc.get("id", doc_idx),
                    "chunk_id": chunk_idx,
                    "total_chunks": len(chunks),
                    "token_count": count_tokens(chunk)
                }
                
                # Add any additional metadata from original document
                for key, value in doc.items():
                    if key != text_field and key not in chunk_record:
                        chunk_record[key] = value
                
                chunked_data.append(chunk_record)
        
        if not chunked_data:
            raise ValueError("No valid documents to ingest")
        
        # Convert to DataFrame for LanceDB
        df = pd.DataFrame(chunked_data)
        
        # Create or append to table
        try:
            # Try to open existing table
            table = db.open_table(table_name)
            print(f"Appending {len(chunked_data)} chunks to existing table '{table_name}'")
            table.add(df)
        except Exception:
            # Create new table if it doesn't exist
            print(f"Creating new table '{table_name}' with {len(chunked_data)} chunks")
            table = db.create_table(table_name, df)
        
        print(f"Successfully ingested {len(chunked_data)} chunks from {len(documents)} documents")
        return table
        
    except Exception as e:
        print(f"Error during ingestion: {e}")
        raise


def main():
    """Demonstrate token-aware document ingestion."""
    
    # Create a long document that exceeds token limits
    long_text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural 
    intelligence displayed by humans and animals. Leading AI textbooks define the field as the study 
    of "intelligent agents": any device that perceives its environment and takes actions that maximize 
    its chance of successfully achieving its goals. Colloquially, the term "artificial intelligence" 
    is often used to describe machines (or computers) that mimic "cognitive" functions that humans 
    associate with the human mind, such as "learning" and "problem solving".
    
    As machines become increasingly capable, tasks considered to require "intelligence" are often 
    removed from the definition of AI, a phenomenon known as the AI effect. A quip in Tesler's Theorem 
    says "AI is whatever hasn't been done yet." For instance, optical character recognition is 
    frequently excluded from things considered to be AI, having become a routine technology.
    
    Modern machine learning techniques are at the core of AI. Machine learning is a subset of AI that 
    provides systems the ability to automatically learn and improve from experience without being 
    explicitly programmed. Deep learning is a subset of machine learning that uses neural networks 
    with multiple layers. These neural networks attempt to simulate the behavior of the human brain—
    albeit far from matching its ability—allowing it to "learn" from large amounts of data.
    
    Natural language processing (NLP) is a subfield of linguistics, computer science, and artificial 
    intelligence concerned with the interactions between computers and human language, in particular 
    how to program computers to process and analyze large amounts of natural language data. The goal 
    is a computer capable of "understanding" the contents of documents, including the contextual 
    nuances of the language within them.
    """ * 50  # Repeat to create a very long document
    
    # Create sample documents
    documents = [
        {
            "id": "doc1",
            "text": long_text,
            "title": "Introduction to AI",
            "author": "AI Research Team",
            "category": "technology"
        },
        {
            "id": "doc2",
            "text": "Vector databases are specialized databases designed to store and query high-dimensional vectors efficiently. They are essential for modern AI applications that use embeddings.",
            "title": "Vector Databases",
            "author": "Database Expert",
            "category": "databases"
        }
    ]
    
    # Connect to LanceDB
    db = lancedb.connect("./token_aware_db")
    
    # Ingest with automatic chunking
    print(f"Ingesting {len(documents)} documents with token-aware chunking...")
    print(f"Max tokens per chunk: {MAX_TOKENS}")
    print("-" * 60)
    
    table = ingest_with_chunking(
        db=db,
        table_name="chunked_documents",
        documents=documents,
        text_field="text",
        max_tokens=MAX_TOKENS
    )
    
    print("-" * 60)
    print(f"Table '{table.name}' created with {table.count_rows()} chunks")
    
    # Demonstrate search on chunked data
    print("\nSearching for 'machine learning'...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_vector = model.encode("machine learning").tolist()
    
    results = table.search(query_vector).limit(3).to_pandas()
    
    print(f"\nTop 3 results:")
    for idx, row in results.iterrows():
        print(f"\n{idx + 1}. Doc ID: {row['doc_id']}, Chunk: {row['chunk_id']}/{row['total_chunks']}")
        print(f"   Tokens: {row['token_count']}")
        print(f"   Text preview: {row['text'][:100]}...")
    
    print("\nToken-aware ingestion complete!")


if __name__ == "__main__":
    main()
```

This solution provides a complete implementation for handling token limits with chunking in LanceDB:

**Key Features:**

1. **Token Counting**: Uses `tiktoken` to accurately count tokens with the cl100k_base encoding (used by GPT-3.5/4)

2. **Smart Chunking**: 
   - Splits text at sentence boundaries to maintain semantic coherence
   - Falls back to word-level splitting for very long sentences
   - Ensures each chunk stays under the token limit

3. **Automatic Ingestion**:
   - Processes documents and creates chunks automatically
   - Generates embeddings using SentenceTransformer
   - Stores chunks with metadata (doc_id, chunk_id, token_count)
   - Preserves original document metadata

4. **Error Handling**:
   - Handles missing text fields
   - Gracefully handles empty documents
   - Provides fallback token counting
   - Proper exception handling throughout

5. **LanceDB Integration**:
   - Creates tables with proper schema
   - Handles both new table creation and appending to existing tables
   - Stores vectors with metadata for efficient retrieval

The example demonstrates ingesting a very long document (repeated 50x) and a shorter one, then performing a vector search on the chunked results.