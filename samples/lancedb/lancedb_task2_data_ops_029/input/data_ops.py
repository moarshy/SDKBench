"""Multi-table schema with relationships."""

from typing import Optional

# TODO: Import lancedb
# TODO: Import LanceModel, Vector from lancedb.pydantic

# TODO: Define multiple related schemas
# class User(LanceModel):
#     user_id: str
#     name: str
#     email: str

# class Document(LanceModel):
#     doc_id: str
#     text: str
#     vector: Vector(384)
#     user_id: str  # Foreign key to User

def create_related_tables(db):
    """Create multiple related tables.

    TODO:
        1. Create users table
        2. Create documents table with user_id reference
        3. Return both tables
    """
    pass

def join_query(db, user_id: str):
    """Query documents with user info.

    TODO:
        1. Get documents for user_id
        2. Get user info
        3. Combine results
    """
    pass

def main():
    # TODO: Create related tables
    # TODO: Insert related data
    # TODO: Query with join
    print("Multi-table complete")

if __name__ == "__main__":
    main()
