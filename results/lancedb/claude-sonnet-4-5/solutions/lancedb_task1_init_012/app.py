# filepath: app.py
"""LanceDB with IVF-PQ index creation."""

import lancedb
from lancedb.pydantic import LanceModel, Vector
import pandas as pd
import numpy as np

# Define document schema with vector embeddings
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
        data: Data to populate the table with

    Returns:
        LanceDB table with IVF-PQ index
    """
    try:
        # Create table with data
        table = db.create_table(
            table_name,
            data=data,
            mode="overwrite"  # Overwrite if exists
        )
        
        # Create IVF-PQ index for efficient similarity search
        # IVF (Inverted File Index) partitions the vector space
        # PQ (Product Quantization) compresses vectors
        table.create_index(
            metric="cosine",  # Cosine similarity metric
            num_partitions=4,  # Number of IVF partitions
            num_sub_vectors=32  # Number of PQ sub-vectors
        )
        
        print(f"Table '{table_name}' created with IVF-PQ index")
        return table
        
    except Exception as e:
        print(f"Error creating indexed table: {e}")
        raise

def main():
    try:
        # Connect to database (creates directory if it doesn't exist)
        db = lancedb.connect("./my_lancedb")
        print("Connected to LanceDB successfully")
        
        # Create sample data for demonstration
        sample_data = []
        for i in range(100):
            sample_data.append({
                "id": i,
                "text": f"Sample document {i}",
                "vector": np.random.randn(128).tolist(),  # Random 128-dim vector
                "category": f"category_{i % 5}"
            })
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(sample_data)
        
        # Create indexed table
        table = create_indexed_table(db, "documents", df)
        
        # Verify table creation
        print(f"Table row count: {table.count_rows()}")
        print(f"Table schema: {table.schema}")
        
        # Test a simple search to verify index is working
        query_vector = np.random.randn(128).tolist()
        results = table.search(query_vector).limit(5).to_pandas()
        print(f"\nSearch test successful - found {len(results)} results")
        
        print("\nIndexed database ready")
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()