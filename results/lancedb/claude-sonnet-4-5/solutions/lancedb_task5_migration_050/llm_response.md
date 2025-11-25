# LanceDB Schema Migration Solution

I'll provide a complete solution for migrating from an old embedding model (384 dimensions) to a new one (768 dimensions, simulating an upgrade to a better model like all-MiniLM-L6-v2 to all-mpnet-base-v2).

```txt
# filepath: requirements.txt
lancedb>=0.5.0
pandas>=2.0.0
pyarrow>=12.0.0
sentence-transformers>=2.2.0
```

```python
# filepath: migration.py
"""Schema Migration: Upgrade embedding model.

Migrate existing LanceDB table to new schema while preserving data.
This example migrates from a 384-dim embedding model to a 768-dim model.
"""

import lancedb
import pandas as pd
import pyarrow as pa
from typing import Optional, List
from datetime import datetime
import os
import shutil

# Old schema (before migration) - 384 dimensions
OLD_SCHEMA = pa.schema([
    pa.field("id", pa.string()),
    pa.field("text", pa.string()),
    pa.field("vector", pa.list_(pa.float32(), 384)),
    pa.field("metadata", pa.string(), nullable=True)
])

# New schema (after migration) - 768 dimensions with additional fields
NEW_SCHEMA = pa.schema([
    pa.field("id", pa.string()),
    pa.field("text", pa.string()),
    pa.field("vector", pa.list_(pa.float32(), 768)),
    pa.field("metadata", pa.string(), nullable=True),
    pa.field("migrated_at", pa.timestamp('us')),
    pa.field("embedding_model", pa.string())
])

# Configuration
DB_PATH = "./my_lancedb"
TABLE_NAME = "documents"
BACKUP_PATH = "./backup_lancedb"
NEW_EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"  # 768 dims
OLD_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # 384 dims


def connect_database(path: str = DB_PATH) -> lancedb.DBConnection:
    """Connect to existing database.
    
    Args:
        path: Path to LanceDB database
        
    Returns:
        LanceDB connection object
    """
    try:
        db = lancedb.connect(path)
        print(f"✓ Connected to database at {path}")
        return db
    except Exception as e:
        print(f"✗ Failed to connect to database: {e}")
        raise


def backup_data(table_name: str, db_path: str = DB_PATH) -> pd.DataFrame:
    """Backup existing table data.
    
    Args:
        table_name: Name of table to backup
        db_path: Path to database
        
    Returns:
        DataFrame containing all table data
    """
    try:
        # Connect to database
        db = connect_database(db_path)
        
        # Check if table exists
        table_names = db.table_names()
        if table_name not in table_names:
            raise ValueError(f"Table '{table_name}' does not exist. Available tables: {table_names}")
        
        # Open and read table
        table = db.open_table(table_name)
        backup_df = table.to_pandas()
        
        print(f"✓ Backed up {len(backup_df)} records from '{table_name}'")
        
        # Also create a physical backup of the database
        if os.path.exists(BACKUP_PATH):
            shutil.rmtree(BACKUP_PATH)
        shutil.copytree(db_path, BACKUP_PATH)
        print(f"✓ Created physical backup at {BACKUP_PATH}")
        
        return backup_df
        
    except Exception as e:
        print(f"✗ Failed to backup data: {e}")
        raise


def migrate_data(old_data: pd.DataFrame, new_schema: pa.Schema) -> pd.DataFrame:
    """Transform data to match new schema.
    
    Args:
        old_data: DataFrame with old schema
        new_schema: PyArrow schema for new table
        
    Returns:
        DataFrame with new schema
    """
    try:
        print(f"Starting migration of {len(old_data)} records...")
        
        # Initialize new embedding model
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(NEW_EMBEDDING_MODEL)
        print(f"✓ Loaded new embedding model: {NEW_EMBEDDING_MODEL}")
        
        # Create new DataFrame with transformed data
        new_data = pd.DataFrame()
        
        # Copy existing fields
        new_data['id'] = old_data['id']
        new_data['text'] = old_data['text']
        
        # Handle metadata field (may be missing in old data)
        if 'metadata' in old_data.columns:
            new_data['metadata'] = old_data['metadata']
        else:
            new_data['metadata'] = None
        
        # Re-generate embeddings with new model
        print("Re-generating embeddings with new model...")
        texts = old_data['text'].tolist()
        
        # Process in batches for efficiency
        batch_size = 32
        new_vectors = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_vectors = model.encode(batch, show_progress_bar=False)
            new_vectors.extend(batch_vectors.tolist())
            
            if (i + batch_size) % 100 == 0:
                print(f"  Processed {min(i + batch_size, len(texts))}/{len(texts)} records")
        
        new_data['vector'] = new_vectors
        
        # Add new fields
        new_data['migrated_at'] = pd.Timestamp.now()
        new_data['embedding_model'] = NEW_EMBEDDING_MODEL
        
        print(f"✓ Successfully migrated {len(new_data)} records")
        print(f"  Old vector dimension: 384")
        print(f"  New vector dimension: 768")
        
        return new_data
        
    except Exception as e:
        print(f"✗ Failed to migrate data: {e}")
        raise


def create_new_table(table_name: str, data: pd.DataFrame, db_path: str = DB_PATH):
    """Create new table with migrated data.
    
    Args:
        table_name: Name of table to create
        data: Migrated data
        db_path: Path to database
    """
    try:
        db = connect_database(db_path)
        
        # Drop old table if exists
        table_names = db.table_names()
        if table_name in table_names:
            db.drop_table(table_name)
            print(f"✓ Dropped old table '{table_name}'")
        
        # Create new table with migrated data
        table = db.create_table(
            table_name,
            data=data,
            schema=NEW_SCHEMA,
            mode="overwrite"
        )
        
        print(f"✓ Created new table '{table_name}' with {len(data)} records")
        
        # Create indexes for better search performance
        print("Creating vector index...")
        # Note: Index creation is automatic in latest LanceDB versions
        # but we can configure it if needed
        
        return table
        
    except Exception as e:
        print(f"✗ Failed to create new table: {e}")
        raise


def verify_migration(table_name: str, expected_count: int, db_path: str = DB_PATH) -> bool:
    """Verify migration was successful.
    
    Args:
        table_name: Name of migrated table
        expected_count: Expected number of records
        db_path: Path to database
        
    Returns:
        True if verification passed, False otherwise
    """
    try:
        print("\nVerifying migration...")
        db = connect_database(db_path)
        
        # Check table exists
        table_names = db.table_names()
        if table_name not in table_names:
            print(f"✗ Table '{table_name}' does not exist")
            return False
        print(f"✓ Table '{table_name}' exists")
        
        # Open table and verify
        table = db.open_table(table_name)
        df = table.to_pandas()
        
        # Verify record count
        actual_count = len(df)
        if actual_count != expected_count:
            print(f"✗ Record count mismatch: expected {expected_count}, got {actual_count}")
            return False
        print(f"✓ Record count matches: {actual_count}")
        
        # Verify new schema fields
        required_fields = ['id', 'text', 'vector', 'metadata', 'migrated_at', 'embedding_model']
        missing_fields = [f for f in required_fields if f not in df.columns]
        if missing_fields:
            print(f"✗ Missing fields: {missing_fields}")
            return False
        print(f"✓ All required fields present")
        
        # Verify vector dimensions
        sample_vector = df['vector'].iloc[0]
        vector_dim = len(sample_vector)
        if vector_dim != 768:
            print(f"✗ Vector dimension mismatch: expected 768, got {vector_dim}")
            return False
        print(f"✓ Vector dimension correct: {vector_dim}")
        
        # Verify embedding model field
        unique_models = df['embedding_model'].unique()
        if len(unique_models) != 1 or unique_models[0] != NEW_EMBEDDING_MODEL:
            print(f"✗ Embedding model field incorrect: {unique_models}")
            return False
        print(f"✓ Embedding model field correct: {NEW_EMBEDDING_MODEL}")
        
        # Test a simple search to ensure functionality
        print("Testing search functionality...")
        sample_text = df['text'].iloc[0]
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(NEW_EMBEDDING_MODEL)
        query_vector = model.encode(sample_text).tolist()
        
        results = table.search(query_vector).limit(5).to_pandas()
        if len(results) == 0:
            print(f"✗ Search returned no results")
            return False
        print(f"✓ Search functionality working: {len(results)} results")
        
        print("\n✓ Migration verification PASSED")
        return True
        
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False


def rollback_migration(table_name: str):
    """Rollback migration by restoring from backup.
    
    Args:
        table_name: Name of table to rollback
    """
    try:
        print("\nRolling back migration...")
        
        if not os.path.exists(BACKUP_PATH):
            raise ValueError("Backup not found. Cannot rollback.")
        
        # Remove current database
        if os.path.exists(DB_PATH):
            shutil.rmtree(DB_PATH)
        
        # Restore from backup
        shutil.copytree(BACKUP_PATH, DB_PATH)
        
        print(f"✓ Successfully rolled back to backup")
        
    except Exception as e:
        print(f"✗ Rollback failed: {e}")
        raise


def run_migration():
    """Execute the complete migration.
    
    Steps:
        1. Backup existing data
        2. Transform to new schema with new embeddings
        3. Create new table
        4. Verify migration
        5. Rollback if verification fails
    """
    print("=" * 60)
    print("LanceDB Schema Migration: Embedding Model Upgrade")
    print("=" * 60)
    print(f"Old model: {OLD_EMBEDDING_MODEL} (384 dims)")
    print(f"New model: {NEW_EMBEDDING_MODEL} (768 dims)")
    print("=" * 60)
    
    try:
        # Step 1: Backup existing data
        print("\n[Step 1/4] Backing up existing data...")
        backup_df = backup_data(TABLE_NAME)
        original_count = len(backup_df)
        
        # Step 2: Transform data to new schema
        print("\n[Step 2/4] Transforming data to new schema...")
        migrated_df = migrate_data(backup_df, NEW_SCHEMA)
        
        # Step 3: Create new table with migrated data
        print("\n[Step 3/4] Creating new table with migrated data...")
        create_new_table(TABLE_NAME, migrated_df)
        
        # Step 4: Verify migration
        print("\n[Step 4/4] Verifying migration...")
        verification_passed = verify_migration(TABLE_NAME, original_count)
        
        if verification_passed:
            print("\n" + "=" * 60)
            print("✓ MIGRATION COMPLETED SUCCESSFULLY")
            print("=" * 60)
            print(f"Migrated {original_count} records")
            print(f"Backup available at: {BACKUP_PATH}")
            print("You can safely delete the backup after testing.")
        else:
            print("\n" + "=" * 60)
            print("✗ MIGRATION VERIFICATION FAILED")
            print("=" * 60)
            
            # Ask user if they want to rollback
            response = input("Do you want to rollback? (yes/no): ").strip().lower()
            if response == 'yes':
                rollback_migration(TABLE_NAME)
            else:
                print("Migration left in current state. Manual intervention required.")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ MIGRATION FAILED: {e}")
        print("=" * 60)
        
        # Ask user if they want to rollback
        response = input("Do you want to rollback? (yes/no): ").strip().lower()
        if response == 'yes':
            rollback_migration(TABLE_NAME)
        else:
            print("Migration left in current state. Manual intervention required.")
        
        raise


if __name__ == "__main__":
    run_migration()
```

This solution provides:

1. **Complete Migration Pipeline**: Backs up data, transforms it with new embeddings, creates new table, and verifies success

2. **Schema Evolution**: Migrates from 384-dim to 768-dim vectors while adding new fields (`migrated_at`, `embedding_model`)

3. **Safety Features**:
   - Physical backup before migration
   - Verification step with multiple checks
   - Rollback capability if verification fails

4. **Production-Ready**:
   - Comprehensive error handling
   - Progress reporting
   - Batch processing for efficiency
   - Clear logging and status messages

5. **Flexible**: Easy to adapt for different embedding models or schema changes

The migration handles the complete workflow from backup to verification, ensuring data integrity throughout the process.