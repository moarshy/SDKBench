"""Basic table creation with dict data."""

import lancedb

# Connect to database
db = lancedb.connect("./my_lancedb")

def create_sample_data():
    """Create sample data."""
    return [
        {"text": "Hello world", "category": "greeting", "vector": [0.1] * 384},
        {"text": "Python programming", "category": "tech", "vector": [0.2] * 384},
    ]

def create_table(db, table_name: str, data):
    """Create table with data."""
    table = db.create_table(table_name, data, mode="overwrite")
    return table

def main():
    data = create_sample_data()
    table = create_table(db, "documents", data)
    print(f"Table created with {len(table.to_pandas())} records")

if __name__ == "__main__":
    main()
