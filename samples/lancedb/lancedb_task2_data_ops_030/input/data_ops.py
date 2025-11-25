"""Full data validation pipeline."""

from typing import Optional, List
from pydantic import field_validator

# TODO: Import lancedb
# TODO: Import LanceModel, Vector from lancedb.pydantic

# TODO: Define schema with validators
# class Document(LanceModel):
#     text: str
#     vector: Vector(384)
#     category: str
#
#     @field_validator("text")
#     @classmethod
#     def text_not_empty(cls, v):
#         if not v or not v.strip():
#             raise ValueError("text cannot be empty")
#         return v.strip()
#
#     @field_validator("category")
#     @classmethod
#     def valid_category(cls, v):
#         allowed = ["tech", "science", "business"]
#         if v not in allowed:
#             raise ValueError(f"category must be one of {allowed}")
#         return v

def validate_and_insert(table, documents: List[dict]):
    """Validate documents before insertion.

    TODO:
        1. Validate each document against schema
        2. Collect validation errors
        3. Insert valid documents
        4. Return errors
    """
    pass

def main():
    # TODO: Create docs with some invalid data
    # TODO: Validate and insert
    # TODO: Report errors
    print("Validation complete")

if __name__ == "__main__":
    main()
