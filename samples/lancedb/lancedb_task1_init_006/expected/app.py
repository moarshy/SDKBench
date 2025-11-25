"""In-memory LanceDB for testing."""

import lancedb

def create_test_db():
    """Create in-memory database for testing."""
    return lancedb.connect(":memory:")

def setup_test_data(db):
    """Set up test data in database."""
    # Create a simple test table
    data = [{"text": "test", "vector": [0.1] * 384}]
    db.create_table("test_table", data, mode="overwrite")

# Initialize test database
db = create_test_db()

def main():
    """Test main."""
    setup_test_data(db)
    tables = db.table_names()
    print(f"Test database ready with {len(tables)} tables")

if __name__ == "__main__":
    main()
