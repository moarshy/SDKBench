"""Async LanceDB initialization."""

import asyncio
import lancedb

async def init_database():
    """Async database initialization."""
    # LanceDB connect is sync, but we wrap for async context
    db = lancedb.connect("./async_db")
    return db

db = None

async def main():
    """Async main entry point."""
    global db
    db = await init_database()
    tables = db.table_names()
    print(f"Async connected with {len(tables)} tables")
    print("Async app started")

if __name__ == "__main__":
    asyncio.run(main())
