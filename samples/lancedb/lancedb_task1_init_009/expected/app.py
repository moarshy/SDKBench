"""LanceDB with predefined schema."""

import lancedb
from lancedb.pydantic import LanceModel, Vector
from typing import Optional

# Define document schema
class Document(LanceModel):
    text: str
    vector: Vector(384)
    category: Optional[str] = None
    timestamp: Optional[str] = None

# Initialize database
db = lancedb.connect("./schema_db")

def create_typed_table(table_name: str):
    """Create table with predefined schema."""
    # Create empty table with schema
    data = [Document(text="init", vector=[0.0] * 384)]
    table = db.create_table(table_name, data, mode="overwrite")
    return table

def main():
    """Schema-based main."""
    table = create_typed_table("documents")
    print(f"Created typed table with schema: {Document.__fields__.keys()}")
    print("Schema-based app ready")

if __name__ == "__main__":
    main()
