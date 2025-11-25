"""Basic table creation with dict data."""

import pandas as pd

# TODO: Import lancedb

def create_sample_data():
    """Create sample data."""
    return [
        {"text": "Hello world", "category": "greeting"},
        {"text": "Python programming", "category": "tech"},
    ]

def create_table(db, table_name: str, data):
    """Create table with data.

    TODO:
        1. Use db.create_table()
        2. Pass data directly (list of dicts)
        3. Return table
    """
    pass

def main():
    # TODO: Connect to database
    # TODO: Create table
    print("Table created")

if __name__ == "__main__":
    main()
