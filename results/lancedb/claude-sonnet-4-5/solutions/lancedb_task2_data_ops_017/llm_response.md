```txt
# filepath: requirements.txt
pandas>=2.0.0
numpy>=1.24.0
lancedb>=0.5.0
```

```python
# filepath: data_ops.py
"""Create table with LanceModel schema."""

import lancedb
from lancedb.pydantic import LanceModel, Vector
import numpy as np
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
        Created table object
        
    Raises:
        ValueError: If data format is invalid
        Exception: If table creation fails
    """
    try:
        # Validate data format
        if not data:
            raise ValueError("Data cannot be empty")
        
        # Ensure all required fields are present
        required_fields = {'text', 'vector', 'category'}
        for item in data:
            if not all(field in item for field in required_fields):
                raise ValueError(f"Data must contain fields: {required_fields}")
            
            # Validate vector dimension
            if len(item['vector']) != 384:
                raise ValueError(f"Vector must be 384-dimensional, got {len(item['vector'])}")
        
        # Create table with schema
        # The schema parameter ensures type validation
        table = db.create_table(
            table_name,
            data=data,
            schema=Document,
            mode="overwrite"  # Overwrite if table exists
        )
        
        print(f"✓ Table '{table_name}' created successfully with {len(data)} documents")
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
        db = lancedb.connect("./my_lancedb")
        print("✓ Connected to LanceDB")
        
        # Create sample data with 384-dimensional vectors
        # In production, these would come from an embedding model
        sample_data = [
            {
                "text": "LanceDB is a vector database for AI applications",
                "vector": np.random.randn(384).tolist(),  # Random 384-dim vector
                "category": "technology"
            },
            {
                "text": "Machine learning models require efficient vector storage",
                "vector": np.random.randn(384).tolist(),
                "category": "ai"
            },
            {
                "text": "Semantic search enables finding similar documents",
                "vector": np.random.randn(384).tolist(),
                "category": "search"
            },
            {
                "text": "Embeddings capture semantic meaning of text",
                "vector": np.random.randn(384).tolist(),
                "category": "nlp"
            },
            {
                "text": "Vector databases optimize similarity search operations",
                "vector": np.random.randn(384).tolist(),
                "category": "database"
            }
        ]
        
        # Create table with schema
        table_name = "documents"
        table = create_table_with_schema(db, table_name, sample_data)
        
        # Verify table creation
        print(f"\n✓ Table info:")
        print(f"  - Name: {table.name}")
        print(f"  - Schema: {table.schema}")
        print(f"  - Count: {table.count_rows()} rows")
        
        # Display sample records
        print(f"\n✓ Sample records:")
        df = table.to_pandas()
        for idx, row in df.head(3).iterrows():
            print(f"  [{idx}] {row['category']}: {row['text'][:50]}...")
        
        print("\n✓ Schema-based table created successfully")
        
    except Exception as e:
        print(f"\n✗ Error in main: {e}")
        raise


if __name__ == "__main__":
    main()
```