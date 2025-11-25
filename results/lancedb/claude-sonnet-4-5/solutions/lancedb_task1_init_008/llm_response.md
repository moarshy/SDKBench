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
        # Create directory if it doesn't exist
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
    # LanceDB connections are automatically closed when the object is garbage collected
    # No explicit cleanup needed for LanceDB 0.5.0


# Create FastAPI app with lifespan
app = FastAPI(
    title="FastAPI with LanceDB",
    description="FastAPI application with LanceDB vector database integration",
    version="1.0.0",
    lifespan=lifespan
)


def get_db() -> lancedb.DBConnection:
    """Dependency to get database from app state.
    
    Returns:
        lancedb.DBConnection: The LanceDB connection instance
        
    Raises:
        HTTPException: If database connection is not available
    """
    try:
        db = app.state.db
        if db is None:
            raise HTTPException(
                status_code=503,
                detail="Database connection not available"
            )
        return db
    except AttributeError:
        raise HTTPException(
            status_code=503,
            detail="Database not initialized"
        )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "FastAPI with LanceDB",
        "status": "running"
    }


@app.get("/health")
async def health_check(db: lancedb.DBConnection = Depends(get_db)):
    """Health check endpoint.
    
    Verifies that the database connection is working and returns
    information about the database state.
    """
    try:
        # Get list of tables to verify connection is working
        tables = db.table_names()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "database": "connected",
                "tables_count": len(tables),
                "tables": tables
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database health check failed: {str(e)}"
        )


@app.get("/db/info")
async def database_info(db: lancedb.DBConnection = Depends(get_db)):
    """Get database information.
    
    Returns detailed information about the LanceDB instance.
    """
    try:
        tables = db.table_names()
        
        return {
            "database_path": "./api_db",
            "tables": tables,
            "table_count": len(tables),
            "status": "operational"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve database info: {str(e)}"
        )


def main():
    """Main entry point for the application."""
    print("FastAPI service ready")
    print("Starting server...")
    print("Access the API at: http://localhost:8000")
    print("Access the docs at: http://localhost:8000/docs")
    
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
```

## Summary

This solution provides:

1. **LanceDB Integration**: Added `lancedb>=0.5.0` to requirements.txt

2. **Lifespan Context Manager**: 
   - Initializes LanceDB connection on startup
   - Creates the database directory if it doesn't exist
   - Stores the connection in `app.state.db`
   - Handles cleanup on shutdown (automatic for LanceDB)

3. **Database Dependency**: 
   - `get_db()` function provides the database connection to endpoints
   - Includes proper error handling for missing connections

4. **Health Check Endpoints**:
   - `/` - Root endpoint
   - `/health` - Verifies database connection and returns table information
   - `/db/info` - Provides detailed database information

5. **Error Handling**: 
   - Proper exception handling throughout
   - HTTP 503 for service unavailable
   - HTTP 500 for internal errors

6. **Production Ready**:
   - Type hints for better code quality
   - Comprehensive docstrings
   - Logging for debugging
   - Uvicorn server configuration in main()

You can test the application by running:
```bash
pip install -r requirements.txt
python app.py
```

Then visit `http://localhost:8000/docs` to see the interactive API documentation.