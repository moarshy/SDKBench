"""FastAPI with LanceDB using lifespan context manager."""

from contextlib import asynccontextmanager

# TODO: Import FastAPI
# TODO: Import lancedb

# TODO: Define lifespan context manager
# @asynccontextmanager
# async def lifespan(app):
#     # Startup: Initialize database
#     app.state.db = lancedb.connect("./api_db")
#     yield
#     # Shutdown: Cleanup if needed

# TODO: Create FastAPI app with lifespan
# app = FastAPI(lifespan=lifespan)

def get_db():
    """Dependency to get database from app state.

    TODO:
        1. Access app.state.db
        2. Return database connection
    """
    pass

# TODO: Create health check endpoint

def main():
    print("FastAPI service ready")

if __name__ == "__main__":
    main()
