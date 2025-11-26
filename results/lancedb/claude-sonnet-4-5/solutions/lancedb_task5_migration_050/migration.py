# filepath: migration.py
"""Schema Migration: Upgrade embedding model.

Migrate existing LanceDB table to new schema while preserving data.
This migration upgrades from a 384-dim embedding model to a 768-dim model.
"""

import lancedb
import pandas as pd
import pyarrow as pa
from typing import Optional, List
from datetime import datetime
import os
import shutil

# Old schema (before migration) - 384 dimensions (e.g., all-MiniLM-L6-v2)
OLD_VECTOR_DIM = 384

# New schema (after migration) - 768 dimensions (e.g., all-mpnet-base-v2)
NEW_VECTOR_DIM = 768

def get_new_schema():
    """Define new schema with upgraded embedding dimensions.
    
    Returns:
        pyarrow.Schema: New table schema with 768-dim vectors
    """
    return pa.schema([
        pa.field("id", pa.string()),
        pa.field("text", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), NEW_VECTOR_DIM)),
        pa.field("metadata", pa.string(), nullable=True),
        pa.field("created_at", pa.timestamp('ms')),
        pa.field("migrated_at", pa.timestamp('ms'), nullable=True)
    ])


def connect_database(db_path: str = "./my_lancedb"):
    """Connect to existing database.
    
    Args:
        db_path: Path to LanceDB database
        
    Returns:
        lancedb.DBConnection: Database connection
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}")
    
    db = lancedb.connect(db_path)
    print(f"✓ Connected to database at {db_path}")
    return db


def backup_data(db, table_name: str, backup_path: Optional[str] = None):
    """Backup existing table data.
    
    Args:
        db: LanceDB connection
        table_name: Name of table to backup
        backup_path: Optional custom backup path
        
    Returns:
        pd.DataFrame: Backup data as DataFrame
    """
    try:
        # Open existing table
        table = db.open_table(table_name)
        
        # Read all data to DataFrame
        backup_df = table.to_pandas()
        
        # Save backup to disk
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"./backups/{table_name}_backup_{timestamp}.parquet"
        
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        backup_df.to_parquet(backup_path)
        
        print(f"✓ Backed up {len(backup_df)} records to {backup_path}")
        return backup_df
        
    except Exception as e:
        print(f"✗ Error backing up data: {e}")
        raise


def re_embed_text(texts: List[str], model_name: str = "sentence-transformers/all-mpnet-base-v2"):
    """Re-embed texts using new embedding model.
    
    Args:
        texts: List of text strings to embed
        model_name: Name of the new embedding model
        
    Returns:
        List of new embedding vectors
    """
    try:
        from sentence_transformers import SentenceTransformer
        
        print(f"Loading embedding model: {model_name}")
        model = SentenceTransformer(model_name)
        
        print(f"Re-embedding {len(texts)} texts...")
        embeddings = model.encode(texts, show_progress_bar=True)
        
        return embeddings.tolist()
        
    except ImportError:
        print("✗ sentence-transformers not installed. Install with: pip install sentence-transformers")
        raise
    except Exception as e:
        print(f"✗ Error re-embedding texts: {e}")
        raise


def migrate_data(old_data: pd.DataFrame, new_embedding_model: str = "sentence-transformers/all-mpnet-base-v2"):
    """Transform data to match new schema.
    
    Args:
        old_data: DataFrame with old schema
        new_embedding_model: Name of new embedding model
        
    Returns:
        pd.DataFrame: Transformed data with new schema
    """
    print("Starting data migration...")
    
    # Create copy to avoid modifying original
    migrated_df = old_data.copy()
    
    # Re-embed all texts with new model
    texts = migrated_df['text'].tolist()
    new_vectors = re_embed_text(texts, new_embedding_model)
    
    # Update vectors
    migrated_df['vector'] = new_vectors
    
    # Add migration timestamp
    migrated_df['migrated_at'] = pd.Timestamp.now()
    
    # Handle missing fields with defaults
    if 'id' not in migrated_df.columns:
        migrated_df['id'] = [f"doc_{i}" for i in range(len(migrated_df))]
    
    if 'metadata' not in migrated_df.columns:
        migrated_df['metadata'] = None
    
    if 'created_at' not in migrated_df.columns:
        migrated_df['created_at'] = pd.Timestamp.now()
    
    # Ensure correct column order
    column_order = ['id', 'text', 'vector', 'metadata', 'created_at', 'migrated_at']
    migrated_df = migrated_df[column_order]
    
    print(f"✓ Migrated {len(migrated_df)} records to new schema")
    return migrated_df


def create_new_table(db, table_name: str, data: pd.DataFrame, mode: str = "overwrite"):
    """Create new table with migrated data.
    
    Args:
        db: LanceDB connection
        table_name: Name of table to create
        data: Migrated data
        mode: Creation mode ('overwrite' or 'create')
    """
    try:
        # Drop old table if exists and mode is overwrite
        if mode == "overwrite":
            try:
                db.drop_table(table_name)
                print(f"✓ Dropped old table: {table_name}")
            except Exception:
                print(f"Table {table_name} doesn't exist, creating new one")
        
        # Create table with new schema
        schema = get_new_schema()
        table = db.create_table(
            table_name,
            data=data,
            schema=schema,
            mode="overwrite" if mode == "overwrite" else "create"
        )
        
        print(f"✓ Created new table '{table_name}' with {len(data)} records")
        
        # Create vector index for efficient search
        print("Creating vector index...")
        table.create_index(metric="cosine", num_partitions=256, num_sub_vectors=96)
        print("✓ Vector index created")
        
        return table
        
    except Exception as e:
        print(f"✗ Error creating new table: {e}")
        raise


def verify_migration(db, table_name: str, expected_count: int, expected_vector_dim: int = NEW_VECTOR_DIM):
    """Verify migration was successful.
    
    Args:
        db: LanceDB connection
        table_name: Name of migrated table
        expected_count: Expected number of records
        expected_vector_dim: Expected vector dimension
        
    Returns:
        bool: True if verification passed
    """
    print("\nVerifying migration...")
    
    try:
        # Check table exists
        table_names = db.table_names()
        if table_name not in table_names:
            print(f"✗ Table '{table_name}' not found")
            return False
        print(f"✓ Table '{table_name}' exists")
        
        # Open table
        table = db.open_table(table_name)
        
        # Verify record count
        actual_count = table.count_rows()
        if actual_count != expected_count:
            print(f"✗ Record count mismatch: expected {expected_count}, got {actual_count}")
            return False
        print(f"✓ Record count matches: {actual_count}")
        
        # Verify schema and vector dimensions
        sample = table.to_pandas().head(1)
        if len(sample) > 0:
            vector_dim = len(sample['vector'].iloc[0])
            if vector_dim != expected_vector_dim:
                print(f"✗ Vector dimension mismatch: expected {expected_vector_dim}, got {vector_dim}")
                return False
            print(f"✓ Vector dimension correct: {vector_dim}")
            
            # Verify new fields exist
            required_fields = ['id', 'text', 'vector', 'migrated_at']
            for field in required_fields:
                if field not in sample.columns:
                    print(f"✗ Missing required field: {field}")
                    return False
            print(f"✓ All required fields present")
        
        print("\n✓ Migration verification passed!")
        return True
        
    except Exception as e:
        print(f"✗ Verification error: {e}")
        return False


def run_migration(
    db_path: str = "./my_lancedb",
    table_name: str = "documents",
    new_embedding_model: str = "sentence-transformers/all-mpnet-base-v2",
    backup_enabled: bool = True
):
    """Execute the complete migration.
    
    Args:
        db_path: Path to LanceDB database
        table_name: Name of table to migrate
        new_embedding_model: Name of new embedding model
        backup_enabled: Whether to create backup
    """
    print("=" * 60)
    print("LanceDB Schema Migration: Embedding Model Upgrade")
    print(f"Old dimension: {OLD_VECTOR_DIM} -> New dimension: {NEW_VECTOR_DIM}")
    print("=" * 60)
    
    try:
        # Step 1: Connect to database
        db = connect_database(db_path)
        
        # Step 2: Backup existing data
        if backup_enabled:
            backup_df = backup_data(db, table_name)
        else:
            table = db.open_table(table_name)
            backup_df = table.to_pandas()
            print(f"✓ Loaded {len(backup_df)} records (backup disabled)")
        
        expected_count = len(backup_df)
        
        # Step 3: Transform to new schema
        migrated_data = migrate_data(backup_df, new_embedding_model)
        
        # Step 4: Create new table
        create_new_table(db, table_name, migrated_data, mode="overwrite")
        
        # Step 5: Verify migration
        success = verify_migration(db, table_name, expected_count)
        
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
        print("\nTo restore from backup, use the backup file in ./backups/")
        raise


if __name__ == "__main__":
    # Example usage with custom parameters
    run_migration(
        db_path="./my_lancedb",
        table_name="documents",
        new_embedding_model="sentence-transformers/all-mpnet-base-v2",
        backup_enabled=True
    )