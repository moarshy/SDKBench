```txt
# filepath: requirements.txt
pandas>=2.0.0
numpy>=1.24.0
lancedb>=0.5.0
pyarrow>=12.0.0
```

```python
# filepath: data_ops.py
"""Handle bad/mismatched vectors gracefully."""

import numpy as np
import lancedb
from typing import List, Dict, Any, Union
import pyarrow as pa

def validate_vector(vector, expected_dim: int) -> bool:
    """Validate vector dimension.
    
    Args:
        vector: Vector to validate (list, numpy array, or similar)
        expected_dim: Expected dimension of the vector
        
    Returns:
        True if vector is valid, False otherwise
    """
    try:
        # Check if vector is list or array-like
        if not isinstance(vector, (list, np.ndarray, tuple)):
            print(f"Invalid vector type: {type(vector)}")
            return False
        
        # Convert to numpy array for easier handling
        vec_array = np.array(vector)
        
        # Check if it's a 1D array
        if vec_array.ndim != 1:
            print(f"Vector must be 1-dimensional, got shape: {vec_array.shape}")
            return False
        
        # Check dimension matches expected
        if len(vec_array) != expected_dim:
            print(f"Vector dimension mismatch: expected {expected_dim}, got {len(vec_array)}")
            return False
        
        # Check for NaN or infinite values
        if not np.all(np.isfinite(vec_array)):
            print("Vector contains NaN or infinite values")
            return False
        
        return True
    
    except Exception as e:
        print(f"Error validating vector: {e}")
        return False


def safe_insert(table, data: List[Dict[str, Any]], vector_dim: int) -> Dict[str, int]:
    """Insert data with vector validation.
    
    Args:
        table: LanceDB table to insert into
        data: List of dictionaries containing records with vectors
        vector_dim: Expected dimension of vectors
        
    Returns:
        Dictionary with statistics about the insertion
    """
    valid_records = []
    invalid_records = []
    fixed_records = []
    
    for idx, record in enumerate(data):
        try:
            # Check if record has a vector field
            if 'vector' not in record:
                print(f"Record {idx} missing 'vector' field")
                invalid_records.append(idx)
                continue
            
            vector = record['vector']
            
            # Validate the vector
            if validate_vector(vector, vector_dim):
                # Vector is valid, add to valid records
                valid_records.append(record)
            else:
                # Try to fix the vector
                fixed_vector = fix_vector(vector, vector_dim)
                if fixed_vector is not None and validate_vector(fixed_vector, vector_dim):
                    # Successfully fixed the vector
                    fixed_record = record.copy()
                    fixed_record['vector'] = fixed_vector
                    valid_records.append(fixed_record)
                    fixed_records.append(idx)
                    print(f"Fixed vector for record {idx}")
                else:
                    # Cannot fix, skip this record
                    invalid_records.append(idx)
                    print(f"Skipping record {idx} due to invalid vector")
        
        except Exception as e:
            print(f"Error processing record {idx}: {e}")
            invalid_records.append(idx)
    
    # Insert valid records
    if valid_records:
        try:
            table.add(valid_records)
            print(f"Successfully inserted {len(valid_records)} records")
        except Exception as e:
            print(f"Error inserting records: {e}")
            return {
                'inserted': 0,
                'fixed': len(fixed_records),
                'invalid': len(invalid_records),
                'total': len(data)
            }
    else:
        print("No valid records to insert")
    
    return {
        'inserted': len(valid_records),
        'fixed': len(fixed_records),
        'invalid': len(invalid_records),
        'total': len(data)
    }


def fix_vector(vector, expected_dim: int) -> Union[np.ndarray, None]:
    """Attempt to fix a bad vector.
    
    Args:
        vector: Vector to fix
        expected_dim: Expected dimension
        
    Returns:
        Fixed vector as numpy array, or None if cannot be fixed
    """
    try:
        # Convert to numpy array
        vec_array = np.array(vector, dtype=np.float32)
        
        # Handle multi-dimensional arrays by flattening
        if vec_array.ndim > 1:
            vec_array = vec_array.flatten()
        
        # Replace NaN and infinite values with zeros
        if not np.all(np.isfinite(vec_array)):
            vec_array = np.nan_to_num(vec_array, nan=0.0, posinf=0.0, neginf=0.0)
        
        current_dim = len(vec_array)
        
        # If dimension is too small, pad with zeros
        if current_dim < expected_dim:
            padding = np.zeros(expected_dim - current_dim, dtype=np.float32)
            vec_array = np.concatenate([vec_array, padding])
        
        # If dimension is too large, truncate
        elif current_dim > expected_dim:
            vec_array = vec_array[:expected_dim]
        
        return vec_array.tolist()
    
    except Exception as e:
        print(f"Cannot fix vector: {e}")
        return None


def main():
    """Main function demonstrating bad vector handling."""
    
    # Connect to LanceDB
    db = lancedb.connect("./lancedb_data")
    
    # Define expected vector dimension
    VECTOR_DIM = 128
    
    # Create sample data with some bad vectors
    data = [
        # Valid record
        {
            "id": 1,
            "text": "Valid record",
            "vector": np.random.randn(VECTOR_DIM).tolist()
        },
        # Wrong dimension (too small)
        {
            "id": 2,
            "text": "Too small vector",
            "vector": np.random.randn(64).tolist()
        },
        # Wrong dimension (too large)
        {
            "id": 3,
            "text": "Too large vector",
            "vector": np.random.randn(256).tolist()
        },
        # Contains NaN
        {
            "id": 4,
            "text": "NaN vector",
            "vector": [np.nan] * VECTOR_DIM
        },
        # Contains infinity
        {
            "id": 5,
            "text": "Infinite vector",
            "vector": [np.inf if i % 2 == 0 else -np.inf for i in range(VECTOR_DIM)]
        },
        # Valid record
        {
            "id": 6,
            "text": "Another valid record",
            "vector": np.random.randn(VECTOR_DIM).tolist()
        },
        # Missing vector field
        {
            "id": 7,
            "text": "No vector field"
        },
        # Wrong type (string instead of list)
        {
            "id": 8,
            "text": "Wrong type",
            "vector": "not a vector"
        },
        # Multi-dimensional array
        {
            "id": 9,
            "text": "Multi-dimensional",
            "vector": np.random.randn(8, 16).tolist()
        },
        # Valid record
        {
            "id": 10,
            "text": "Final valid record",
            "vector": np.random.randn(VECTOR_DIM).tolist()
        }
    ]
    
    # Define schema
    schema = pa.schema([
        pa.field("id", pa.int64()),
        pa.field("text", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), VECTOR_DIM))
    ])
    
    # Create table with schema
    try:
        # Drop table if it exists
        try:
            db.drop_table("vectors_with_validation")
        except:
            pass
        
        # Create new table with first valid record to establish schema
        initial_data = [{
            "id": 0,
            "text": "Initial record",
            "vector": np.random.randn(VECTOR_DIM).tolist()
        }]
        
        table = db.create_table("vectors_with_validation", initial_data, schema=schema)
        print(f"Created table with schema (vector dimension: {VECTOR_DIM})")
        
        # Safely insert data with validation
        print("\nInserting data with validation...")
        stats = safe_insert(table, data, VECTOR_DIM)
        
        # Print statistics
        print("\n" + "="*50)
        print("Insertion Statistics:")
        print(f"  Total records: {stats['total']}")
        print(f"  Successfully inserted: {stats['inserted']}")
        print(f"  Fixed and inserted: {stats['fixed']}")
        print(f"  Invalid (skipped): {stats['invalid']}")
        print("="*50)
        
        # Verify the table contents
        print(f"\nTotal records in table: {table.count_rows()}")
        
        # Show sample of inserted data
        print("\nSample of inserted records:")
        df = table.to_pandas()
        print(df[['id', 'text']].head(10))
        
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nBad vector handling complete")


if __name__ == "__main__":
    main()
```

This solution provides a comprehensive approach to handling bad/mismatched vectors in LanceDB:

**Key Features:**

1. **`validate_vector()`**: Validates vectors by checking:
   - Type (list, numpy array, tuple)
   - Dimensionality (must be 1D)
   - Size (matches expected dimension)
   - Values (no NaN or infinite values)

2. **`safe_insert()`**: Safely inserts data with validation:
   - Validates each vector before insertion
   - Attempts to fix bad vectors
   - Tracks statistics (inserted, fixed, invalid)
   - Skips records that cannot be fixed

3. **`fix_vector()`**: Attempts to repair bad vectors:
   - Flattens multi-dimensional arrays
   - Replaces NaN/infinite values with zeros
   - Pads short vectors with zeros
   - Truncates long vectors

4. **Error Handling**: Comprehensive try-catch blocks throughout

5. **Demo**: The `main()` function demonstrates handling various bad vector scenarios:
   - Wrong dimensions (too small/large)
   - NaN values
   - Infinite values
   - Missing vector field
   - Wrong data types
   - Multi-dimensional arrays

The solution is production-ready with proper error handling, logging, and statistics tracking.