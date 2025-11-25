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
def initialize_embedding_model(max_retries: int = 3):
    """Initialize embedding model with retry logic."""
    for attempt in range(max_retries):
        try:
            registry = EmbeddingFunctionRegistry.get_instance()
            model = registry.get("sentence-transformers").create(
                name="all-MiniLM-L6-v2",
                device="cpu"
            )
            logger.info("Embedding model initialized successfully")
            return model
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error("Failed to initialize embedding model after all retries")
                raise

# Initialize the model
model = initialize_embedding_model()

# Define production schema with all fields
class Document(LanceModel):
    """Production document schema with embeddings."""
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
        logger.info(f"Initialized ProductionDB with path: {db_path}")

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
                
                # Attempt connection
                self._db = lancedb.connect(self.db_path)
                logger.info(f"Successfully connected to database at {self.db_path}")
                
                # Verify connection by listing tables
                tables = self._db.table_names()
                logger.info(f"Found {len(tables)} existing tables: {tables}")
                
                return self._db
            
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1}/{retries} failed: {e}")
                if attempt < retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to connect after {retries} attempts")
                    raise Exception(f"Database connection failed: {e}")

    def get_or_create_table(self, table_name: str, sample_data: Optional[list] = None):
        """Get existing table or create new one.

        Args:
            table_name: Name of the table
            sample_data: Optional sample data for table creation

        Returns:
            LanceDB table object

        Raises:
            Exception: If database is not connected
        """
        if self._db is None:
            raise Exception("Database not connected. Call connect() first.")

        try:
            # Check if table exists
            if table_name in self._db.table_names():
                logger.info(f"Opening existing table: {table_name}")
                table = self._db.open_table(table_name)
                logger.info(f"Table '{table_name}' has {table.count_rows()} rows")
                return table
            
            # Create new table with schema
            logger.info(f"Creating new table: {table_name}")
            
            if sample_data is None:
                # Create with empty data but proper schema
                sample_data = [
                    {
                        "id": "sample_1",
                        "text": "This is a sample document for initialization",
                        "metadata": "sample",
                        "created_at": datetime.now().isoformat()
                    }
                ]
            
            table = self._db.create_table(
                table_name,
                schema=Document,
                data=sample_data,
                mode="overwrite"
            )
            
            logger.info(f"Table '{table_name}' created successfully with {table.count_rows()} rows")
            return table
        
        except Exception as e:
            logger.error(f"Error getting/creating table '{table_name}': {e}")
            raise

    def create_fts_index(self, table_name: str, column: str = "text"):
        """Create full-text search index on a column.

        Args:
            table_name: Name of the table
            column: Column to index for full-text search
        """
        try:
            table = self._db.open_table(table_name)
            table.create_fts_index(column)
            logger.info(f"Full-text search index created on '{column}' for table '{table_name}'")
        except Exception as e:
            logger.error(f"Error creating FTS index: {e}")
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
        db_path = os.getenv("LANCEDB_PATH", "./production_lancedb")
        logger.info(f"Starting production database initialization at {db_path}")
        
        db = ProductionDB(db_path)
        
        # Connect with retry logic
        db.connect(retries=3)
        
        # Create table with proper error handling
        table_name = "documents"
        sample_documents = [
            {
                "id": "doc_1",
                "text": "LanceDB is a developer-friendly vector database",
                "metadata": "introduction",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "doc_2",
                "text": "Vector search enables semantic similarity matching",
                "metadata": "features",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "doc_3",
                "text": "Production deployments require proper error handling",
                "metadata": "best_practices",
                "created_at": datetime.now().isoformat()
            }
        ]
        
        table = db.get_or_create_table(table_name, sample_documents)
        
        # Create full-text search index
        try:
            db.create_fts_index(table_name, "text")
        except Exception as e:
            logger.warning(f"FTS index creation skipped: {e}")
        
        # Verify setup
        logger.info(f"Table row count: {table.count_rows()}")
        logger.info("Production database ready")
        
        # Test vector search
        query_text = "database features"
        logger.info(f"Testing vector search with query: '{query_text}'")
        results = table.search(query_text).limit(2).to_pandas()
        logger.info(f"Search returned {len(results)} results")
        
        print("\n" + "="*50)
        print("Production database setup completed successfully!")
        print(f"Database path: {db_path}")
        print(f"Table name: {table_name}")
        print(f"Total documents: {table.count_rows()}")
        print("="*50 + "\n")
        
        return db, table
        
    except Exception as e:
        logger.error(f"Production setup failed: {e}")
        raise

if __name__ == "__main__":
    main()