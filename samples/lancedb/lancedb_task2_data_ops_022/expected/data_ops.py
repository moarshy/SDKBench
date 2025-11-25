"""Batch ingestion with progress tracking."""

import lancedb
from lancedb.pydantic import LanceModel, Vector
import numpy as np
from tqdm import tqdm

# Connect to database
db = lancedb.connect("./my_lancedb")

class Document(LanceModel):
    id: int
    text: str
    vector: Vector(384)

BATCH_SIZE = 100

def batch_ingest(table_name: str, documents: list, batch_size: int = BATCH_SIZE):
    """Ingest documents in batches with progress."""
    # First batch creates the table
    first_batch = documents[:batch_size]
    table = db.create_table(table_name, first_batch, mode="overwrite")

    # Add remaining batches with progress bar
    remaining = documents[batch_size:]
    for i in tqdm(range(0, len(remaining), batch_size), desc="Ingesting"):
        batch = remaining[i:i + batch_size]
        table.add(batch)

    return table

def main():
    # Create large dataset
    documents = [
        Document(id=i, text=f"Document {i}", vector=np.random.randn(384).tolist())
        for i in range(1000)
    ]
    table = batch_ingest("documents", documents)
    print(f"Batch ingestion complete: {len(table.to_pandas())} records")

if __name__ == "__main__":
    main()
