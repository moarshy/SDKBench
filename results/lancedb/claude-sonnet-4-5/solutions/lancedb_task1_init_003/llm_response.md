I'll help you set up a Streamlit app with a cached LanceDB connection. Here's the complete solution:

```txt
# filepath: requirements.txt
pandas>=2.0.0
numpy>=1.24.0
streamlit>=1.28.0
lancedb>=0.5.0
```

```python
# filepath: app.py
"""Streamlit app with cached LanceDB connection."""

import streamlit as st
import lancedb
import os

# Use @st.cache_resource decorator for database connection
@st.cache_resource
def get_database():
    """Get cached database connection.
    
    Creates or opens a LanceDB database in the ./lancedb directory.
    The connection is cached across reruns for better performance.
    
    Returns:
        lancedb.DBConnection: Cached database connection
    """
    try:
        # Define database path
        db_path = "./lancedb"
        
        # Create directory if it doesn't exist
        os.makedirs(db_path, exist_ok=True)
        
        # Connect to LanceDB (creates database if it doesn't exist)
        db = lancedb.connect(db_path)
        
        return db
    except Exception as e:
        st.error(f"Failed to connect to LanceDB: {str(e)}")
        raise

def main():
    st.title("Vector Search App")
    
    try:
        # Get cached database connection
        db = get_database()
        
        # Display connection status
        st.success("✅ Connected to LanceDB")
        
        # Get and display table count
        table_names = db.table_names()
        table_count = len(table_names)
        
        st.metric("Number of Tables", table_count)
        
        # Display table names if any exist
        if table_count > 0:
            st.subheader("Available Tables")
            for table_name in table_names:
                st.write(f"- {table_name}")
        else:
            st.info("No tables found. Create your first table to get started!")
        
        st.write("App ready")
        
    except Exception as e:
        st.error(f"Error initializing app: {str(e)}")

if __name__ == "__main__":
    main()
```

## Key Implementation Details:

1. **LanceDB Import**: Added `lancedb` to imports and requirements.txt (version 0.5.0)

2. **Cached Connection**: 
   - Used `@st.cache_resource` decorator to cache the database connection
   - This ensures the connection is created once and reused across Streamlit reruns
   - Improves performance by avoiding repeated connection overhead

3. **Connection Path**:
   - Database stored in `./lancedb` directory
   - Directory is created automatically if it doesn't exist
   - Uses relative path for portability

4. **Error Handling**:
   - Try-except blocks for robust error handling
   - User-friendly error messages displayed in Streamlit UI
   - Graceful degradation if connection fails

5. **Connection Verification**:
   - Displays success message when connected
   - Shows table count using `db.table_names()`
   - Lists available tables if any exist
   - Provides helpful message if no tables are found

The app is now ready to use with LanceDB. The cached connection will persist across Streamlit reruns, making the app more efficient. You can extend this foundation by adding table creation, vector search, and other LanceDB features.