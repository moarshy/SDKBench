"""FastAPI with LanceDB using lifespan context manager."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
import lancedb

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    # Startup: Initialize database
    app.state.db = lancedb.connect("./api_db")
    print("Database initialized")
    yield
    # Shutdown: Cleanup if needed
    print("Shutting down")

# Create FastAPI app with lifespan
app = FastAPI(title="Vector Search API", lifespan=lifespan)

def get_db(request: Request):
    """Dependency to get database from app state."""
    return request.app.state.db

@app.get("/health")
def health_check(db=Depends(get_db)):
    """Health check endpoint."""
    tables = db.table_names()
    return {"status": "healthy", "tables": len(tables)}

def main():
    print("FastAPI service ready")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
