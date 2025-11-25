"""JSON metadata storage pattern."""

import json
from typing import Optional

# TODO: Import lancedb
# TODO: Import LanceModel, Vector from lancedb.pydantic

# TODO: Define schema with JSON metadata field
# class Document(LanceModel):
#     text: str
#     vector: Vector(384)
#     metadata_json: Optional[str] = None  # Store as JSON string

def add_with_json_metadata(table, text: str, vector, metadata: dict):
    """Add document with JSON metadata.

    TODO:
        1. Serialize metadata to JSON string
        2. Create document
        3. Add to table
    """
    pass

def get_metadata(row) -> dict:
    """Parse JSON metadata from row.

    TODO:
        1. Get metadata_json field
        2. Parse JSON
        3. Return dict
    """
    pass

def main():
    # TODO: Add documents with nested metadata
    # TODO: Query and parse metadata
    print("JSON metadata complete")

if __name__ == "__main__":
    main()
