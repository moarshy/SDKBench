"""Async LanceDB connection pattern."""

import asyncio
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import lancedb

class AsyncLanceDB:
    """Async wrapper for LanceDB operations."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._db: Optional[object] = None
        self._executor = ThreadPoolExecutor(max_workers=4)

    async def connect(self):
        """Async connect to database."""
        loop = asyncio.get_event_loop()
        self._db = await loop.run_in_executor(
            self._executor,
            lancedb.connect,
            self.db_path
        )
        return self

    async def table_names(self):
        """Async get table names."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._db.table_names
        )

    async def search(self, table_name: str, query_vector, limit: int = 10):
        """Async vector search."""
        loop = asyncio.get_event_loop()

        def _search():
            table = self._db.open_table(table_name)
            return table.search(query_vector).limit(limit).to_pandas()

        return await loop.run_in_executor(self._executor, _search)

# Global async database instance
async_db: Optional[AsyncLanceDB] = None

async def main():
    global async_db
    async_db = AsyncLanceDB("./async_db")
    await async_db.connect()

    tables = await async_db.table_names()
    print(f"Async connected with {len(tables)} tables")
    print("Async connection ready")

if __name__ == "__main__":
    asyncio.run(main())
