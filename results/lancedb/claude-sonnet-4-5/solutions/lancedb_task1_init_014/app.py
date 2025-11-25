# filepath: app.py
"""Async LanceDB connection pattern."""

import asyncio
from typing import Optional
import lancedb
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import numpy as np


class AsyncLanceDB:
    """Async wrapper for LanceDB operations."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._db: Optional[lancedb.DBConnection] = None
        self._executor = ThreadPoolExecutor(max_workers=4)

    async def connect(self):
        """Async connect to database.

        Runs the synchronous lancedb.connect() in a thread executor
        to avoid blocking the event loop.

        Returns:
            self: The AsyncLanceDB instance for method chaining
        """
        loop = asyncio.get_event_loop()
        try:
            # Run sync connect in executor to avoid blocking
            self._db = await loop.run_in_executor(
                self._executor,
                lancedb.connect,
                self.db_path
            )
            print(f"Connected to LanceDB at: {self.db_path}")
            return self
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    async def create_table(
        self,
        table_name: str,
        data: pd.DataFrame,
        mode: str = "create"
    ):
        """Async create table.

        Args:
            table_name: Name of the table to create
            data: DataFrame with data to insert
            mode: Creation mode ('create', 'overwrite', 'append')

        Returns:
            The created table
        """
        if self._db is None:
            raise RuntimeError("Database not connected. Call connect() first.")

        loop = asyncio.get_event_loop()
        try:
            table = await loop.run_in_executor(
                self._executor,
                lambda: self._db.create_table(table_name, data, mode=mode)
            )
            print(f"Table '{table_name}' created successfully")
            return table
        except Exception as e:
            print(f"Error creating table: {e}")
            raise

    async def search(
        self,
        table_name: str,
        query_vector: list,
        limit: int = 10
    ):
        """Async vector search.

        Args:
            table_name: Name of the table to search
            query_vector: Query vector for similarity search
            limit: Maximum number of results to return

        Returns:
            Search results as a pandas DataFrame
        """
        if self._db is None:
            raise RuntimeError("Database not connected. Call connect() first.")

        loop = asyncio.get_event_loop()
        try:
            # Open table and perform search in executor
            def _search():
                table = self._db.open_table(table_name)
                return table.search(query_vector).limit(limit).to_pandas()

            results = await loop.run_in_executor(self._executor, _search)
            print(f"Search completed: {len(results)} results found")
            return results
        except Exception as e:
            print(f"Error during search: {e}")
            raise

    async def list_tables(self):
        """Async list all tables in the database.

        Returns:
            List of table names
        """
        if self._db is None:
            raise RuntimeError("Database not connected. Call connect() first.")

        loop = asyncio.get_event_loop()
        try:
            tables = await loop.run_in_executor(
                self._executor,
                self._db.table_names
            )
            return tables
        except Exception as e:
            print(f"Error listing tables: {e}")
            raise

    async def close(self):
        """Close the database connection and cleanup resources."""
        if self._executor:
            self._executor.shutdown(wait=True)
            print("Database connection closed")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


async def main():
    """Demonstrate async LanceDB operations."""
    # Create async connection using context manager
    async with AsyncLanceDB("./my_lancedb") as db:
        # Create sample data with vectors
        sample_data = pd.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "text": ["hello", "world", "lancedb", "async", "python"],
            "vector": [
                np.random.rand(128).tolist(),
                np.random.rand(128).tolist(),
                np.random.rand(128).tolist(),
                np.random.rand(128).tolist(),
                np.random.rand(128).tolist(),
            ]
        })

        # Create table
        await db.create_table("sample_table", sample_data, mode="overwrite")

        # List tables
        tables = await db.list_tables()
        print(f"Available tables: {tables}")

        # Perform async search
        query_vector = np.random.rand(128).tolist()
        results = await db.search("sample_table", query_vector, limit=3)
        print("\nSearch Results:")
        print(results[["id", "text", "_distance"]].head())

        print("\nAsync connection ready and operations completed!")


if __name__ == "__main__":
    asyncio.run(main())