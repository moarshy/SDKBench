"""Handle bad/mismatched vectors gracefully."""

import numpy as np
import lancedb
import pyarrow as pa
from typing import List, Dict, Any, Union


def validate_vector(vector, expected_dim: int) -> bool:
    """Validate vector dimension.
    
    Args:
        vector: Vector to validate (list, numpy array, or other array-like)
        expected_dim: Expected dimension of the vector
        
    Returns:
        True if vector is valid, False otherwise
    """
    try:
        # Check if vector is list or array-like
        if not isinstance(vector, (list, np.ndarray, tuple)):
            return False
        
        # Convert to numpy array for consistent handling
        vec_array = np.array(vector)
        
        # Check if it's a 1D array
        if vec_array.ndim != 1:
            return False
        
        # Check dimension matches expected
        if len(vec_array) != expected_dim:
            return False
        
        # Check for NaN or infinite values
        if not np.all(np.isfinite(vec_array)):
            return False
        
        return True
    except (ValueError, TypeError):
        return False


def safe_insert(table, data: List[Dict[str, Any]], vector_dim: int, vector_column: str = "vector") -> Dict[str, Any]:
    """Insert data with vector validation.
    
    Args:
        table: LanceDB table to insert into
        data: List of dictionaries containing records to insert
        vector_dim: Expected dimension of vectors
        vector_column: Name of the vector column (default: "vector")
        
    Returns:
        Dictionary with statistics about the insertion
    """
    valid_records = []
    invalid_records = []
    fixed_records = []
    
    for idx, record in enumerate(data):
        try:
            # Check if vector column exists
            if vector_column not in record:
                invalid_records.append({
                    "index": idx,
                    "reason": f"Missing '{vector_column}' column",
                    "record": record
                })
                continue
            
            vector = record[vector_column]
            
            # Validate the vector
            if validate_vector(vector, vector_dim):
                valid_records.append(record)
            else:
                # Try to fix common issues
                try:
                    vec_array = np.array(vector, dtype=np.float32)
                    
                    # Handle wrong dimensions
                    if vec_array.ndim != 1:
                        vec_array = vec_array.flatten()
                    
                    # Handle dimension mismatch
                    if len(vec_array) < vector_dim:
                        # Pad with zeros
                        vec_array = np.pad(vec_array, (0, vector_dim - len(vec_array)), 
                                          mode='constant', constant_values=0)
                        fixed_record = record.copy()
                        fixed_record[vector_column] = vec_array.tolist()
                        valid_records.append(fixed_record)
                        fixed_records.append({
                            "index": idx,
                            "action": "padded",
                            "original_dim": len(vector),
                            "new_dim": vector_dim
                        })
                    elif len(vec_array) > vector_dim:
                        # Truncate
                        vec_array = vec_array[:vector_dim]
                        fixed_record = record.copy()
                        fixed_record[vector_column] = vec_array.tolist()
                        valid_records.append(fixed_record)
                        fixed_records.append({
                            "index": idx,
                            "action": "truncated",
                            "original_dim": len(vector),
                            "new_dim": vector_dim
                        })
                    else:
                        # Replace NaN/inf with zeros
                        if not np.all(np.isfinite(vec_array)):
                            vec_array = np.nan_to_num(vec_array, nan=0.0, posinf=0.0, neginf=0.0)
                            fixed_record = record.copy()
                            fixed_record[vector_column] = vec_array.tolist()
                            valid_records.append(fixed_record)
                            fixed_records.append({
                                "index": idx,
                                "action": "replaced_invalid_values"
                            })
                        else:
                            invalid_records.append({
                                "index": idx,
                                "reason": "Unknown validation failure",
                                "record": record
                            })
                except Exception as e:
                    invalid_records.append({
                        "index": idx,
                        "reason": f"Failed to fix: {str(e)}",
                        "record": record
                    })
        except Exception as e:
            invalid_records.append({
                "index": idx,
                "reason": f"Processing error: {str(e)}",
                "record": record
            })
    
    # Insert valid records
    inserted_count = 0
    if valid_records:
        try:
            table.add(valid_records)
            inserted_count = len(valid_records)
        except Exception as e:
            print(f"Error inserting records: {e}")
    
    # Return statistics
    stats = {
        "total_records": len(data),
        "inserted": inserted_count,
        "fixed": len(fixed_records),
        "invalid": len(invalid_records),
        "fixed_details": fixed_records,
        "invalid_details": invalid_records
    }
    
    return stats


def main():
    """Demonstrate handling of bad/mismatched vectors."""
    
    # Connect to LanceDB
    db = lancedb.connect("./lancedb_data")
    
    # Define vector dimension
    VECTOR_DIM = 128
    
    # Define schema
    schema = pa.schema([
        pa.field("id", pa.int64()),
        pa.field("text", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), VECTOR_DIM))
    ])
    
    # Create table with schema
    try:
        # Drop table if exists
        try:
            db.drop_table("test_vectors")
        except:
            pass
        
        # Create new table
        table = db.create_table("test_vectors", schema=schema)
        print(f"Created table with vector dimension: {VECTOR_DIM}")
    except Exception as e:
        print(f"Error creating table: {e}")
        return
    
    # Create test data with various bad vectors
    test_data = [
        # Valid vector
        {
            "id": 1,
            "text": "Valid vector",
            "vector": np.random.randn(VECTOR_DIM).tolist()
        },
        # Vector too short
        {
            "id": 2,
            "text": "Short vector",
            "vector": np.random.randn(64).tolist()
        },
        # Vector too long
        {
            "id": 3,
            "text": "Long vector",
            "vector": np.random.randn(256).tolist()
        },
        # Vector with NaN
        {
            "id": 4,
            "text": "NaN vector",
            "vector": [float('nan')] * VECTOR_DIM
        },
        # Vector with infinity
        {
            "id": 5,
            "text": "Inf vector",
            "vector": [float('inf')] * VECTOR_DIM
        },
        # Missing vector
        {
            "id": 6,
            "text": "Missing vector"
        },
        # Wrong type (string)
        {
            "id": 7,
            "text": "Wrong type",
            "vector": "not a vector"
        },
        # 2D array
        {
            "id": 8,
            "text": "2D array",
            "vector": np.random.randn(8, 16).tolist()
        },
        # Another valid vector
        {
            "id": 9,
            "text": "Another valid vector",
            "vector": np.random.randn(VECTOR_DIM).tolist()
        }
    ]
    
    print(f"\nAttempting to insert {len(test_data)} records...")
    
    # Safely insert data
    stats = safe_insert(table, test_data, VECTOR_DIM)
    
    # Print statistics
    print("\n=== Insertion Statistics ===")
    print(f"Total records: {stats['total_records']}")
    print(f"Successfully inserted: {stats['inserted']}")
    print(f"Fixed and inserted: {stats['fixed']}")
    print(f"Invalid (skipped): {stats['invalid']}")
    
    if stats['fixed_details']:
        print("\n=== Fixed Records ===")
        for fix in stats['fixed_details']:
            print(f"  Record {fix['index']}: {fix['action']}", end="")
            if 'original_dim' in fix:
                print(f" (dim: {fix['original_dim']} -> {fix['new_dim']})")
            else:
                print()
    
    if stats['invalid_details']:
        print("\n=== Invalid Records (Skipped) ===")
        for invalid in stats['invalid_details']:
            print(f"  Record {invalid['index']}: {invalid['reason']}")
    
    # Verify inserted data
    print(f"\n=== Table Contents ===")
    try:
        result = table.to_pandas()
        print(f"Total rows in table: {len(result)}")
        print("\nSample records:")
        print(result[['id', 'text']].head())
        
        # Verify vector dimensions
        if len(result) > 0:
            first_vector = result.iloc[0]['vector']
            print(f"\nVector dimension check: {len(first_vector)} (expected: {VECTOR_DIM})")
    except Exception as e:
        print(f"Error reading table: {e}")
    
    print("\nBad vector handling complete!")


if __name__ == "__main__":
    main()