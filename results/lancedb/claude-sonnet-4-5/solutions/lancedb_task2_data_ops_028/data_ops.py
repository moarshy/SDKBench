# filepath: data_ops.py
"""Async batch embedding with rate limiting."""

import asyncio
import time
from typing import List, Dict
import numpy as np

import lancedb
from sentence_transformers import SentenceTransformer

RATE_LIMIT = 10  # requests per second
BATCH_SIZE = 50

# Initialize embedding model (this is done once globally)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


async def embed_batch_async(texts: List[str], semaphore: asyncio.Semaphore) -> np.ndarray:
    """Embed batch of texts with rate limiting.
    
    Args:
        texts: List of text strings to embed
        semaphore: Asyncio semaphore for rate limiting
        
    Returns:
        numpy array of embeddings
    """
    async with semaphore:
        # Simulate async API call by running in executor
        # In production, this would be an actual async API call
        loop = asyncio.get_event_loop()
        
        try:
            # Run the embedding in a thread pool to avoid blocking
            embeddings = await loop.run_in_executor(
                None, 
                embedding_model.encode, 
                texts
            )
            
            # Add small delay to respect rate limit
            await asyncio.sleep(1.0 / RATE_LIMIT)
            
            return embeddings
            
        except Exception as e:
            print(f"Error embedding batch: {e}")
            # Return zero vectors as fallback
            return np.zeros((len(texts), 384))


async def ingest_async(db: lancedb.DBConnection, table_name: str, documents: List[Dict[str, str]]):
    """Async batch ingestion with rate limiting.
    
    Args:
        db: LanceDB connection
        table_name: Name of the table to ingest into
        documents: List of document dictionaries with 'id', 'text', and 'metadata' keys
    """
    # Create semaphore for rate limiting
    semaphore = asyncio.Semaphore(RATE_LIMIT)
    
    # Split documents into batches
    batches = [documents[i:i + BATCH_SIZE] for i in range(0, len(documents), BATCH_SIZE)]
    
    print(f"Processing {len(documents)} documents in {len(batches)} batches...")
    
    # Process batches concurrently
    tasks = []
    for batch_idx, batch in enumerate(batches):
        texts = [doc['text'] for doc in batch]
        task = embed_batch_async(texts, semaphore)
        tasks.append((batch_idx, batch, task))
    
    # Gather all embeddings
    all_results = []
    completed = 0
    
    for batch_idx, batch, task in tasks:
        try:
            embeddings = await task
            
            # Prepare data for insertion
            for i, doc in enumerate(batch):
                result = {
                    'id': doc['id'],
                    'text': doc['text'],
                    'vector': embeddings[i].tolist(),
                    'metadata': doc.get('metadata', {})
                }
                all_results.append(result)
            
            completed += 1
            if completed % 5 == 0:
                print(f"Completed {completed}/{len(batches)} batches")
                
        except Exception as e:
            print(f"Error processing batch {batch_idx}: {e}")
            continue
    
    # Insert all results into table
    try:
        if all_results:
            # Check if table exists
            try:
                table = db.open_table(table_name)
                # Add data to existing table
                table.add(all_results)
                print(f"Added {len(all_results)} documents to existing table '{table_name}'")
            except Exception:
                # Create new table if it doesn't exist
                table = db.create_table(table_name, data=all_results)
                print(f"Created table '{table_name}' with {len(all_results)} documents")
            
            print(f"Successfully ingested {len(all_results)} documents")
        else:
            print("No results to ingest")
            
    except Exception as e:
        print(f"Error inserting data into table: {e}")
        raise


async def main():
    """Main function to demonstrate async batch ingestion."""
    
    # Connect to LanceDB
    db = lancedb.connect("./lancedb_async_demo")
    table_name = "async_documents"
    
    # Create large document set (500 documents for demonstration)
    print("Generating document set...")
    documents = []
    for i in range(500):
        doc = {
            'id': f'doc_{i:04d}',
            'text': f'This is document number {i}. It contains sample text for embedding and search purposes. '
                   f'The content varies to create diverse embeddings for testing.',
            'metadata': {
                'category': f'category_{i % 10}',
                'priority': i % 5,
                'timestamp': time.time()
            }
        }
        documents.append(doc)
    
    print(f"Created {len(documents)} documents")
    
    # Ingest with async batching
    start_time = time.time()
    await ingest_async(db, table_name, documents)
    elapsed_time = time.time() - start_time
    
    print(f"\nAsync batch complete in {elapsed_time:.2f} seconds")
    print(f"Average rate: {len(documents) / elapsed_time:.2f} documents/second")
    
    # Verify the data
    try:
        table = db.open_table(table_name)
        count = table.count_rows()
        print(f"\nTable '{table_name}' now contains {count} rows")
        
        # Perform a sample search
        print("\nPerforming sample search...")
        query_text = "sample text for testing"
        query_vector = embedding_model.encode(query_text).tolist()
        
        results = table.search(query_vector).limit(5).to_pandas()
        print(f"\nTop 5 search results:")
        print(results[['id', 'text']].to_string())
        
    except Exception as e:
        print(f"Error verifying data: {e}")


if __name__ == "__main__":
    asyncio.run(main())