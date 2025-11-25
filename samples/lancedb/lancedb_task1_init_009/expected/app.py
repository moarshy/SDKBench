"""Flask application with LanceDB."""

from flask import Flask, g
import lancedb

app = Flask(__name__)
app.config["LANCEDB_PATH"] = "./flask_db"

def get_db():
    """Get database connection."""
    if "db" not in g:
        g.db = lancedb.connect(app.config["LANCEDB_PATH"])
    return g.db

@app.route("/health")
def health():
    """Health check endpoint."""
    db = get_db()
    tables = db.table_names()
    return {"status": "healthy", "tables": len(tables)}

def main():
    print("Flask app ready")

if __name__ == "__main__":
    app.run(debug=True)
