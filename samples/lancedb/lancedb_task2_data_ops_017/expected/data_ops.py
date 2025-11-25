"""Create table with LanceModel schema."""

import lancedb
from lancedb.pydantic import LanceModel, Vector
import numpy as np

# Connect to database
db = lancedb.connect("./my_lancedb")

class Document(LanceModel):
    text: str
    vector: Vector(384)
    category: str

def create_table_with_schema(db, table_name: str, data):
    """Create table with LanceModel schema."""
    table = db.create_table(table_name, data, mode="overwrite")
    return table

def main():
    data = [
        Document(text="Hello", vector=np.random.randn(384).tolist(), category="greeting"),
        Document(text="Python", vector=np.random.randn(384).tolist(), category="tech"),
    ]
    table = create_table_with_schema(db, "documents", data)
    print(f"Schema-based table created with {len(table.to_pandas())} records")

if __name__ == "__main__":
    main()
