"""json_metadata data operations."""

import lancedb
from lancedb.pydantic import LanceModel, Vector
import numpy as np

db = lancedb.connect("./my_lancedb")

class Document(LanceModel):
    text: str
    vector: Vector(384)

def create_data():
    """Create sample data."""
    return [
        Document(text=f"Document {i}", vector=np.random.randn(384).tolist())
        for i in range(10)
    ]

def store_data(data):
    """Store data in database."""
    table = db.create_table("documents", data, mode="overwrite")
    return table

def main():
    data = create_data()
    table = store_data(data)
    print(f"Data operations complete: {len(table.to_pandas())} records")

if __name__ == "__main__":
    main()
