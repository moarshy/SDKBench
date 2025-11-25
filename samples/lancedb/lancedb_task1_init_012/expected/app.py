"""LanceDB with IVF-PQ index creation."""

import lancedb
from lancedb.pydantic import LanceModel, Vector
import numpy as np

class Document(LanceModel):
    text: str
    vector: Vector(384)

# Initialize database
db = lancedb.connect("./indexed_db")

def create_indexed_table(table_name: str, data):
    """Create table and build IVF-PQ index."""
    # Create table with data
    table = db.create_table(table_name, data, mode="overwrite")

    # Create IVF-PQ index for faster search
    table.create_index(
        metric="cosine",
        num_partitions=4,
        num_sub_vectors=32
    )

    return table

def main():
    # Create sample data
    data = [
        Document(text=f"Document {i}", vector=np.random.randn(384).tolist())
        for i in range(100)
    ]

    table = create_indexed_table("indexed_docs", data)
    print(f"Created indexed table with {len(table.to_pandas())} records")
    print("Indexed database ready")

if __name__ == "__main__":
    main()
