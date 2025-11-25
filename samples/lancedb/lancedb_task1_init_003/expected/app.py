"""Streamlit dashboard with vector search."""

import streamlit as st
import lancedb

@st.cache_resource
def get_database():
    """Get cached database connection."""
    return lancedb.connect("./streamlit_data/vectors")

# Initialize cached database
db = get_database()

def main():
    """Streamlit app main."""
    st.set_page_config(page_title="Vector Search", layout="wide")
    st.title("Vector Search Dashboard")

    # Display connection status
    tables = db.table_names()
    st.success(f"Connected to LanceDB with {len(tables)} tables")

    print("Streamlit app ready")

if __name__ == "__main__":
    main()
