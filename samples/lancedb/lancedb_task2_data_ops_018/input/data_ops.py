"""Handle null/optional fields in LanceDB."""

from typing import Optional

# TODO: Import lancedb
# TODO: Import LanceModel, Vector from lancedb.pydantic

# TODO: Define schema with optional fields
# class Document(LanceModel):
#     text: str
#     vector: Vector(384)
#     category: Optional[str] = None
#     tags: Optional[str] = None

def insert_with_nulls(table, data):
    """Insert data with optional null fields.

    TODO:
        1. Handle missing fields gracefully
        2. Insert data
    """
    pass

def main():
    # TODO: Create data with some null fields
    # TODO: Insert and verify
    print("Null handling complete")

if __name__ == "__main__":
    main()
