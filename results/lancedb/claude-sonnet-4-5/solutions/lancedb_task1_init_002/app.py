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
    """Verify database works by creating a test table.
    
    Args:
        db: LanceDB connection
        
    Returns:
        bool: True if verification successful
    """
    try:
        # Create sample data with vectors
        data = pd.DataFrame({
            "id": [1, 2, 3],
            "text": ["hello", "world", "test"],
            "vector": [
                np.array([1.0, 0.0, 0.0]),
                np.array([0.0, 1.0, 0.0]),
                np.array([0.0, 0.0, 1.0])
            ]
        })
        
        # Create a test table
        table = db.create_table("test_table", data, mode="overwrite")
        
        # Verify we can query the table
        result = table.search([1.0, 0.0, 0.0]).limit(1).to_pandas()
        
        if len(result) > 0:
            print(f"✓ Database verification successful")
            print(f"✓ Created test table with {len(data)} rows")
            print(f"✓ Search query returned {len(result)} result(s)")
            return True
        else:
            print("✗ Database verification failed: no results returned")
            return False
            
    except Exception as e:
        print(f"✗ Database verification failed: {e}")
        return False


def main():
    """Test database setup."""
    try:
        # Create in-memory database
        print("Creating in-memory LanceDB...")
        db = create_test_db()
        print(f"✓ Database created: {db}")
        
        # Verify it works
        print("\nVerifying database functionality...")
        if verify_database(db):
            print("\n✓ Test database ready")
        else:
            print("\n✗ Test database verification failed")
            
    except Exception as e:
        print(f"\n✗ Error during setup: {e}")
        raise


if __name__ == "__main__":
    main()