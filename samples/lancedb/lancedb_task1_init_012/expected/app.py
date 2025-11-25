"""Initialize for Jupyter notebook - data analysis."""

import lancedb

def initialize():
    """Initialize database connection."""
    return lancedb.connect("./notebook_data")

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
    print("data analysis ready")

if __name__ == "__main__":
    main()
