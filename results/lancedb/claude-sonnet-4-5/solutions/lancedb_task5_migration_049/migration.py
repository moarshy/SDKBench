# filepath: migration.py
"""Schema Migration: Migrate/rebuild vector index.

Migrate existing LanceDB table to new schema while preserving data.
"""

import lancedb
import pandas as pd
import pyarrow as pa
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
import shutil

# Old schema (before migration)
# class OldDocument:
#     text: str
#     vector: Vector(384)

# New schema with additional fields
class NewDocument(lancedb.pydantic_models.LanceModel):
    """New schema with enhanced fields."""
    text: str
    vector: List[float]  # Vector(384) - embedding dimension
    metadata: Optional[str] = None  # New field
    timestamp: Optional[str] = None  # New field
    category: Optional[str] = "general"  # New field with default

# Database configuration
DB_PATH = "./my_lancedb"
TABLE_NAME = "documents"
BACKUP_SUFFIX = "_backup"
VECTOR_DIM = 384

def connect_database() -> lancedb.DBConnection:
    """Connect to existing database.
    
    Returns:
        LanceDB connection object
    """
    try:
        db = lancedb.connect(DB_PATH)
        print(f"✓ Connected to database at {DB_PATH}")
        return db
    except Exception as e:
        print(f"✗ Failed to connect to database: {e}")
        raise

def backup_data(table_name: str) -> pd.DataFrame:
    """Backup existing table data.
    
    Args:
        table_name: Name of the table to backup
        
    Returns:
        DataFrame containing all table data
    """
    try:
        db = connect_database()
        
        # Check if table exists
        table_names = db.table_names()
        if table_name not in table_names:
            print(f"✗ Table '{table_name}' does not exist")
            print(f"Available tables: {table_names}")
            return pd.DataFrame()
        
        # Open existing table
        table = db.open_table(table_name)
        
        # Read all data to DataFrame
        backup_df = table.to_pandas()
        record_count = len(backup_df)
        
        print(f"✓ Backed up {record_count} records from '{table_name}'")
        
        # Save backup to disk
        backup_path = f"{DB_PATH}/{table_name}{BACKUP_SUFFIX}.parquet"
        backup_df.to_parquet(backup_path)
        print(f"✓ Backup saved to {backup_path}")
        
        return backup_df
        
    except Exception as e:
        print(f"✗ Failed to backup data: {e}")
        raise

def migrate_data(old_data: pd.DataFrame, new_schema: type) -> List[Dict[str, Any]]:
    """Transform data to match new schema.
    
    Args:
        old_data: DataFrame with old schema
        new_schema: New schema class definition
        
    Returns:
        List of dictionaries matching new schema
    """
    try:
        if old_data.empty:
            print("⚠ No data to migrate")
            return []
        
        migrated_records = []
        current_timestamp = datetime.now().isoformat()
        
        for idx, row in old_data.iterrows():
            # Create new record with transformed data
            new_record = {
                'text': row.get('text', ''),
                'vector': row.get('vector', [0.0] * VECTOR_DIM),
                # Add new fields with defaults
                'metadata': row.get('metadata', None),
                'timestamp': row.get('timestamp', current_timestamp),
                'category': row.get('category', 'general')
            }
            
            # Ensure vector is a list
            if hasattr(new_record['vector'], 'tolist'):
                new_record['vector'] = new_record['vector'].tolist()
            
            migrated_records.append(new_record)
        
        print(f"✓ Migrated {len(migrated_records)} records to new schema")
        return migrated_records
        
    except Exception as e:
        print(f"✗ Failed to migrate data: {e}")
        raise

def create_new_table(table_name: str, data: List[Dict[str, Any]]) -> None:
    """Create new table with migrated data.
    
    Args:
        table_name: Name of the table to create
        data: Migrated data matching new schema
    """
    try:
        db = connect_database()
        
        if not data:
            print("⚠ No data to create table with")
            return
        
        # Drop old table if exists
        table_names = db.table_names()
        if table_name in table_names:
            db.drop_table(table_name)
            print(f"✓ Dropped old table '{table_name}'")
        
        # Create table with new schema
        # LanceDB will infer schema from the data
        table = db.create_table(
            table_name,
            data=data,
            mode="overwrite"
        )
        
        print(f"✓ Created new table '{table_name}' with {len(data)} records")
        
        # Create vector index for better search performance
        try:
            table.create_index(
                metric="cosine",
                num_partitions=256,
                num_sub_vectors=96
            )
            print(f"✓ Created vector index on '{table_name}'")
        except Exception as e:
            print(f"⚠ Could not create vector index: {e}")
        
    except Exception as e:
        print(f"✗ Failed to create new table: {e}")
        raise

def verify_migration(table_name: str, expected_count: int) -> bool:
    """Verify migration was successful.
    
    Args:
        table_name: Name of the migrated table
        expected_count: Expected number of records
        
    Returns:
        True if verification passed, False otherwise
    """
    try:
        db = connect_database()
        
        # Check table exists
        table_names = db.table_names()
        if table_name not in table_names:
            print(f"✗ Verification failed: Table '{table_name}' does not exist")
            return False
        
        print(f"✓ Table '{table_name}' exists")
        
        # Open table and verify
        table = db.open_table(table_name)
        
        # Verify record count
        actual_count = table.count_rows()
        if actual_count != expected_count:
            print(f"✗ Record count mismatch: expected {expected_count}, got {actual_count}")
            return False
        
        print(f"✓ Record count matches: {actual_count}")
        
        # Verify new schema fields
        df = table.to_pandas()
        required_fields = ['text', 'vector', 'metadata', 'timestamp', 'category']
        
        for field in required_fields:
            if field not in df.columns:
                print(f"✗ Missing field: {field}")
                return False
        
        print(f"✓ All required fields present: {required_fields}")
        
        # Sample a record to verify structure
        if len(df) > 0:
            sample = df.iloc[0]
            print(f"✓ Sample record:")
            print(f"  - text: {sample['text'][:50]}...")
            print(f"  - vector dimension: {len(sample['vector'])}")
            print(f"  - metadata: {sample['metadata']}")
            print(f"  - timestamp: {sample['timestamp']}")
            print(f"  - category: {sample['category']}")
        
        print("✓ Migration verification passed!")
        return True
        
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False

def rollback_migration(table_name: str) -> None:
    """Rollback migration by restoring from backup.
    
    Args:
        table_name: Name of the table to rollback
    """
    try:
        backup_path = f"{DB_PATH}/{table_name}{BACKUP_SUFFIX}.parquet"
        
        if not os.path.exists(backup_path):
            print(f"✗ No backup found at {backup_path}")
            return
        
        # Read backup data
        backup_df = pd.read_parquet(backup_path)
        backup_data = backup_df.to_dict('records')
        
        # Restore table
        db = connect_database()
        db.drop_table(table_name)
        db.create_table(table_name, data=backup_data, mode="overwrite")
        
        print(f"✓ Rolled back '{table_name}' from backup")
        
    except Exception as e:
        print(f"✗ Rollback failed: {e}")
        raise

def run_migration() -> None:
    """Execute the complete migration.
    
    Migration steps:
    1. Backup existing data
    2. Transform to new schema
    3. Create new table
    4. Verify migration
    5. Cleanup or rollback
    """
    print("=" * 60)
    print("Starting LanceDB Migration")
    print("=" * 60)
    
    try:
        # Step 1: Backup existing data
        print("\n[Step 1/4] Backing up existing data...")
        old_data = backup_data(TABLE_NAME)
        
        if old_data.empty:
            print("⚠ No existing data found. Creating new table with schema...")
            # Create empty table with new schema
            db = connect_database()
            sample_data = [{
                'text': 'Sample document',
                'vector': [0.0] * VECTOR_DIM,
                'metadata': None,
                'timestamp': datetime.now().isoformat(),
                'category': 'general'
            }]
            db.create_table(TABLE_NAME, data=sample_data, mode="overwrite")
            print("✓ Created new table with schema")
            return
        
        expected_count = len(old_data)
        
        # Step 2: Transform to new schema
        print("\n[Step 2/4] Transforming data to new schema...")
        migrated_data = migrate_data(old_data, NewDocument)
        
        # Step 3: Create new table
        print("\n[Step 3/4] Creating new table with migrated data...")
        create_new_table(TABLE_NAME, migrated_data)
        
        # Step 4: Verify migration
        print("\n[Step 4/4] Verifying migration...")
        verification_passed = verify_migration(TABLE_NAME, expected_count)
        
        if verification_passed:
            print("\n" + "=" * 60)
            print("✓ Migration completed successfully!")
            print("=" * 60)
            print(f"\nBackup preserved at: {DB_PATH}/{TABLE_NAME}{BACKUP_SUFFIX}.parquet")
            print("You can safely delete the backup after confirming everything works.")
        else:
            print("\n" + "=" * 60)
            print("✗ Migration verification failed!")
            print("=" * 60)
            print("\nAttempting rollback...")
            rollback_migration(TABLE_NAME)
            
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ Migration failed with error: {e}")
        print("=" * 60)
        print("\nAttempting rollback...")
        try:
            rollback_migration(TABLE_NAME)
        except Exception as rollback_error:
            print(f"✗ Rollback also failed: {rollback_error}")
            print("Please restore manually from backup")

if __name__ == "__main__":
    run_migration()