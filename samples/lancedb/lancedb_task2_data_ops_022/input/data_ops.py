"""Batch ingestion with progress tracking."""

from tqdm import tqdm

# TODO: Import lancedb

BATCH_SIZE = 100

def batch_ingest(db, table_name: str, documents: list, batch_size: int = BATCH_SIZE):
    """Ingest documents in batches with progress.

    TODO:
        1. Split documents into batches
        2. Create table with first batch
        3. Add remaining batches with progress bar
    """
    pass

def main():
    # TODO: Create large dataset
    # TODO: Batch ingest
    print("Batch ingestion complete")

if __name__ == "__main__":
    main()
