```txt
# filepath: requirements.txt
pandas>=2.0.0
numpy>=1.24.0
lancedb>=0.5.0
```

```python
# filepath: app.py
"""Async LanceDB connection pattern."""

import asyncio
from typing import Optional
import lancedb
from concurrent.futures import ThreadPoolExecutor


class AsyncLanceDB:
    """Async wrapper for LanceDB operations."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._db: Optional[lancedb.DBConnection] = None
        self._executor = ThreadPoolExecutor(max_workers=4)

    async def connect(self):
        """Async connect to database.

        Returns:
            self: The AsyncLanceDB instance for method chaining
        """
        loop = asyncio.get_event_loop()
        # Run sync connect in executor to avoid blocking
        self._db = await loop.run_in_executor(
            self._executor,
            lancedb.connect,
            self.db_path
        )
        return self

    async def create_table(self, table_name: str, data, mode: str = "create"):
        """Async create table.

        Args:
            table_name: Name of the table
            data: Data to insert (pandas DataFrame or list of dicts)
            mode: Creation mode ("create", "overwrite", etc.)

        Returns:
            Table object
        """
        if self._db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        loop = asyncio.get_event_loop()
        table = await loop.run_in_executor(
            self._executor,
            lambda: self._db.create_table(table_name, data, mode=mode)
        )
        return table

    async def open_table(self, table_name: str):
        """Async open existing table.

        Args:
            table_name: Name of the table to open

        Returns:
            Table object
        """
        if self._db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        loop = asyncio.get_event_loop()
        table = await loop.run_in_executor(
            self._executor,
            self._db.open_table,
            table_name
        )
        return table

    async def search(self, table_name: str, query_vector, limit: int = 10):
        """Async vector search.

        Args:
            table_name: Name of the table to search
            query_vector: Query vector for similarity search
            limit: Maximum number of results to return

        Returns:
            Search results as pandas DataFrame
        """
        if self._db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        loop = asyncio.get_event_loop()
        
        # Open table and perform search in executor
        def _search():
            table = self._db.open_table(table_name)
            return table.search(query_vector).limit(limit).to_pandas()
        
        results = await loop.run_in_executor(self._executor, _search)
        return results

    async def list_tables(self):
        """Async list all tables in database.

        Returns:
            List of table names
        """
        if self._db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        loop = asyncio.get_event_loop()
        tables = await loop.run_in_executor(
            self._executor,
            self._db.table_names
        )
        return tables

    async def close(self):
        """Close the database connection and executor."""
        self._executor.shutdown(wait=True)
        self._db = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


async def main():
    """Example usage of async LanceDB connection."""
    import pandas as pd
    import numpy as np
    
    # Create async connection using context manager
    async with AsyncLanceDB("./my_async_lancedb") as db:
        print("✓ Async connection established")
        
        # Create sample data with vectors
        sample_data = pd.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "vector": [
                np.random.rand(128).tolist(),
                np.random.rand(128).tolist(),
                np.random.rand(128).tolist(),
                np.random.rand(128).tolist(),
                np.random.rand(128).tolist()
            ],
            "text": ["doc1", "doc2", "doc3", "doc4", "doc5"]
        })
        
        # Create table asynchronously
        print("Creating table...")
        await db.create_table("test_table", sample_data, mode="overwrite")
        print("✓ Table created")
        
        # List tables
        tables = await db.list_tables()
        print(f"✓ Available tables: {tables}")
        
        # Perform async search
        query_vector = np.random.rand(128).tolist()
        print("Performing vector search...")
        results = await db.search("test_table", query_vector, limit=3)
        print(f"✓ Search completed, found {len(results)} results")
        print("\nTop results:")
        print(results[["id", "text"]].head())
        
        print("\n✓ Async connection ready and operational")


if __name__ == "__main__":
    asyncio.run(main())
```