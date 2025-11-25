"""Configurable vector database application."""

import os
import lancedb

# Read configuration from environment
DEFAULT_PATH = "./default_lancedb"

def get_db_path():
    """Get database path from configuration."""
    return os.environ.get("LANCEDB_PATH", DEFAULT_PATH)

def initialize_database():
    """Initialize database with configuration."""
    path = get_db_path()
    return lancedb.connect(path)

# Initialize with config
db = initialize_database()

def main():
    """Main entry point."""
    path = get_db_path()
    tables = db.table_names()
    print(f"Connected to {path} with {len(tables)} tables")
    print("Configurable app started")

if __name__ == "__main__":
    main()
