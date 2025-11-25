I'll help you create a complete migration solution for LanceDB. This will handle schema changes, data migration, and verification.

```txt
# filepath: requirements.txt
lancedb>=0.5.0
pandas>=2.0.0
pyarrow>=12.0.0
```

```python
# filepath: migration.py
"""Schema Migration: Migrate/rebuild vector index.

Migrate existing LanceDB table to new schema while preserving data.
"""

import lancedb
import pandas as pd
import pyarrow as pa
from typing import Optional, List, Dict, Any
import os
from datetime import datetime

# Old schema (before migration)
# class OldDocument:
#     text: str
#     vector: Vector(384)

# New schema with additional fields
class NewDocument(lancedb.pydantic_models.LanceModel):
    """New schema with enhanced fields."""
    text: str
    vector: lancedb.pydantic_models.Vector(384)
    metadata: Optional[str] = None  # New field
    timestamp: Optional[str] = None  # New field
    category: Optional[str] = "general"  # New field with default

def connect_database(db_path: str = "./lancedb") -> lancedb.DBConnection:
    """Connect to existing database.
    
    Args:
        db_path: Path to LanceDB database directory
        
    Returns:
        LanceDB connection object
    """
    try:
        db = lancedb.connect(db_path)
        print(f"✓ Connected to database at: {db_path}")
        return db
    except Exception as e:
        print(f"✗ Error connecting to database: {e}")
        raise

def backup_data(db: lancedb.DBConnection, table_name: str) -> pd.DataFrame:
    """Backup existing table data.
    
    Args:
        db: LanceDB connection
        table_name: Name of table to backup
        
    Returns:
        DataFrame containing all table data
    """
    try:
        # Open existing table
        table = db.open_table(table_name)
        
        # Read all data to DataFrame
        backup_df = table.to_pandas()
        
        print(f"✓ Backed up {len(backup_df)} records from '{table_name}'")
        
        # Save backup to file for safety
        backup_filename = f"{table_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
        backup_df.to_parquet(backup_filename)
        print(f"✓ Backup saved to: {backup_filename}")
        
        return backup_df
    except Exception as e:
        print(f"✗ Error backing up data: {e}")
        raise

def migrate_data(old_data: pd.DataFrame, new_schema: type) -> List[Dict[str, Any]]:
    """Transform data to match new schema.
    
    Args:
        old_data: DataFrame with old schema data
        new_schema: New schema class (LanceModel)
        
    Returns:
        List of dictionaries matching new schema
    """
    try:
        migrated_records = []
        current_timestamp = datetime.now().isoformat()
        
        for idx, row in old_data.iterrows():
            # Create new record with old data
            new_record = {
                'text': row['text'],
                'vector': row['vector'].tolist() if hasattr(row['vector'], 'tolist') else row['vector'],
            }
            
            # Handle new fields with defaults
            # Check if metadata exists in old data
            if 'metadata' in row and pd.notna(row['metadata']):
                new_record['metadata'] = row['metadata']
            else:
                new_record['metadata'] = None
            
            # Add timestamp
            if 'timestamp' in row and pd.notna(row['timestamp']):
                new_record['timestamp'] = row['timestamp']
            else:
                new_record['timestamp'] = current_timestamp
            
            # Add category with default
            if 'category' in row and pd.notna(row['category']):
                new_record['category'] = row['category']
            else:
                new_record['category'] = "general"
            
            migrated_records.append(new_record)
        
        print(f"✓ Migrated {len(migrated_records)} records to new schema")
        return migrated_records
    except Exception as e:
        print(f"✗ Error migrating data: {e}")
        raise

def create_new_table(
    db: lancedb.DBConnection,
    table_name: str,
    data: List[Dict[str, Any]],
    schema: type
) -> lancedb.table.Table:
    """Create new table with migrated data.
    
    Args:
        db: LanceDB connection
        table_name: Name of table to create
        data: Migrated data records
        schema: New schema class
        
    Returns:
        Newly created table
    """
    try:
        # Drop old table if exists
        existing_tables = db.table_names()
        if table_name in existing_tables:
            db.drop_table(table_name)
            print(f"✓ Dropped old table '{table_name}'")
        
        # Create table with new schema
        table = db.create_table(
            table_name,
            data=data,
            schema=schema,
            mode="create"
        )
        
        print(f"✓ Created new table '{table_name}' with {len(data)} records")
        return table
    except Exception as e:
        print(f"✗ Error creating new table: {e}")
        raise

def verify_migration(
    db: lancedb.DBConnection,
    table_name: str,
    expected_count: int,
    new_schema: type
) -> bool:
    """Verify migration was successful.
    
    Args:
        db: LanceDB connection
        table_name: Name of migrated table
        expected_count: Expected number of records
        new_schema: New schema class
        
    Returns:
        True if verification passed, False otherwise
    """
    try:
        # Check table exists
        if table_name not in db.table_names():
            print(f"✗ Table '{table_name}' does not exist")
            return False
        
        # Open table
        table = db.open_table(table_name)
        
        # Verify record count
        actual_count = table.count_rows()
        if actual_count != expected_count:
            print(f"✗ Record count mismatch: expected {expected_count}, got {actual_count}")
            return False
        
        print(f"✓ Record count verified: {actual_count}")
        
        # Verify schema fields
        df_sample = table.to_pandas().head(1)
        schema_fields = set(new_schema.model_fields.keys())
        table_fields = set(df_sample.columns)
        
        if not schema_fields.issubset(table_fields):
            missing_fields = schema_fields - table_fields
            print(f"✗ Missing fields in table: {missing_fields}")
            return False
        
        print(f"✓ Schema fields verified: {list(schema_fields)}")
        
        # Test vector search functionality
        sample_vector = df_sample['vector'].iloc[0]
        if hasattr(sample_vector, 'tolist'):
            sample_vector = sample_vector.tolist()
        
        search_results = table.search(sample_vector).limit(1).to_pandas()
        if len(search_results) == 0:
            print("✗ Vector search test failed")
            return False
        
        print("✓ Vector search functionality verified")
        
        print(f"\n✓ Migration verification PASSED for '{table_name}'")
        return True
    except Exception as e:
        print(f"✗ Error during verification: {e}")
        return False

def run_migration(
    db_path: str = "./lancedb",
    table_name: str = "documents",
    new_schema: type = NewDocument
):
    """Execute the complete migration.
    
    Args:
        db_path: Path to LanceDB database
        table_name: Name of table to migrate
        new_schema: New schema class
    """
    print("=" * 60)
    print("Starting LanceDB Migration")
    print("=" * 60)
    
    try:
        # Step 1: Connect to database
        print("\n[1/5] Connecting to database...")
        db = connect_database(db_path)
        
        # Step 2: Backup existing data
        print("\n[2/5] Backing up existing data...")
        old_data = backup_data(db, table_name)
        original_count = len(old_data)
        
        # Step 3: Transform to new schema
        print("\n[3/5] Transforming data to new schema...")
        migrated_data = migrate_data(old_data, new_schema)
        
        # Step 4: Create new table
        print("\n[4/5] Creating new table with migrated data...")
        new_table = create_new_table(db, table_name, migrated_data, new_schema)
        
        # Step 5: Verify migration
        print("\n[5/5] Verifying migration...")
        verification_passed = verify_migration(db, table_name, original_count, new_schema)
        
        if verification_passed:
            print("\n" + "=" * 60)
            print("✓ MIGRATION COMPLETED SUCCESSFULLY")
            print("=" * 60)
            print(f"Table: {table_name}")
            print(f"Records migrated: {original_count}")
            print(f"New schema: {new_schema.__name__}")
        else:
            print("\n" + "=" * 60)
            print("✗ MIGRATION VERIFICATION FAILED")
            print("=" * 60)
            print("Please check the backup file and retry migration")
            
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ MIGRATION FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        print("Data backup has been preserved. Please review and retry.")
        raise

if __name__ == "__main__":
    # Example usage with custom parameters
    run_migration(
        db_path="./lancedb",
        table_name="documents",
        new_schema=NewDocument
    )

```

This migration solution provides:

## Key Features:

1. **Complete Migration Pipeline**:
   - Database connection
   - Data backup (with file export)
   - Schema transformation
   - Table recreation
   - Verification

2. **Safety Measures**:
   - Automatic backup to Parquet file before migration
   - Timestamped backup files
   - Comprehensive error handling
   - Verification step to ensure data integrity

3. **Schema Migration**:
   - Handles new fields with defaults
   - Preserves existing data
   - Supports optional fields
   - Uses LanceDB's Pydantic models

4. **Verification**:
   - Record count validation
   - Schema field validation
   - Vector search functionality test

5. **Production-Ready**:
   - Detailed logging and progress tracking
   - Error handling at each step
   - Backup preservation on failure
   - Type hints for better IDE support

## Usage:

```python
# Basic usage
run_migration()

# Custom usage
run_migration(
    db_path="./my_lancedb",
    table_name="my_table",
    new_schema=MyCustomSchema
)
```

The migration handles the transition from older LanceDB versions to the latest API patterns while preserving all your data safely.