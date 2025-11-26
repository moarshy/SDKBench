"""Schema Migration: Upgrade embedding model.

Migrate existing LanceDB table to new schema while preserving data.
"""

import lancedb
import pandas as pd
from lancedb.pydantic import LanceModel, Vector
from typing import List, Dict, Any

# New schema (after migration) - content renamed from text, vector preserved
class NewDocument(LanceModel):
    content: str  # Renamed from 'text'
    vector: List[float]  # Preserved from original

# Database connection
db = lancedb.connect("./migration_db")

def connect_database():
    """Connect to existing database."""
    return db

def backup_data(table_name: str) -> pd.DataFrame:
    """Backup existing table data.

    Args:
        table_name: Name of table to backup

    Returns:
        DataFrame with all table data
    """
    try:
        table = db.open_table(table_name)
        backup = table.to_pandas()
        print(f"Backed up {len(backup)} records from {table_name}")
        return backup
    except Exception as e:
        print(f"No existing table to backup: {e}")
        return pd.DataFrame()

def migrate_data(old_data: pd.DataFrame) -> List[Dict[str, Any]]:
    """Transform data to match new schema.

    Args:
        old_data: DataFrame with old schema data

    Returns:
        List of records matching new schema
    """
    transformed = []

    for _, record in old_data.iterrows():
        # Rename text field to content
        transformed.append({
            "content": record["text"],
            "vector": record["vector"]
        })

    print(f"Transformed {len(transformed)} records")
    return transformed

def create_new_table(table_name: str, data: List[Dict[str, Any]]):
    """Create new table with migrated data.

    Args:
        table_name: Name for new table
        data: Migrated data records
    """
    # Convert to LanceModel instances
    documents = [NewDocument(**d) for d in data]

    # Create table (overwrite if exists)
    table = db.create_table(table_name, documents, mode="overwrite")
    print(f"Created table {table_name} with {len(documents)} records")
    return table

def verify_migration(table_name: str, expected_count: int) -> bool:
    """Verify migration was successful.

    Args:
        table_name: Name of migrated table
        expected_count: Expected number of records

    Returns:
        True if verification passes
    """
    table = db.open_table(table_name)
    actual_count = len(table.to_pandas())

    if actual_count != expected_count:
        print(f"Count mismatch: expected {expected_count}, got {actual_count}")
        return False

    print(f"Migration verified: {actual_count} records")
    return True

def run_migration():
    """Execute the complete migration."""
    table_name = "documents"

    print("Starting migration...")

    # Step 1: Backup existing data
    old_data = backup_data(table_name)

    if old_data.empty:
        # Create sample data for demonstration
        print("Creating sample data for migration demo...")
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")

        sample_texts = ["Sample document 1", "Sample document 2", "Sample document 3"]
        embeddings = model.encode(sample_texts).tolist()

        old_data = pd.DataFrame({
            "text": sample_texts,
            "vector": embeddings
        })

    expected_count = len(old_data)

    # Step 2: Transform to new schema
    migrated_data = migrate_data(old_data)

    # Step 3: Create new table
    create_new_table(table_name, migrated_data)

    # Step 4: Verify migration
    success = verify_migration(table_name, expected_count)

    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed verification!")

    return success

if __name__ == "__main__":
    run_migration()
