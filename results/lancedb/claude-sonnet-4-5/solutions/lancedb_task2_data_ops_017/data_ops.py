# filepath: data_ops.py
"""Create table with LanceModel schema."""

import lancedb
from lancedb.pydantic import LanceModel, Vector
import numpy as np
import pandas as pd
from typing import List


# Define Document schema with LanceModel
class Document(LanceModel):
    """Document schema with text, vector, and category fields."""
    text: str
    vector: Vector(384)  # 384-dimensional vector
    category: str


def create_table_with_schema(db, table_name: str, data: List[dict]):
    """Create table with LanceModel schema.
    
    Args:
        db: LanceDB connection
        table_name: Name of the table to create
        data: List of dictionaries containing document data
        
    Returns:
        LanceDB table with the defined schema
        
    Raises:
        ValueError: If data format is invalid
        Exception: If table creation fails
    """
    try:
        # Validate data format
        if not data:
            raise ValueError("Data cannot be empty")
        
        # Validate that all required fields are present
        required_fields = {'text', 'vector', 'category'}
        for item in data:
            if not all(field in item for field in required_fields):
                raise ValueError(f"Data must contain fields: {required_fields}")
            
            # Validate vector dimension
            if len(item['vector']) != 384:
                raise ValueError(f"Vector must be 384-dimensional, got {len(item['vector'])}")
        
        # Convert data to Document instances
        documents = [Document(**item) for item in data]
        
        # Create table with schema
        # If table exists, it will be overwritten (mode="overwrite")
        table = db.create_table(
            table_name,
            data=documents,
            mode="overwrite"
        )
        
        print(f"✓ Table '{table_name}' created successfully with {len(data)} documents")
        print(f"✓ Schema: text (str), vector (384-dim), category (str)")
        
        return table
        
    except ValueError as ve:
        print(f"✗ Validation error: {ve}")
        raise
    except Exception as e:
        print(f"✗ Error creating table: {e}")
        raise


def main():
    """Main function to demonstrate table creation with schema."""
    try:
        # Connect to LanceDB (creates database if it doesn't exist)
        db = lancedb.connect("./lancedb_data")
        print("✓ Connected to LanceDB")
        
        # Create sample data with 384-dimensional vectors
        sample_data = [
            {
                "text": "Machine learning is a subset of artificial intelligence",
                "vector": np.random.randn(384).tolist(),  # Random 384-dim vector
                "category": "AI"
            },
            {
                "text": "Python is a popular programming language for data science",
                "vector": np.random.randn(384).tolist(),
                "category": "Programming"
            },
            {
                "text": "Vector databases enable semantic search capabilities",
                "vector": np.random.randn(384).tolist(),
                "category": "Database"
            },
            {
                "text": "Deep learning models require large amounts of training data",
                "vector": np.random.randn(384).tolist(),
                "category": "AI"
            },
            {
                "text": "LanceDB is a serverless vector database for AI applications",
                "vector": np.random.randn(384).tolist(),
                "category": "Database"
            }
        ]
        
        # Create table with schema
        table_name = "documents"
        table = create_table_with_schema(db, table_name, sample_data)
        
        # Verify table creation by counting rows
        count = table.count_rows()
        print(f"✓ Table contains {count} rows")
        
        # Display sample of the data
        print("\n--- Sample Data ---")
        df = table.to_pandas()
        print(df[['text', 'category']].head())
        
        # Show schema information
        print("\n--- Schema Information ---")
        print(f"Table name: {table_name}")
        print(f"Schema: {table.schema}")
        
        print("\n✓ Schema-based table created successfully!")
        
    except Exception as e:
        print(f"\n✗ Error in main: {e}")
        raise


if __name__ == "__main__":
    main()