"""Streamlit app with cached LanceDB connection."""

import streamlit as st

# TODO: Import lancedb

# TODO: Use @st.cache_resource decorator for database connection

def get_database():
    """Get cached database connection.

    TODO:
        1. Apply @st.cache_resource decorator
        2. Connect to LanceDB
        3. Return cached connection
    """
    pass

def main():
    st.title("Vector Search App")
    # TODO: Get cached database
    # TODO: Display table count
    st.write("App ready")

if __name__ == "__main__":
    main()
