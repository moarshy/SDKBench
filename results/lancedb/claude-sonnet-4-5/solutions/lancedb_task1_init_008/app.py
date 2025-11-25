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
    print("✓ Shutting down LanceDB connection")
    # LanceDB connections are automatically cleaned up
    # but we can perform any additional cleanup here if needed


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
        # Get list of tables to verify connection is working
        tables = db.table_names()
        
        return {
            "status": "healthy",
            "database": "connected",
            "tables_count": len(tables),
            "tables": tables
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database health check failed: {str(e)}"
        )


@app.get("/db/info")
async def database_info(db: lancedb.DBConnection = Depends(get_db)):
    """Get database information.
    
    Returns:
        dict: Database metadata and statistics
    """
    try:
        tables = db.table_names()
        
        return {
            "database_path": "./api_db",
            "total_tables": len(tables),
            "table_names": tables,
            "connection_status": "active"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve database info: {str(e)}"
        )


def main():
    """Main entry point for the application."""
    print("=" * 50)
    print("FastAPI service with LanceDB")
    print("=" * 50)
    print("\nStarting server...")
    print("Documentation available at: http://localhost:8000/docs")
    print("Health check at: http://localhost:8000/health")
    print("\nPress CTRL+C to stop the server")
    print("=" * 50)
    
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