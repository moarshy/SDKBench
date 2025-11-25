# filepath: app.py
"""Streamlit app with cached LanceDB connection."""

import streamlit as st
import lancedb
import os

# Use @st.cache_resource decorator for database connection
@st.cache_resource
def get_database():
    """Get cached database connection.
    
    Creates a persistent LanceDB connection that is cached across reruns.
    The database is stored in a local directory called 'lancedb_data'.
    
    Returns:
        lancedb.DBConnection: Cached database connection
    """
    try:
        # Define database path
        db_path = "./lancedb_data"
        
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
        
        # Display database path
        with st.expander("Database Information"):
            st.write(f"**Database Path:** `./lancedb_data`")
            st.write(f"**Connection Type:** Cached (persistent across reruns)")
        
        st.write("App ready")
        
    except Exception as e:
        st.error(f"Error initializing app: {str(e)}")

if __name__ == "__main__":
    main()