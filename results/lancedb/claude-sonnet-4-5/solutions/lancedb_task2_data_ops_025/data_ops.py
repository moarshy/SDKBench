# filepath: data_ops.py
"""Idempotent table creation pattern."""

import lancedb
import pyarrow as pa
import pandas as pd
from typing import Optional, List, Dict, Any


def get_or_create_table(db: lancedb.DBConnection, table_name: str, schema: Optional[pa.Schema] = None):
    """Get existing table or create new one.
    
    Args:
        db: LanceDB connection
        table_name: Name of the table
        schema: PyArrow schema for table creation (required if table doesn't exist)
    
    Returns:
        LanceDB table instance
        
    Raises:
        ValueError: If table doesn't exist and no schema provided
    """
    try:
        # Check if table exists in db.table_names()
        if table_name in db.table_names():
            print(f"Table '{table_name}' exists, opening...")
            return db.open_table(table_name)
        
        # If not, create with schema
        if schema is None:
            raise ValueError(f"Table '{table_name}' does not exist and no schema provided")
        
        print(f"Table '{table_name}' does not exist, creating...")
        # Create empty table with schema
        empty_data = pa.Table.from_pylist([], schema=schema)
        return db.create_table(table_name, empty_data)
        
    except Exception as e:
        print(f"Error in get_or_create_table: {e}")
        raise


def ensure_table(db: lancedb.DBConnection, table_name: str, initial_data: List[Dict[str, Any]]):
    """Ensure table exists with mode='overwrite' for idempotency.
    
    This function is idempotent - safe to run multiple times.
    It will always overwrite the table with the provided data.
    
    Args:
        db: LanceDB connection
        table_name: Name of the table
        initial_data: List of dictionaries containing the initial data
        
    Returns:
        LanceDB table instance
    """
    try:
        # Use create_table with mode="overwrite"
        # This is idempotent - safe to run multiple times
        print(f"Ensuring table '{table_name}' with overwrite mode...")
        table = db.create_table(table_name, initial_data, mode="overwrite")
        print(f"Table '{table_name}' created/overwritten successfully")
        return table
        
    except Exception as e:
        print(f"Error in ensure_table: {e}")
        raise


def main():
    """Demonstrate idempotent table creation patterns."""
    
    # Connect to LanceDB (creates directory if it doesn't exist)
    db = lancedb.connect("./lancedb_data")
    print("Connected to LanceDB\n")
    
    # Example 1: get_or_create_table pattern
    print("=== Example 1: get_or_create_table ===")
    
    # Define schema for a simple vector table
    schema = pa.schema([
        pa.field("id", pa.int64()),
        pa.field("vector", pa.list_(pa.float32(), 3)),  # 3-dimensional vectors
        pa.field("text", pa.string()),
    ])
    
    # First call - creates table
    table1 = get_or_create_table(db, "my_vectors", schema)
    
    # Add some data
    data = [
        {"id": 1, "vector": [1.0, 2.0, 3.0], "text": "first"},
        {"id": 2, "vector": [4.0, 5.0, 6.0], "text": "second"},
    ]
    table1.add(data)
    print(f"Added {len(data)} records\n")
    
    # Second call - opens existing table (idempotent)
    table1_again = get_or_create_table(db, "my_vectors", schema)
    print(f"Table has {table1_again.count_rows()} rows\n")
    
    # Example 2: ensure_table pattern (always overwrites)
    print("=== Example 2: ensure_table (overwrite mode) ===")
    
    initial_data = [
        {"id": 10, "vector": [0.1, 0.2, 0.3], "text": "initial_1"},
        {"id": 20, "vector": [0.4, 0.5, 0.6], "text": "initial_2"},
        {"id": 30, "vector": [0.7, 0.8, 0.9], "text": "initial_3"},
    ]
    
    # First call - creates table
    table2 = ensure_table(db, "idempotent_table", initial_data)
    print(f"Table has {table2.count_rows()} rows")
    
    # Second call - overwrites table (idempotent, always same result)
    table2_again = ensure_table(db, "idempotent_table", initial_data)
    print(f"Table still has {table2_again.count_rows()} rows")
    
    # Third call with different data - still overwrites
    new_data = [
        {"id": 100, "vector": [1.1, 1.2, 1.3], "text": "new_1"},
    ]
    table2_new = ensure_table(db, "idempotent_table", new_data)
    print(f"Table now has {table2_new.count_rows()} rows (overwritten)\n")
    
    # Example 3: Demonstrate with more complex schema
    print("=== Example 3: Complex schema with metadata ===")
    
    complex_schema = pa.schema([
        pa.field("id", pa.int64()),
        pa.field("embedding", pa.list_(pa.float32(), 128)),  # 128-dim embeddings
        pa.field("text", pa.string()),
        pa.field("metadata", pa.string()),  # JSON string for metadata
        pa.field("timestamp", pa.timestamp('ms')),
    ])
    
    table3 = get_or_create_table(db, "complex_vectors", complex_schema)
    
    # Add sample data with proper dimensions
    import numpy as np
    from datetime import datetime
    
    complex_data = [
        {
            "id": 1,
            "embedding": np.random.rand(128).tolist(),
            "text": "Sample document 1",
            "metadata": '{"source": "api", "version": 1}',
            "timestamp": datetime.now(),
        },
        {
            "id": 2,
            "embedding": np.random.rand(128).tolist(),
            "text": "Sample document 2",
            "metadata": '{"source": "upload", "version": 1}',
            "timestamp": datetime.now(),
        },
    ]
    
    table3.add(complex_data)
    print(f"Added {len(complex_data)} records with 128-dim embeddings")
    
    # Verify idempotency - opening again should work
    table3_verify = get_or_create_table(db, "complex_vectors", complex_schema)
    print(f"Verified: Table has {table3_verify.count_rows()} rows\n")
    
    # Display all tables
    print("=== All tables in database ===")
    for table_name in db.table_names():
        tbl = db.open_table(table_name)
        print(f"- {table_name}: {tbl.count_rows()} rows")
    
    print("\nIdempotent creation complete")


if __name__ == "__main__":
    main()