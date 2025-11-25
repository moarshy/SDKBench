"""CLI tool with LanceDB backend."""

import argparse
import os
from pathlib import Path
import lancedb

def get_default_db_path():
    """Get default database path in user home."""
    home = Path.home()
    db_dir = home / ".lancedb" / "data"
    db_dir.mkdir(parents=True, exist_ok=True)
    return str(db_dir)

def init_cli_database(path: str = None):
    """Initialize database for CLI."""
    db_path = path or get_default_db_path()
    return lancedb.connect(db_path)

# Initialize database
db = init_cli_database()

def main():
    """CLI main entry point."""
    parser = argparse.ArgumentParser(description="Vector DB CLI")
    parser.add_argument("--path", help="Database path")
    args = parser.parse_args()

    if args.path:
        global db
        db = init_cli_database(args.path)

    tables = db.table_names()
    print(f"CLI connected, {len(tables)} tables available")
    print("CLI tool ready")

if __name__ == "__main__":
    main()
