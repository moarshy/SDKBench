# filepath: app.py
"""Full production LanceDB setup with all best practices."""

import os
from typing import Optional
import logging
import time
from datetime import datetime

import lancedb
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize embedding model with error handling and retry
def get_embedding_model(retries: int = 3):
    """Get embedding model with retry logic."""
    registry = EmbeddingFunctionRegistry.get_instance()
    
    for attempt in range(retries):
        try:
            model = registry.get("sentence-transformers").create(
                name="all-MiniLM-L6-v2",
                device="cpu"
            )
            logger.info("Embedding model initialized successfully")
            return model
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{retries} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error("Failed to initialize embedding model")
                raise

model = get_embedding_model()

# Define production schema with all fields
class Document(LanceModel):
    """Document schema with vector embeddings."""
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
        """Connect with retry logic.

        Args:
            retries: Number of connection attempts

        Raises:
            Exception: If connection fails after all retries
        """
        for attempt in range(retries):
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)
                
                # Connect to database
                self._db = lancedb.connect(self.db_path)
                logger.info(f"Connected to LanceDB at {self.db_path}")
                
                # Verify connection by listing tables
                tables = self._db.table_names()
                logger.info(f"Database has {len(tables)} existing tables: {tables}")
                return self._db
                
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1}/{retries} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to connect to database after {retries} attempts")
                    raise

    def get_or_create_table(self, table_name: str):
        """Get existing table or create new one.

        Args:
            table_name: Name of the table

        Returns:
            LanceDB table instance

        Raises:
            ValueError: If database not connected
        """
        if self._db is None:
            raise ValueError("Database not connected. Call connect() first.")

        try:
            # Check if table exists
            if table_name in self._db.table_names():
                logger.info(f"Opening existing table: {table_name}")
                table = self._db.open_table(table_name)
            else:
                logger.info(f"Creating new table: {table_name}")
                # Create table with schema
                table = self._db.create_table(
                    table_name,
                    schema=Document,
                    mode="create"
                )
                logger.info(f"Table '{table_name}' created successfully")
            
            return table
            
        except Exception as e:
            logger.error(f"Error getting/creating table '{table_name}': {e}")
            raise

    def add_documents(self, table_name: str, documents: list[dict]):
        """Add documents to table with automatic embedding.

        Args:
            table_name: Name of the table
            documents: List of document dictionaries

        Returns:
            Number of documents added
        """
        try:
            table = self.get_or_create_table(table_name)
            
            # Add timestamps if not present
            for doc in documents:
                if "created_at" not in doc or doc["created_at"] is None:
                    doc["created_at"] = datetime.utcnow().isoformat()
            
            # Add documents (embeddings will be generated automatically)
            table.add(documents)
            logger.info(f"Added {len(documents)} documents to '{table_name}'")
            return len(documents)
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    def search(self, table_name: str, query: str, limit: int = 10):
        """Perform vector similarity search.

        Args:
            table_name: Name of the table
            query: Search query text
            limit: Maximum number of results

        Returns:
            Search results as pandas DataFrame
        """
        try:
            table = self.get_or_create_table(table_name)
            
            # Perform vector search
            results = table.search(query).limit(limit).to_pandas()
            logger.info(f"Search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error performing search: {e}")
            raise

    def close(self):
        """Close database connection."""
        if self._db is not None:
            logger.info("Closing database connection")
            self._db = None

def main():
    """Main function demonstrating production setup."""
    try:
        # Initialize production database
        db_path = os.getenv("LANCEDB_PATH", "./data/lancedb")
        logger.info(f"Initializing database at: {db_path}")
        
        db = ProductionDB(db_path)
        db.connect()
        
        # Create table with proper error handling
        table_name = "documents"
        table = db.get_or_create_table(table_name)
        logger.info(f"Table '{table_name}' is ready")
        
        # Example: Add sample documents
        sample_docs = [
            {
                "id": "doc1",
                "text": "LanceDB is a vector database for AI applications",
                "metadata": "sample document"
            },
            {
                "id": "doc2",
                "text": "Vector search enables semantic similarity matching",
                "metadata": "sample document"
            }
        ]
        
        db.add_documents(table_name, sample_docs)
        
        # Example: Perform search
        results = db.search(table_name, "vector database", limit=5)
        logger.info(f"Search results:\n{results}")
        
        print("Production database ready")
        print(f"Database path: {db_path}")
        print(f"Table: {table_name}")
        print(f"Documents: {len(sample_docs)}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    main()