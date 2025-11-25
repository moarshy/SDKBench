# filepath: app.py
"""In-memory LanceDB for testing."""

import lancedb
import pandas as pd
import numpy as np


def create_test_db():
    """Create in-memory database for testing.
    
    Returns:
        lancedb.DBConnection: In-memory database connection
    """
    try:
        # Use lancedb.connect(":memory:") for ephemeral storage
        db = lancedb.connect(":memory:")
        return db
    except Exception as e:
        print(f"Error creating in-memory database: {e}")
        raise


def verify_database(db):
    """Verify database is working by creating a test table.
    
    Args:
        db: LanceDB connection
        
    Returns:
        bool: True if verification successful
    """
    try:
        # Create sample data for testing
        data = pd.DataFrame({
            "id": [1, 2, 3],
            "vector": [
                np.array([1.0, 2.0, 3.0]),
                np.array([4.0, 5.0, 6.0]),
                np.array([7.0, 8.0, 9.0])
            ],
            "text": ["first", "second", "third"]
        })
        
        # Create a test table
        table = db.create_table("test_table", data, mode="overwrite")
        
        # Verify table was created
        table_names = db.table_names()
        assert "test_table" in table_names, "Test table not found in database"
        
        # Verify data can be retrieved
        result = table.to_pandas()
        assert len(result) == 3, f"Expected 3 rows, got {len(result)}"
        
        print(f"✓ Database verified successfully")
        print(f"✓ Tables in database: {table_names}")
        print(f"✓ Test table contains {len(result)} rows")
        
        return True
    except Exception as e:
        print(f"✗ Database verification failed: {e}")
        return False


def main():
    """Test database setup."""
    try:
        # Create in-memory database
        print("Creating in-memory LanceDB...")
        db = create_test_db()
        print(f"✓ In-memory database created: {db}")
        
        # Verify it works
        print("\nVerifying database functionality...")
        if verify_database(db):
            print("\n✓ Test database ready and fully functional!")
        else:
            print("\n✗ Database verification failed")
            return 1
            
        return 0
        
    except Exception as e:
        print(f"\n✗ Error during setup: {e}")
        return 1


if __name__ == "__main__":
    exit(main())