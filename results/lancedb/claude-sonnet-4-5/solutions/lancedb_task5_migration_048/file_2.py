"""Schema Migration: Add new field with defaults.

Migrate existing LanceDB table to new schema while preserving data.
"""

import lancedb
import pandas as pd
import pyarrow as pa
from typing import Optional
from datetime import datetime

# Old schema (before migration)
# class OldDocument:
#     text: str
#     vector: Vector(384)

# New schema with additional fields
def get_new_schema():
    """Define new schema with additional fields."""
    return pa.schema([
        pa.field("text", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), 384)),
        pa.field("created_at", pa.timestamp('ms')),  # New field with default
        pa.field("category", pa.string()),  # New field with default
        pa.field("priority", pa.int32()),  # New field with default
    ])

def connect_database(db_path: str = "./lancedb"):
    """Connect to existing database.
    
    Args:
        db_path: Path to LanceDB database
        
    Returns:
        LanceDB connection object
    """
    try:
        db = lancedb.connect(db_path)
        print(f"✓ Connected to database at {db_path}")
        return db
    except Exception as e:
        print(f"✗ Error connecting to database: {e}")
        raise

def backup_data(db, table_name: str):
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
        return backup_df
    except Exception as e:
        print(f"✗ Error backing up data: {e}")
        raise

def migrate_data(old_data: pd.DataFrame, new_schema: pa.Schema):
    """Transform data to match new schema.
    
    Args:
        old_data: DataFrame with old schema
        new_schema: PyArrow schema for new table
        
    Returns:
        DataFrame with new schema and default values
    """
    try:
        # Create a copy to avoid modifying original
        migrated_df = old_data.copy()
        
        # Add new fields with default values
        if 'created_at' not in migrated_df.columns:
            # Default to current timestamp
            migrated_df['created_at'] = pd.Timestamp.now()
            print("  Added 'created_at' field with current timestamp")
        
        if 'category' not in migrated_df.columns:
            # Default to 'uncategorized'
            migrated_df['category'] = 'uncategorized'
            print("  Added 'category' field with default 'uncategorized'")
        
        if 'priority' not in migrated_df.columns:
            # Default to medium priority (5)
            migrated_df['priority'] = 5
            print("  Added 'priority' field with default value 5")
        
        # Ensure column order matches schema
        schema_columns = [field.name for field in new_schema]
        migrated_df = migrated_df[schema_columns]
        
        print(f"✓ Migrated {len(migrated_df)} records to new schema")
        return migrated_df
    except Exception as e:
        print(f"✗ Error migrating data: {e}")
        raise

def create_new_table(db, table_name: str, data: pd.DataFrame, schema: pa.Schema):
    """Create new table with migrated data.
    
    Args:
        db: LanceDB connection
        table_name: Name of table to create
        data: Migrated data
        schema: PyArrow schema for new table
    """
    try:
        # Drop old table if exists
        try:
            db.drop_table(table_name)
            print(f"  Dropped old table '{table_name}'")
        except Exception:
            print(f"  Table '{table_name}' does not exist, creating new")
        
        # Create table with new schema
        table = db.create_table(
            table_name,
            data=data,
            schema=schema,
            mode="overwrite"
        )
        
        print(f"✓ Created new table '{table_name}' with {len(data)} records")
        return table
    except Exception as e:
        print(f"✗ Error creating new table: {e}")
        raise

def verify_migration(db, table_name: str, expected_count: int, expected_schema: pa.Schema):
    """Verify migration was successful.
    
    Args:
        db: LanceDB connection
        table_name: Name of table to verify
        expected_count: Expected number of records
        expected_schema: Expected schema
        
    Returns:
        bool: True if verification passed
    """
    try:
        # Check table exists
        table_names = db.table_names()
        if table_name not in table_names:
            print(f"✗ Table '{table_name}' does not exist")
            return False
        print(f"✓ Table '{table_name}' exists")
        
        # Open table and verify record count
        table = db.open_table(table_name)
        actual_count = table.count_rows()
        
        if actual_count != expected_count:
            print(f"✗ Record count mismatch: expected {expected_count}, got {actual_count}")
            return False
        print(f"✓ Record count matches: {actual_count}")
        
        # Verify schema fields
        table_schema = table.schema
        expected_fields = {field.name for field in expected_schema}
        actual_fields = {field.name for field in table_schema}
        
        if expected_fields != actual_fields:
            missing = expected_fields - actual_fields
            extra = actual_fields - expected_fields
            if missing:
                print(f"✗ Missing fields: {missing}")
            if extra:
                print(f"✗ Extra fields: {extra}")
            return False
        print(f"✓ Schema fields match: {actual_fields}")
        
        # Sample a few records to verify data integrity
        sample_df = table.to_pandas().head(3)
        print(f"✓ Sample records:")
        for idx, row in sample_df.iterrows():
            print(f"  Record {idx}: text='{row['text'][:50]}...', category='{row['category']}', priority={row['priority']}")
        
        print(f"\n✓ Migration verification passed!")
        return True
    except Exception as e:
        print(f"✗ Error verifying migration: {e}")
        return False

def run_migration(db_path: str = "./lancedb", table_name: str = "documents"):
    """Execute the complete migration.
    
    Args:
        db_path: Path to LanceDB database
        table_name: Name of table to migrate
    """
    print("=" * 60)
    print("Starting LanceDB Schema Migration")
    print("=" * 60)
    
    try:
        # Step 1: Connect to database
        print("\n[1/5] Connecting to database...")
        db = connect_database(db_path)
        
        # Step 2: Backup existing data
        print("\n[2/5] Backing up existing data...")
        backup_df = backup_data(db, table_name)
        original_count = len(backup_df)
        
        # Step 3: Define new schema
        print("\n[3/5] Defining new schema...")
        new_schema = get_new_schema()
        print(f"  New schema fields: {[field.name for field in new_schema]}")
        
        # Step 4: Transform data to new schema
        print("\n[4/5] Migrating data to new schema...")
        migrated_df = migrate_data(backup_df, new_schema)
        
        # Step 5: Create new table with migrated data
        print("\n[5/5] Creating new table...")
        create_new_table(db, table_name, migrated_df, new_schema)
        
        # Verify migration
        print("\n" + "=" * 60)
        print("Verifying Migration")
        print("=" * 60)
        success = verify_migration(db, table_name, original_count, new_schema)
        
        if success:
            print("\n" + "=" * 60)
            print("✓ Migration completed successfully!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("✗ Migration verification failed!")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        raise

if __name__ == "__main__":
    # Example: Create sample data for testing
    import numpy as np
    
    # Create a test database with old schema
    db = lancedb.connect("./lancedb")
    
    # Check if table exists, if not create sample data
    if "documents" not in db.table_names():
        print("Creating sample data for migration test...")
        sample_data = pd.DataFrame({
            "text": [
                "This is the first document",
                "This is the second document",
                "This is the third document"
            ],
            "vector": [np.random.rand(384).tolist() for _ in range(3)]
        })
        db.create_table("documents", data=sample_data, mode="overwrite")
        print("Sample data created.\n")
    
    # Run the migration
    run_migration(db_path="./lancedb", table_name="documents")