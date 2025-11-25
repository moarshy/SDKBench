"""Vector data application - simple app."""

import lancedb

# Initialize LanceDB connection
db = lancedb.connect("./my_lancedb")

def main():
    """Main entry point."""
    # List available tables
    tables = db.table_names()
    print(f"Connected to LanceDB at ./my_lancedb")
    print(f"Available tables: {tables}")

    print("Application started")

if __name__ == "__main__":
    main()
