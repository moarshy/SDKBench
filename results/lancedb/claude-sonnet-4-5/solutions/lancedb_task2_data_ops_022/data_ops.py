# filepath: data_ops.py
"""Batch ingestion with progress tracking."""

import lancedb
import numpy as np
import pandas as pd
from tqdm import tqdm
from typing import List, Dict, Any

BATCH_SIZE = 100

def batch_ingest(db, table_name: str, documents: list, batch_size: int = BATCH_SIZE):
    """Ingest documents in batches with progress.

    Args:
        db: LanceDB connection
        table_name: Name of the table to create/update
        documents: List of document dictionaries with 'id', 'text', and 'vector' keys
        batch_size: Number of documents per batch

    Returns:
        The created/updated table
    """
    if not documents:
        raise ValueError("Documents list cannot be empty")
    
    # Split documents into batches
    batches = [documents[i:i + batch_size] for i in range(0, len(documents), batch_size)]
    
    table = None
    
    try:
        # Create table with first batch
        first_batch = batches[0]
        print(f"Creating table '{table_name}' with {len(first_batch)} documents...")
        
        # Convert first batch to pandas DataFrame
        df_first = pd.DataFrame(first_batch)
        
        # Create the table
        table = db.create_table(table_name, data=df_first, mode="overwrite")
        print(f"Table created successfully with {len(first_batch)} documents")
        
        # Add remaining batches with progress bar
        if len(batches) > 1:
            print(f"\nAdding remaining {len(batches) - 1} batches...")
            
            for batch in tqdm(batches[1:], desc="Ingesting batches", unit="batch"):
                df_batch = pd.DataFrame(batch)
                table.add(df_batch)
            
            print(f"\nSuccessfully ingested {len(documents)} documents in {len(batches)} batches")
        
        return table
        
    except Exception as e:
        print(f"Error during batch ingestion: {e}")
        raise

def generate_sample_documents(num_docs: int, vector_dim: int = 128) -> List[Dict[str, Any]]:
    """Generate sample documents with random vectors.
    
    Args:
        num_docs: Number of documents to generate
        vector_dim: Dimension of the vector embeddings
        
    Returns:
        List of document dictionaries
    """
    documents = []
    
    for i in range(num_docs):
        doc = {
            "id": i,
            "text": f"This is sample document number {i} with some content.",
            "category": f"category_{i % 5}",  # 5 different categories
            "vector": np.random.randn(vector_dim).astype(np.float32).tolist()
        }
        documents.append(doc)
    
    return documents

def verify_ingestion(table, expected_count: int):
    """Verify that the ingestion was successful.
    
    Args:
        table: LanceDB table
        expected_count: Expected number of documents
    """
    try:
        # Count rows in the table
        df = table.to_pandas()
        actual_count = len(df)
        
        print(f"\nVerification:")
        print(f"  Expected documents: {expected_count}")
        print(f"  Actual documents: {actual_count}")
        print(f"  Status: {'✓ PASS' if actual_count == expected_count else '✗ FAIL'}")
        
        if actual_count > 0:
            print(f"\nSample document:")
            print(df.head(1).to_dict('records')[0])
        
        return actual_count == expected_count
        
    except Exception as e:
        print(f"Error during verification: {e}")
        return False

def main():
    """Main function to demonstrate batch ingestion."""
    
    # Configuration
    DB_PATH = "./lancedb_batch_demo"
    TABLE_NAME = "documents"
    NUM_DOCUMENTS = 1000
    VECTOR_DIM = 128
    BATCH_SIZE_CONFIG = 100
    
    print("=" * 60)
    print("LanceDB Batch Ingestion Demo")
    print("=" * 60)
    
    try:
        # Create database connection
        print(f"\nConnecting to database at: {DB_PATH}")
        db = lancedb.connect(DB_PATH)
        print("✓ Database connection established")
        
        # Generate large dataset
        print(f"\nGenerating {NUM_DOCUMENTS} sample documents...")
        documents = generate_sample_documents(NUM_DOCUMENTS, VECTOR_DIM)
        print(f"✓ Generated {len(documents)} documents with {VECTOR_DIM}-dimensional vectors")
        
        # Batch ingest with progress tracking
        print(f"\nStarting batch ingestion (batch size: {BATCH_SIZE_CONFIG})...")
        table = batch_ingest(db, TABLE_NAME, documents, batch_size=BATCH_SIZE_CONFIG)
        
        # Verify ingestion
        verify_ingestion(table, NUM_DOCUMENTS)
        
        # Demonstrate a simple search
        print("\n" + "=" * 60)
        print("Testing vector search on ingested data...")
        print("=" * 60)
        
        # Create a random query vector
        query_vector = np.random.randn(VECTOR_DIM).astype(np.float32)
        
        # Perform search
        results = table.search(query_vector).limit(5).to_pandas()
        
        print(f"\nTop 5 search results:")
        for idx, row in results.iterrows():
            print(f"  {idx + 1}. ID: {row['id']}, Category: {row['category']}")
            print(f"     Text: {row['text'][:50]}...")
        
        print("\n" + "=" * 60)
        print("Batch ingestion complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise

if __name__ == "__main__":
    main()