"""FastAPI service with LanceDB backend."""

from fastapi import FastAPI, Depends
import lancedb

app = FastAPI(title="Vector Search API")

# Initialize database on startup
db = None

@app.on_event("startup")
async def startup():
    global db
    db = lancedb.connect("./api_data/lancedb")

def get_db():
    """Dependency to get database connection."""
    return db

@app.get("/health")
def health_check(db = Depends(get_db)):
    """Health check endpoint."""
    tables = db.table_names()
    return {"status": "healthy", "tables": len(tables)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    print("FastAPI service ready")
