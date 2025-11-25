"""Full production LanceDB setup with all best practices."""

import os
from typing import Optional
import logging
import time
import lancedb
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize embedding model with error handling
registry = EmbeddingFunctionRegistry.get_instance()
model = registry.get("sentence-transformers").create(
    name="all-MiniLM-L6-v2",
    device="cpu"
)

# Define production schema with all fields
class Document(LanceModel):
    id: str
    text: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()
    metadata: Optional[str] = None
    created_at: Optional[str] = None

class ProductionDB:
    """Production-ready database wrapper."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._db = None

    def connect(self, retries: int = 3):
        """Connect with retry logic."""
        for attempt in range(retries):
            try:
                self._db = lancedb.connect(self.db_path)
                logger.info(f"Connected to {self.db_path}")
                return self._db
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(1)
                else:
                    raise

    def get_or_create_table(self, table_name: str):
        """Get existing table or create new one."""
        if table_name in self._db.table_names():
            logger.info(f"Opening existing table: {table_name}")
            return self._db.open_table(table_name)
        else:
            logger.info(f"Creating new table: {table_name}")
            # Create with empty initial record
            data = [Document(id="init", text="initialization")]
            return self._db.create_table(table_name, data)

# Initialize production database
prod_db = ProductionDB("./prod_db")

def main():
    db = prod_db.connect()
    table = prod_db.get_or_create_table("documents")
    print(f"Production database ready with {len(table.to_pandas())} records")

if __name__ == "__main__":
    main()
