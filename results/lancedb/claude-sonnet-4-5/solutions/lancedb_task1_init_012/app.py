# filepath: app.py
"""LanceDB with IVF-PQ index creation."""

import lancedb
from lancedb.pydantic import LanceModel, Vector
import pandas as pd
import numpy as np
from pathlib import Path

# Define document schema with 128-dimensional vectors
class Document(LanceModel):
    id: int
    text: str
    vector: Vector(128)  # 128-dimensional vector
    category: str

def create_indexed_table(db, table_name: str, data):
    """Create table and build IVF-PQ index.

    Args:
        db: LanceDB connection
        table_name: Name of the table to create
        data: Data to insert (list of dicts or pandas DataFrame)

    Returns:
        LanceDB table with IVF-PQ index
    """
    try:
        # Drop table if it exists to start fresh
        if table_name in db.table_names():
            db.drop_table(table_name)
        
        # Create table with data
        table = db.create_table(
            table_name,
            data=data,
            schema=Document
        )
        
        print(f"Table '{table_name}' created with {len(data)} records")
        
        # Create IVF-PQ index for efficient vector search
        # IVF (Inverted File Index) partitions the vector space
        # PQ (Product Quantization) compresses vectors
        table.create_index(
            metric="cosine",  # Use cosine similarity
            num_partitions=4,  # Number of IVF partitions
            num_sub_vectors=32  # Number of PQ sub-vectors (must divide vector dimension)
        )
        
        print(f"IVF-PQ index created on table '{table_name}'")
        
        return table
    
    except Exception as e:
        print(f"Error creating indexed table: {e}")
        raise

def main():
    """Main function to initialize LanceDB with indexed table."""
    try:
        # Connect to database (creates directory if it doesn't exist)
        db_path = "./my_lancedb"
        print(f"Connecting to LanceDB at: {db_path}")
        
        db = lancedb.connect(db_path)
        print(f"Successfully connected to LanceDB")
        
        # Create sample data with 128-dimensional vectors
        sample_data = []
        for i in range(100):
            sample_data.append({
                "id": i,
                "text": f"Document {i} about topic {i % 5}",
                "vector": np.random.randn(128).astype(np.float32).tolist(),
                "category": f"category_{i % 5}"
            })
        
        print(f"Generated {len(sample_data)} sample documents")
        
        # Create indexed table
        table = create_indexed_table(db, "documents", sample_data)
        
        # Verify the table was created successfully
        print(f"\nDatabase tables: {db.table_names()}")
        print(f"Table row count: {table.count_rows()}")
        
        # Test a simple vector search to verify index is working
        query_vector = np.random.randn(128).astype(np.float32)
        results = table.search(query_vector).limit(5).to_pandas()
        print(f"\nTest search returned {len(results)} results")
        
        print("\n✓ Indexed database ready")
        
        return db, table
    
    except Exception as e:
        print(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()