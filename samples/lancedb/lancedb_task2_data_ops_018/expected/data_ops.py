"""Data management for vector database."""

import pandas as pd
import numpy as np
import lancedb
from lancedb.pydantic import LanceModel, Vector

# Connect to database
db = lancedb.connect("./my_lancedb")

class Document(LanceModel):
    """Document schema with vector."""
    id: int
    text: str
    category: str
    vector: Vector(384)  # 384-dimensional vector

def create_sample_data():
    """Create sample data for testing."""
    data = [
        {"id": 1, "text": "Hello world", "category": "greeting"},
        {"id": 2, "text": "Python programming", "category": "tech"},
        {"id": 3, "text": "Machine learning", "category": "tech"}
    ]
    return pd.DataFrame(data)

def store_data(df):
    """Store data in vector database."""
    # Add random vectors for demo (in production, use real embeddings)
    df["vector"] = [np.random.randn(384).tolist() for _ in range(len(df))]

    # Create or open table
    table = db.create_table(
        "vectors",
        data=df,
        mode="overwrite"
    )

    return table

def main():
    """Main function."""
    df = create_sample_data()
    table = store_data(df)
    print(f"Stored {len(df)} records in '{table.name}' table")

if __name__ == "__main__":
    main()
