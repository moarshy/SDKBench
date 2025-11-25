# filepath: data_ops.py
"""Basic table creation with dict data."""

import pandas as pd
import lancedb

def create_sample_data():
    """Create sample data."""
    return [
        {"text": "Hello world", "category": "greeting"},
        {"text": "Python programming", "category": "tech"},
    ]

def create_table(db, table_name: str, data):
    """Create table with data.

    Args:
        db: LanceDB connection object
        table_name: Name of the table to create
        data: List of dictionaries containing the data

    Returns:
        LanceDB table object

    Raises:
        ValueError: If data is empty or invalid
        Exception: If table creation fails
    """
    if not data:
        raise ValueError("Data cannot be empty")
    
    if not isinstance(data, list):
        raise ValueError("Data must be a list of dictionaries")
    
    try:
        # Create table with data directly (list of dicts)
        # mode="overwrite" ensures we replace if table exists
        table = db.create_table(table_name, data=data, mode="overwrite")
        return table
    except Exception as e:
        raise Exception(f"Failed to create table '{table_name}': {str(e)}")

def main():
    """Main function to demonstrate table creation."""
    try:
        # Connect to database (creates directory if it doesn't exist)
        db = lancedb.connect("./my_lancedb")
        print("Connected to database")
        
        # Create sample data
        data = create_sample_data()
        print(f"Created sample data with {len(data)} records")
        
        # Create table
        table_name = "sample_table"
        table = create_table(db, table_name, data)
        print(f"Table '{table_name}' created successfully")
        
        # Verify table creation by reading data back
        df = table.to_pandas()
        print(f"\nTable contents:\n{df}")
        print(f"\nTable schema:\n{table.schema}")
        
    except ValueError as ve:
        print(f"Validation error: {ve}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()