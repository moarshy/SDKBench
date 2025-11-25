"""Basic LanceDB connection pattern."""

import lancedb

# Initialize LanceDB connection
db = lancedb.connect("./my_lancedb")

def get_database():
    """Get database connection."""
    return db

def main():
    """Main entry point."""
    tables = db.table_names()
    print(f"Connected to LanceDB at ./my_lancedb")
    print(f"Available tables: {tables}")
    print("Application started")

if __name__ == "__main__":
    main()
