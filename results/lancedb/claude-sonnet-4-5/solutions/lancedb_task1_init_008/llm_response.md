I'll help you set up FastAPI with LanceDB using a lifespan context manager. Here's the complete solution:

```txt
# filepath: requirements.txt
pandas>=2.0.0
numpy>=1.24.0
fastapi>=0.104.0
uvicorn>=0.24.0
lancedb>=0.5.0
```

```python
# filepath: app.py
"""FastAPI with LanceDB using lifespan context manager."""

from contextlib import asynccontextmanager
from typing import Generator
import lancedb
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
import os


@asynccontextmanager
async def lifespan(app: FastAPI) -> Generator:
    """Lifespan context manager for FastAPI application.
    
    Handles startup and shutdown events:
    - Startup: Initialize LanceDB connection
    - Shutdown: Cleanup resources if needed
    """
    # Startup: Initialize database
    db_path = "./api_db"
    
    try:
        # Create database directory if it doesn't exist
        os.makedirs(db_path, exist_ok=True)
        
        # Connect to LanceDB
        app.state.db = lancedb.connect(db_path)
        
        print(f"✓ LanceDB connected successfully at {db_path}")
        print(f"✓ Available tables: {app.state.db.table_names()}")
        
    except Exception as e:
        print(f"✗ Failed to connect to LanceDB: {e}")
        raise
    
    yield
    
    # Shutdown: Cleanup if needed
    print("✓ Shutting down FastAPI application")
    # LanceDB connections are automatically cleaned up
    # but we can explicitly close if needed
    if hasattr(app.state, 'db'):
        del app.state.db


# Create FastAPI app with lifespan
app = FastAPI(
    title="FastAPI with LanceDB",
    description="API service with LanceDB vector database integration",
    version="1.0.0",
    lifespan=lifespan
)


def get_db() -> lancedb.DBConnection:
    """Dependency to get database from app state.
    
    Returns:
        lancedb.DBConnection: The database connection instance
        
    Raises:
        HTTPException: If database is not initialized
    """
    from fastapi import Request
    from starlette.requests import Request as StarletteRequest
    
    # Access the app state through the request context
    # This is a workaround since we can't directly access app.state in dependencies
    try:
        # We'll use a different approach - store db in a global or use request.app.state
        if not hasattr(app.state, 'db'):
            raise HTTPException(
                status_code=503,
                detail="Database not initialized"
            )
        return app.state.db
    except AttributeError:
        raise HTTPException(
            status_code=503,
            detail="Database connection not available"
        )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "FastAPI with LanceDB",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check(db: lancedb.DBConnection = Depends(get_db)):
    """Health check endpoint to verify database connectivity.
    
    Returns:
        dict: Health status including database information
    """
    try:
        # Verify database connection by listing tables
        tables = db.table_names()
        
        return {
            "status": "healthy",
            "database": {
                "connected": True,
                "path": "./api_db",
                "tables_count": len(tables),
                "tables": tables
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database health check failed: {str(e)}"
        )


@app.get("/db/info")
async def database_info(db: lancedb.DBConnection = Depends(get_db)):
    """Get detailed database information.
    
    Returns:
        dict: Database metadata and statistics
    """
    try:
        tables = db.table_names()
        
        tables_info = []
        for table_name in tables:
            try:
                table = db.open_table(table_name)
                tables_info.append({
                    "name": table_name,
                    "count": table.count_rows(),
                    "schema": str(table.schema)
                })
            except Exception as e:
                tables_info.append({
                    "name": table_name,
                    "error": str(e)
                })
        
        return {
            "database_path": "./api_db",
            "total_tables": len(tables),
            "tables": tables_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve database info: {str(e)}"
        )


def main():
    """Main entry point for the application."""
    print("=" * 50)
    print("FastAPI with LanceDB Service")
    print("=" * 50)
    print("\nStarting FastAPI service...")
    print("Database will be initialized on startup")
    print("\nEndpoints:")
    print("  - GET  /          : Root endpoint")
    print("  - GET  /health    : Health check")
    print("  - GET  /db/info   : Database information")
    print("  - GET  /docs      : API documentation")
    print("\nTo run the server:")
    print("  uvicorn app:app --reload")
    print("=" * 50)


if __name__ == "__main__":
    main()
```

## Key Features Implemented:

1. **LanceDB Integration**: Added `lancedb>=0.5.0` to requirements.txt

2. **Lifespan Context Manager**:
   - Initializes LanceDB connection on startup
   - Creates database directory if it doesn't exist
   - Stores connection in `app.state.db`
   - Handles cleanup on shutdown

3. **Database Dependency**:
   - `get_db()` function provides database access to endpoints
   - Includes error handling for uninitialized database

4. **Health Check Endpoints**:
   - `/health`: Verifies database connectivity and lists tables
   - `/db/info`: Provides detailed database information
   - `/`: Root endpoint with basic info

5. **Error Handling**:
   - Proper exception handling during initialization
   - HTTP exceptions for API errors
   - Informative error messages

## Usage:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app:app --reload

# Or run directly
python app.py  # Shows info, then run uvicorn separately
```

The database will be created at `./api_db` and the API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.