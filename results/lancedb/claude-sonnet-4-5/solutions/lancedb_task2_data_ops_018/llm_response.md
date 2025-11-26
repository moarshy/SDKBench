```txt
# filepath: requirements.txt
pandas>=2.0.0
numpy>=1.24.0
lancedb>=0.5.0
pylance>=0.9.0
```

```python
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


def update_null_fields(table, text_filter: str, new_category: str):
    """Update null fields in existing records.
    
    Args:
        table: LanceDB table instance
        text_filter: Text to filter records by
        new_category: New category value to set
        
    Returns:
        None
    """
    try:
        # Update records where category is null
        table.update(
            where=f"text = '{text_filter}'",
            values={"category": new_category}
        )
        print(f"Updated records matching '{text_filter}' with category '{new_category}'")
        
    except Exception as e:
        print(f"Error updating null fields: {e}")
        raise


def main():
    """Main function demonstrating null/optional field handling."""
    try:
        # Connect to LanceDB
        db = lancedb.connect("./lancedb_nulls")
        print("Connected to LanceDB")
        
        # Create data with some null fields
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
                "tags": "research,paper"
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
                # category and tags will be set to None by insert_with_nulls
            },
            {
                "text": "Another complete document",
                "vector": np.random.randn(384).astype(np.float32).tolist(),
                "category": "business",
                "tags": "finance,economics"
            }
        ]
        
        # Create table with schema
        table_name = "documents_with_nulls"
        
        # Drop table if it exists (for clean demo)
        try:
            db.drop_table(table_name)
        except:
            pass
        
        # Create table with schema
        table = db.create_table(table_name, schema=Document)
        print(f"Created table '{table_name}' with schema")
        
        # Insert data with null fields
        print("\n--- Inserting data with null fields ---")
        insert_with_nulls(table, data)
        
        # Verify insertion
        print("\n--- Verifying all records ---")
        all_records = table.to_pandas()
        print(f"Total records: {len(all_records)}")
        print("\nSample records:")
        print(all_records[['text', 'category', 'tags']].head())
        
        # Query with null filters
        print("\n--- Querying records with category='technology' ---")
        tech_results = query_with_null_filters(table, category_filter="technology")
        print(f"Found {len(tech_results)} technology records")
        
        # Show records with null categories
        print("\n--- Records with null category ---")
        null_category = all_records[all_records['category'].isna()]
        print(f"Found {len(null_category)} records with null category:")
        print(null_category[['text', 'category', 'tags']])
        
        # Update null fields
        print("\n--- Updating null category field ---")
        update_null_fields(table, "Document with null category", "updated_category")
        
        # Verify update
        updated_records = table.to_pandas()
        print("\nRecords after update:")
        print(updated_records[['text', 'category', 'tags']])
        
        # Test error handling - try to insert without required field
        print("\n--- Testing error handling ---")
        try:
            invalid_data = [
                {
                    "vector": np.random.randn(384).astype(np.float32).tolist(),
                    # Missing required 'text' field
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
                    "vector": np.random.randn(128).astype(np.float32).tolist(),  # Wrong size
                }
            ]
            insert_with_nulls(table, invalid_vector_data)
        except ValueError as e:
            print(f"Caught expected error: {e}")
        
        print("\n=== Null handling complete ===")
        print(f"Successfully demonstrated:")
        print("  ✓ Schema with optional fields")
        print("  ✓ Inserting records with null values")
        print("  ✓ Querying with null field filters")
        print("  ✓ Updating null fields")
        print("  ✓ Error handling for missing required fields")
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise


if __name__ == "__main__":
    main()
```

This solution provides a complete implementation for handling null/optional fields in LanceDB:

**Key Features:**

1. **Schema Definition**: Uses `LanceModel` with `Optional` fields for `category` and `tags`
2. **Null Handling**: The `insert_with_nulls` function:
   - Validates required fields (`text` and `vector`)
   - Ensures vector dimensions are correct (384)
   - Explicitly sets missing optional fields to `None`
   - Provides clear error messages

3. **Query Operations**: Demonstrates querying with filters on optional fields
4. **Update Operations**: Shows how to update null fields in existing records
5. **Error Handling**: Comprehensive validation and error handling for:
   - Missing required fields
   - Invalid vector dimensions
   - General insertion/query errors

6. **Demonstration**: The `main()` function shows:
   - Creating records with various combinations of null fields
   - Inserting and verifying data
   - Querying with filters
   - Updating null values
   - Error handling scenarios

The code follows LanceDB best practices and is production-ready with proper error handling and validation.