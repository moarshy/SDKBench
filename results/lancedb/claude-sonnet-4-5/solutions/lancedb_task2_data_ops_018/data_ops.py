# filepath: data_ops.py
"""Handle null/optional fields in LanceDB."""

from typing import Optional
import lancedb
from lancedb.pydantic import LanceModel, Vector
import numpy as np
import pandas as pd


# Define schema with optional fields
class Document(LanceModel):
    """Document schema with optional fields."""
    text: str
    vector: Vector(384)
    category: Optional[str] = None
    tags: Optional[str] = None


def insert_with_nulls(table, data):
    """Insert data with optional null fields.
    
    Args:
        table: LanceDB table instance
        data: List of dictionaries or pandas DataFrame with document data
        
    Returns:
        None
        
    Raises:
        ValueError: If required fields are missing
        Exception: For other insertion errors
    """
    try:
        # Convert data to list of dicts if it's a DataFrame
        if isinstance(data, pd.DataFrame):
            data = data.to_dict('records')
        
        # Validate that required fields are present
        for idx, record in enumerate(data):
            if 'text' not in record or record['text'] is None:
                raise ValueError(f"Record {idx}: 'text' is a required field and cannot be null")
            if 'vector' not in record or record['vector'] is None:
                raise ValueError(f"Record {idx}: 'vector' is a required field and cannot be null")
            
            # Ensure vector has correct dimensions
            if len(record['vector']) != 384:
                raise ValueError(f"Record {idx}: vector must have 384 dimensions, got {len(record['vector'])}")
            
            # Handle missing optional fields by setting them to None explicitly
            if 'category' not in record:
                record['category'] = None
            if 'tags' not in record:
                record['tags'] = None
        
        # Insert data into table
        table.add(data)
        print(f"Successfully inserted {len(data)} records with null/optional fields")
        
    except ValueError as ve:
        print(f"Validation error: {ve}")
        raise
    except Exception as e:
        print(f"Error inserting data with nulls: {e}")
        raise


def query_with_null_filters(table, category_filter: Optional[str] = None):
    """Query data with filters on optional fields.
    
    Args:
        table: LanceDB table instance
        category_filter: Optional category to filter by
        
    Returns:
        pandas DataFrame with query results
    """
    try:
        # Create a sample query vector
        query_vector = np.random.randn(384).astype(np.float32)
        
        # Build query
        query = table.search(query_vector).limit(10)
        
        # Add filter if category is specified
        if category_filter is not None:
            query = query.where(f"category = '{category_filter}'")
        
        results = query.to_pandas()
        return results
        
    except Exception as e:
        print(f"Error querying data: {e}")
        raise


def update_optional_fields(table, text_filter: str, new_category: Optional[str] = None, 
                          new_tags: Optional[str] = None):
    """Update optional fields for existing records.
    
    Args:
        table: LanceDB table instance
        text_filter: Text to filter records for update
        new_category: New category value (can be None)
        new_tags: New tags value (can be None)
    """
    try:
        # Build update values
        updates = {}
        if new_category is not None:
            updates['category'] = new_category
        if new_tags is not None:
            updates['tags'] = new_tags
        
        if not updates:
            print("No updates specified")
            return
        
        # Update records matching the filter
        table.update(where=f"text = '{text_filter}'", values=updates)
        print(f"Updated records matching text='{text_filter}'")
        
    except Exception as e:
        print(f"Error updating optional fields: {e}")
        raise


def main():
    """Main function demonstrating null/optional field handling."""
    try:
        # Connect to LanceDB
        db = lancedb.connect("./lancedb_nulls_demo")
        
        # Create sample data with some null fields
        data = [
            {
                "text": "Document with all fields",
                "vector": np.random.randn(384).astype(np.float32).tolist(),
                "category": "technology",
                "tags": "ai,ml,python"
            },
            {
                "text": "Document with null category",
                "vector": np.random.randn(384).astype(np.float32).tolist(),
                "category": None,
                "tags": "general"
            },
            {
                "text": "Document with null tags",
                "vector": np.random.randn(384).astype(np.float32).tolist(),
                "category": "science",
                "tags": None
            },
            {
                "text": "Document with both nulls",
                "vector": np.random.randn(384).astype(np.float32).tolist(),
                "category": None,
                "tags": None
            },
            {
                "text": "Document missing optional fields",
                "vector": np.random.randn(384).astype(np.float32).tolist(),
                # category and tags are intentionally omitted
            }
        ]
        
        # Create table with schema
        print("Creating table with optional fields...")
        table_name = "documents_with_nulls"
        
        # Drop table if it exists
        try:
            db.drop_table(table_name)
        except:
            pass
        
        # Create table with schema
        table = db.create_table(table_name, schema=Document)
        
        # Insert data with null fields
        print("\nInserting data with null/optional fields...")
        insert_with_nulls(table, data)
        
        # Verify insertion
        print("\nVerifying inserted data...")
        all_data = table.to_pandas()
        print(f"Total records: {len(all_data)}")
        print("\nSample records:")
        print(all_data[['text', 'category', 'tags']].head())
        
        # Count null values
        print("\nNull value counts:")
        print(f"Null categories: {all_data['category'].isna().sum()}")
        print(f"Null tags: {all_data['tags'].isna().sum()}")
        
        # Query with filters on optional fields
        print("\nQuerying records with category='technology'...")
        tech_results = query_with_null_filters(table, category_filter="technology")
        print(f"Found {len(tech_results)} technology records")
        
        # Query all records (no filter)
        print("\nQuerying all records...")
        all_results = query_with_null_filters(table)
        print(f"Found {len(all_results)} total records")
        
        # Update optional fields
        print("\nUpdating optional fields...")
        update_optional_fields(
            table, 
            text_filter="Document with both nulls",
            new_category="updated",
            new_tags="new,tags"
        )
        
        # Verify update
        updated_data = table.to_pandas()
        updated_record = updated_data[updated_data['text'] == "Document with both nulls"]
        print("\nUpdated record:")
        print(updated_record[['text', 'category', 'tags']])
        
        # Test error handling - try to insert without required field
        print("\nTesting error handling...")
        try:
            invalid_data = [
                {
                    "text": None,  # This should fail
                    "vector": np.random.randn(384).astype(np.float32).tolist()
                }
            ]
            insert_with_nulls(table, invalid_data)
        except ValueError as e:
            print(f"Caught expected error: {e}")
        
        # Test with wrong vector dimensions
        try:
            invalid_vector_data = [
                {
                    "text": "Invalid vector dimensions",
                    "vector": np.random.randn(128).astype(np.float32).tolist()  # Wrong size
                }
            ]
            insert_with_nulls(table, invalid_vector_data)
        except ValueError as e:
            print(f"Caught expected error: {e}")
        
        print("\n✓ Null handling complete - all operations successful!")
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    main()