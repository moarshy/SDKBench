"""Initialize for background jobs - job processor."""

import lancedb

def initialize():
    """Initialize database connection."""
    return lancedb.connect("./worker_data/lancedb")

def verify_connection(db):
    """Verify database is accessible."""
    tables = db.table_names()
    return len(tables) >= 0

# Initialize database
db = initialize()

def main():
    """Main entry point."""
    if verify_connection(db):
        print(f"Connected to {db_path}")
    print("job processor ready")

if __name__ == "__main__":
    main()
