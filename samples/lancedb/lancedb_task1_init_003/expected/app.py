"""Streamlit app with cached LanceDB connection."""

import streamlit as st
import lancedb

@st.cache_resource
def get_database():
    """Get cached database connection."""
    return lancedb.connect("./streamlit_db")

# Initialize cached database
db = get_database()

def main():
    st.title("Vector Search App")
    tables = db.table_names()
    st.success(f"Connected to LanceDB with {len(tables)} tables")
    st.write("App ready")

if __name__ == "__main__":
    main()
