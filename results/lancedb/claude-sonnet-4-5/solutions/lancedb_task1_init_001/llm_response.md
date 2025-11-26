```txt
# filepath: requirements.txt
pandas>=2.0.0
numpy>=1.24.0
lancedb>=0.5.0
```

```python
# filepath: app.py
"""Basic LanceDB connection pattern."""

import lancedb
import os
from pathlib import Path


def get_database(db_path: str = "./my_lancedb"):
    """Get database connection.
    
    Args:
        db_path: Path to the LanceDB database directory
        
    Returns:
        lancedb.DBConnection: Connected database instance
        
    Raises:
        Exception: If connection fails
    """
    try:
        # Create parent directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Connect to LanceDB (creates database if it doesn't exist)
        db = lancedb.connect(db_path)
        
        print(f"Successfully connected to LanceDB at: {db_path}")
        return db
    except Exception as e:
        print(f"Error connecting to LanceDB: {e}")
        raise


def main():
    """Main entry point."""
    try:
        # Initialize database connection
        db = get_database()
        
        # List existing tables in the database
        table_names = db.table_names()
        
        if table_names:
            print(f"\nExisting tables ({len(table_names)}):")
            for table_name in table_names:
                print(f"  - {table_name}")
        else:
            print("\nNo tables found in database (this is normal for a new database)")
        
        print("\nApplication started successfully")
        
    except Exception as e:
        print(f"Application failed to start: {e}")
        raise


if __name__ == "__main__":
    main()
```