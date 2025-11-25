"""Async batch embedding with rate limiting."""

import asyncio
from typing import List
import lancedb
from lancedb.pydantic import LanceModel, Vector
from sentence_transformers import SentenceTransformer

# Initialize
db = lancedb.connect("./my_lancedb")
model = SentenceTransformer("all-MiniLM-L6-v2")

class Document(LanceModel):
    text: str
    vector: Vector(384)

RATE_LIMIT = 10
BATCH_SIZE = 50

async def embed_batch_async(texts: List[str], semaphore: asyncio.Semaphore):
    """Embed batch of texts with rate limiting."""
    async with semaphore:
        # Run embedding in executor to not block
        loop = asyncio.get_event_loop()
        vectors = await loop.run_in_executor(None, model.encode, texts)
        return vectors.tolist()

async def ingest_async(table_name: str, texts: List[str]):
    """Async batch ingestion with rate limiting."""
    semaphore = asyncio.Semaphore(RATE_LIMIT)

    # Process batches concurrently
    tasks = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        tasks.append(embed_batch_async(batch, semaphore))

    # Gather all embeddings
    all_vectors = await asyncio.gather(*tasks)

    # Flatten and create documents
    documents = []
    vec_idx = 0
    for batch_vectors in all_vectors:
        for vec in batch_vectors:
            documents.append(Document(text=texts[vec_idx], vector=vec))
            vec_idx += 1

    # Insert into table
    table = db.create_table(table_name, documents, mode="overwrite")
    return table

async def main():
    texts = [f"Document number {i}" for i in range(200)]
    table = await ingest_async("documents", texts)
    print(f"Async batch complete: {len(table.to_pandas())} records")

if __name__ == "__main__":
    asyncio.run(main())
