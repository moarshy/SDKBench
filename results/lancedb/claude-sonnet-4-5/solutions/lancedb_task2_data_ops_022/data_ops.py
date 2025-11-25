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
        table_name: Name of the table to create/append to
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
                try:
                    df_batch = pd.DataFrame(batch)
                    table.add(df_batch)
                except Exception as e:
                    print(f"\nWarning: Failed to add batch: {e}")
                    # Continue with next batch instead of failing completely
                    continue
        
        # Get final count
        total_count = len(table)
        print(f"\nBatch ingestion complete! Total documents in table: {total_count}")
        
        return table
        
    except Exception as e:
        print(f"Error during batch ingestion: {e}")
        raise

def create_sample_documents(num_docs: int = 1000, vector_dim: int = 128) -> List[Dict[str, Any]]:
    """Create sample documents with random vectors.
    
    Args:
        num_docs: Number of documents to create
        vector_dim: Dimension of the vector embeddings
        
    Returns:
        List of document dictionaries
    """
    print(f"Generating {num_docs} sample documents with {vector_dim}-dimensional vectors...")
    
    documents = []
    for i in range(num_docs):
        doc = {
            "id": i,
            "text": f"This is sample document number {i} with some content.",
            "category": f"category_{i % 10}",  # 10 different categories
            "vector": np.random.randn(vector_dim).astype(np.float32).tolist()
        }
        documents.append(doc)
    
    print(f"Generated {len(documents)} documents")
    return documents

def verify_ingestion(table, expected_count: int):
    """Verify that ingestion was successful.
    
    Args:
        table: LanceDB table
        expected_count: Expected number of documents
    """
    actual_count = len(table)
    print(f"\nVerification:")
    print(f"  Expected documents: {expected_count}")
    print(f"  Actual documents: {actual_count}")
    
    if actual_count == expected_count:
        print("  ✓ Ingestion verified successfully!")
    else:
        print(f"  ✗ Warning: Count mismatch! Missing {expected_count - actual_count} documents")
    
    # Show sample of data
    print("\nSample data (first 3 rows):")
    sample_df = table.to_pandas().head(3)
    # Don't print full vectors, just show they exist
    for col in sample_df.columns:
        if col == 'vector':
            sample_df[col] = sample_df[col].apply(lambda x: f"[{len(x)} dims]")
    print(sample_df)

def main():
    """Main function to demonstrate batch ingestion."""
    
    # Configuration
    DB_PATH = "./lancedb_batch_demo"
    TABLE_NAME = "documents"
    NUM_DOCUMENTS = 1000
    VECTOR_DIM = 128
    BATCH_SIZE_CONFIG = 100
    
    try:
        # Create LanceDB connection
        print(f"Connecting to LanceDB at '{DB_PATH}'...")
        db = lancedb.connect(DB_PATH)
        print("Connected successfully!\n")
        
        # Create large dataset
        documents = create_sample_documents(
            num_docs=NUM_DOCUMENTS,
            vector_dim=VECTOR_DIM
        )
        
        # Batch ingest with progress tracking
        print(f"\nStarting batch ingestion (batch size: {BATCH_SIZE_CONFIG})...")
        table = batch_ingest(
            db=db,
            table_name=TABLE_NAME,
            documents=documents,
            batch_size=BATCH_SIZE_CONFIG
        )
        
        # Verify ingestion
        verify_ingestion(table, NUM_DOCUMENTS)
        
        print("\n" + "="*50)
        print("Batch ingestion complete!")
        print("="*50)
        
    except Exception as e:
        print(f"\nError in main: {e}")
        raise

if __name__ == "__main__":
    main()