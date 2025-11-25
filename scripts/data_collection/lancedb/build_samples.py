#!/usr/bin/env python3
"""
LanceDB Sample Construction Script

Builds 50 SDK-Bench samples for LanceDB across 5 task types using patterns from mined repositories.
Adapted from Clerk build_samples to follow the same POC process.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import click
from tqdm import tqdm


class LanceDBSampleBuilder:
    """Build SDK-Bench samples for LanceDB from mined repositories."""

    def __init__(self, patterns_file: Path, mined_repos_file: Path, output_dir: Path):
        """Initialize sample builder."""
        self.patterns = self._load_json(patterns_file)
        self.mined_repos = self._load_json(mined_repos_file)
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Sample counts per task type (50 total, same distribution as Clerk)
        self.task_counts = {
            1: 15,  # Initialization (connect to DB)
            2: 15,  # Data Operations (create table, add data)
            3: 10,  # Vector Search
            4: 7,   # Complete Pipeline (RAG)
            5: 3,   # Migration (schema changes)
        }

        # Common embedding models from patterns
        self.embedding_models = [
            "sentence-transformers/all-MiniLM-L6-v2",
            "BAAI/bge-small-en-v1.5",
            "sentence-transformers/all-mpnet-base-v2"
        ]

        # Common frameworks
        self.frameworks = ["streamlit", "fastapi", "flask", "python"]

    def _load_json(self, file_path: Path) -> Dict:
        """Load JSON file."""
        with open(file_path) as f:
            return json.load(f)

    def build_all_samples(self):
        """Build all 50 LanceDB samples."""
        print("\n🚀 SDK-Bench: LanceDB Sample Construction")
        print(f"   Output: {self.output_dir}")
        print(f"   Total samples: {sum(self.task_counts.values())}\n")

        samples_created = []
        sample_counter = 1

        for task_type, count in self.task_counts.items():
            print(f"\n📦 Building Task Type {task_type} samples ({count} samples)...")

            for i in range(count):
                sample_id = f"lancedb_task{task_type}_{self._task_name(task_type)}_{sample_counter:03d}"

                try:
                    sample_dir = self.output_dir / sample_id
                    self._create_sample(task_type, sample_id, sample_dir, i)
                    samples_created.append({
                        "sample_id": sample_id,
                        "task_type": task_type,
                        "sdk": "lancedb",
                        "created_at": datetime.now().isoformat()
                    })
                    print(f"   ✓ {sample_id}")
                    sample_counter += 1
                except Exception as e:
                    print(f"   ✗ Failed to create {sample_id}: {e}")

        # Save dataset manifest
        manifest = {
            "dataset_version": "1.0",
            "sdk": "lancedb",
            "created_at": datetime.now().isoformat(),
            "total_samples": len(samples_created),
            "by_task_type": {
                task_type: len([s for s in samples_created if s["task_type"] == task_type])
                for task_type in self.task_counts.keys()
            },
            "samples": samples_created
        }

        manifest_path = self.output_dir / "lancedb_dataset_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"\n✅ Created {len(samples_created)} LanceDB samples")
        print(f"   Manifest: {manifest_path}")

    def _task_name(self, task_type: int) -> str:
        """Get task type name."""
        names = {
            1: "init",
            2: "data_ops",
            3: "search",
            4: "pipeline",
            5: "migration"
        }
        return names[task_type]

    def _create_sample(self, task_type: int, sample_id: str, sample_dir: Path, index: int):
        """Create a single sample."""
        # Create directory structure
        input_dir = sample_dir / "input"
        expected_dir = sample_dir / "expected"
        tests_dir = sample_dir / "tests"

        for dir in [input_dir, expected_dir, tests_dir]:
            dir.mkdir(parents=True, exist_ok=True)

        # Build sample based on task type
        if task_type == 1:
            self._build_init_sample(sample_id, input_dir, expected_dir, tests_dir, index)
        elif task_type == 2:
            self._build_data_ops_sample(sample_id, input_dir, expected_dir, tests_dir, index)
        elif task_type == 3:
            self._build_search_sample(sample_id, input_dir, expected_dir, tests_dir, index)
        elif task_type == 4:
            self._build_pipeline_sample(sample_id, input_dir, expected_dir, tests_dir, index)
        elif task_type == 5:
            self._build_migration_sample(sample_id, input_dir, expected_dir, tests_dir, index)

    # ==================== Task Type 1: Initialization ====================

    def _build_init_sample(self, sample_id: str, input_dir: Path, expected_dir: Path, tests_dir: Path, index: int):
        """Build Task 1 (Initialization) sample."""
        # Different initialization scenarios with varying complexity
        init_scenarios = [
            {
                "name": "basic_connection",
                "description": "Basic LanceDB connection",
                "db_path": "./my_lancedb",
                "use_case": "simple app"
            },
            {
                "name": "cloud_storage",
                "description": "Connect to cloud-based LanceDB",
                "db_path": "s3://my-bucket/lancedb",
                "use_case": "cloud deployment"
            },
            {
                "name": "streamlit_app",
                "description": "Initialize LanceDB in Streamlit app",
                "db_path": "./streamlit_data/vectors",
                "use_case": "streamlit dashboard"
            },
            {
                "name": "fastapi_service",
                "description": "Initialize LanceDB in FastAPI service",
                "db_path": "./api_data/lancedb",
                "use_case": "REST API backend"
            },
            {
                "name": "config_based",
                "description": "Initialize from environment config",
                "db_path": "${LANCEDB_PATH}",
                "use_case": "configurable deployment"
            },
            {
                "name": "memory_mode",
                "description": "In-memory LanceDB for testing",
                "db_path": ":memory:",
                "use_case": "unit testing"
            },
            {
                "name": "async_init",
                "description": "Async initialization pattern",
                "db_path": "./async_db",
                "use_case": "async application"
            },
            {
                "name": "multi_tenant",
                "description": "Multi-tenant database setup",
                "db_path": "./tenants/{tenant_id}/db",
                "use_case": "SaaS application"
            },
            {
                "name": "with_schema",
                "description": "Initialize with predefined schema",
                "db_path": "./schema_db",
                "use_case": "typed application"
            },
            {
                "name": "embedding_ready",
                "description": "Initialize with embedding model",
                "db_path": "./embeddings_db",
                "use_case": "ML pipeline"
            },
            {
                "name": "cli_tool",
                "description": "Initialize in CLI application",
                "db_path": "~/.lancedb/data",
                "use_case": "command line tool"
            },
            {
                "name": "jupyter_notebook",
                "description": "Initialize for Jupyter notebook",
                "db_path": "./notebook_data",
                "use_case": "data analysis"
            },
            {
                "name": "flask_app",
                "description": "Initialize in Flask application",
                "db_path": "./flask_data/vectors",
                "use_case": "web application"
            },
            {
                "name": "background_worker",
                "description": "Initialize for background jobs",
                "db_path": "./worker_data/lancedb",
                "use_case": "job processor"
            },
            {
                "name": "microservice",
                "description": "Initialize for microservice",
                "db_path": "/data/lancedb",
                "use_case": "containerized service"
            }
        ]

        scenario = init_scenarios[index % len(init_scenarios)]

        # Create input files (without LanceDB)
        self._create_input_init(input_dir, scenario)

        # Create expected files (with LanceDB)
        self._create_expected_init(expected_dir, scenario)

        # Create test file
        self._create_test_init(tests_dir, scenario)

        # Create metadata
        metadata = self._create_metadata_init(sample_id, scenario)
        with open(expected_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def _create_input_init(self, input_dir: Path, scenario: Dict):
        """Create input files for initialization task."""
        name = scenario["name"]
        description = scenario["description"]
        use_case = scenario["use_case"]

        if name == "basic_connection":
            main_content = f'''"""Vector data application - {use_case}."""

# TODO: Import lancedb library

# TODO: Initialize database connection

def main():
    """Main entry point."""
    # TODO: Connect to vector database
    # TODO: List available tables

    print("Application started")

if __name__ == "__main__":
    main()
'''
        elif name == "cloud_storage":
            main_content = f'''"""Cloud-based vector storage application."""

# TODO: Import lancedb and configure cloud storage

# TODO: Set up AWS credentials or use environment variables

def get_cloud_db():
    """Get connection to cloud-hosted LanceDB.

    TODO:
        1. Configure S3 credentials
        2. Connect to cloud LanceDB
        3. Return database connection
    """
    pass

def main():
    """Main entry point for cloud app."""
    # TODO: Initialize cloud database connection
    # TODO: Verify connection

    print("Cloud app started")

if __name__ == "__main__":
    main()
'''
        elif name == "streamlit_app":
            main_content = f'''"""Streamlit dashboard with vector search."""

# TODO: Import streamlit and lancedb

# TODO: Use st.cache_resource for database connection

def get_database():
    """Get cached database connection.

    TODO:
        1. Use Streamlit caching
        2. Connect to LanceDB
        3. Return cached connection
    """
    pass

def main():
    """Streamlit app main."""
    # TODO: Set up page config
    # TODO: Initialize database
    # TODO: Display connection status

    print("Streamlit app ready")

if __name__ == "__main__":
    main()
'''
        elif name == "fastapi_service":
            main_content = f'''"""FastAPI service with LanceDB backend."""

# TODO: Import FastAPI and lancedb

# TODO: Create FastAPI app instance

# TODO: Initialize database on startup

def get_db():
    """Dependency to get database connection.

    TODO:
        1. Return database connection
        2. Handle connection errors
    """
    pass

def health_check():
    """Health check endpoint.

    TODO:
        1. Verify database connection
        2. Return health status
    """
    pass

if __name__ == "__main__":
    print("FastAPI service ready")
'''
        elif name == "config_based":
            main_content = f'''"""Configurable vector database application."""

import os

# TODO: Import lancedb

# TODO: Read configuration from environment

def get_db_path():
    """Get database path from configuration.

    TODO:
        1. Read LANCEDB_PATH from environment
        2. Provide default fallback
        3. Return configured path
    """
    pass

def initialize_database():
    """Initialize database with configuration.

    TODO:
        1. Get path from config
        2. Connect to LanceDB
        3. Return connection
    """
    pass

def main():
    """Main entry point."""
    # TODO: Initialize with config
    print("Configurable app started")

if __name__ == "__main__":
    main()
'''
        elif name == "memory_mode":
            main_content = f'''"""In-memory LanceDB for testing."""

# TODO: Import lancedb

# TODO: Set up in-memory database for tests

def create_test_db():
    """Create in-memory database for testing.

    TODO:
        1. Connect to in-memory LanceDB
        2. Return database instance
    """
    pass

def setup_test_data(db):
    """Set up test data in database.

    TODO:
        1. Create test table
        2. Insert sample data
    """
    pass

def main():
    """Test main."""
    # TODO: Create test database
    # TODO: Verify it works
    print("Test database ready")

if __name__ == "__main__":
    main()
'''
        elif name == "async_init":
            main_content = f'''"""Async LanceDB initialization."""

import asyncio

# TODO: Import lancedb

# TODO: Create async initialization function

async def init_database():
    """Async database initialization.

    TODO:
        1. Connect to LanceDB
        2. Initialize tables if needed
        3. Return connection
    """
    pass

async def main():
    """Async main entry point."""
    # TODO: Initialize database asynchronously
    # TODO: Run async operations

    print("Async app started")

if __name__ == "__main__":
    asyncio.run(main())
'''
        elif name == "multi_tenant":
            main_content = f'''"""Multi-tenant LanceDB setup."""

# TODO: Import lancedb

# TODO: Create tenant-specific database paths

def get_tenant_db(tenant_id: str):
    """Get database for specific tenant.

    Args:
        tenant_id: Unique tenant identifier

    TODO:
        1. Build tenant-specific path
        2. Connect to tenant database
        3. Return connection
    """
    pass

def create_tenant(tenant_id: str):
    """Create new tenant database.

    TODO:
        1. Create tenant directory
        2. Initialize database
        3. Set up default tables
    """
    pass

def main():
    """Multi-tenant main."""
    # TODO: Initialize for tenant
    print("Multi-tenant system ready")

if __name__ == "__main__":
    main()
'''
        elif name == "with_schema":
            main_content = f'''"""LanceDB with predefined schema."""

# TODO: Import lancedb and pydantic

# TODO: Define document schema class

# TODO: Initialize database with schema

def create_typed_table(db, table_name: str):
    """Create table with predefined schema.

    TODO:
        1. Define schema using LanceModel
        2. Create table with schema
        3. Return table reference
    """
    pass

def main():
    """Schema-based main."""
    # TODO: Initialize database
    # TODO: Create typed table
    print("Schema-based app ready")

if __name__ == "__main__":
    main()
'''
        elif name == "embedding_ready":
            main_content = f'''"""LanceDB with embedding model integration."""

# TODO: Import lancedb and sentence_transformers

# TODO: Initialize embedding model

# TODO: Initialize database connection

def get_embedding_model():
    """Get sentence transformer model.

    TODO:
        1. Load embedding model
        2. Return model instance
    """
    pass

def init_embedding_db():
    """Initialize database ready for embeddings.

    TODO:
        1. Connect to LanceDB
        2. Verify model compatibility
        3. Return db and model
    """
    pass

def main():
    """Embedding-ready main."""
    # TODO: Initialize model and database
    print("Embedding pipeline ready")

if __name__ == "__main__":
    main()
'''
        elif name == "cli_tool":
            main_content = f'''"""CLI tool with LanceDB backend."""

import argparse

# TODO: Import lancedb

# TODO: Set up argument parser

def get_default_db_path():
    """Get default database path in user home.

    TODO:
        1. Expand ~ to home directory
        2. Create directory if needed
        3. Return full path
    """
    pass

def init_cli_database(path: str = None):
    """Initialize database for CLI.

    TODO:
        1. Use provided path or default
        2. Connect to database
        3. Return connection
    """
    pass

def main():
    """CLI main entry point."""
    # TODO: Parse arguments
    # TODO: Initialize database
    print("CLI tool ready")

if __name__ == "__main__":
    main()
'''
        else:
            # Generic template for remaining scenarios
            main_content = f'''"""{description} - {use_case}."""

# TODO: Import lancedb and required libraries

# TODO: Set up database configuration

def initialize():
    """Initialize database connection.

    TODO:
        1. Configure database path
        2. Connect to LanceDB
        3. Return connection instance
    """
    pass

def verify_connection(db):
    """Verify database is accessible.

    TODO:
        1. List tables
        2. Check connection health
    """
    pass

def main():
    """Main entry point."""
    # TODO: Initialize database
    # TODO: Verify connection
    print("{use_case} ready")

if __name__ == "__main__":
    main()
'''

        with open(input_dir / "app.py", "w") as f:
            f.write(main_content)

        # Create requirements.txt without lancedb
        requirements = '''pandas==2.0.3
numpy==1.24.3
'''
        with open(input_dir / "requirements.txt", "w") as f:
            f.write(requirements)

    def _create_expected_init(self, expected_dir: Path, scenario: Dict):
        """Create expected files with LanceDB initialization."""
        name = scenario["name"]
        db_path = scenario["db_path"]
        use_case = scenario["use_case"]

        if name == "basic_connection":
            main_content = f'''"""Vector data application - {use_case}."""

import lancedb

# Initialize LanceDB connection
db = lancedb.connect("{db_path}")

def main():
    """Main entry point."""
    # List available tables
    tables = db.table_names()
    print(f"Connected to LanceDB at {db_path}")
    print(f"Available tables: {{tables}}")

    print("Application started")

if __name__ == "__main__":
    main()
'''
        elif name == "cloud_storage":
            main_content = f'''"""Cloud-based vector storage application."""

import lancedb
import os

# Configure cloud storage credentials
# AWS credentials should be set via environment variables:
# AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

def get_cloud_db():
    """Get connection to cloud-hosted LanceDB."""
    db = lancedb.connect("{db_path}")
    return db

# Initialize cloud database
db = get_cloud_db()

def main():
    """Main entry point for cloud app."""
    tables = db.table_names()
    print(f"Connected to cloud LanceDB: {db_path}")
    print(f"Tables: {{tables}}")
    print("Cloud app started")

if __name__ == "__main__":
    main()
'''
        elif name == "streamlit_app":
            main_content = f'''"""Streamlit dashboard with vector search."""

import streamlit as st
import lancedb

@st.cache_resource
def get_database():
    """Get cached database connection."""
    return lancedb.connect("{db_path}")

# Initialize cached database
db = get_database()

def main():
    """Streamlit app main."""
    st.set_page_config(page_title="Vector Search", layout="wide")
    st.title("Vector Search Dashboard")

    # Display connection status
    tables = db.table_names()
    st.success(f"Connected to LanceDB with {{len(tables)}} tables")

    print("Streamlit app ready")

if __name__ == "__main__":
    main()
'''
        elif name == "fastapi_service":
            main_content = f'''"""FastAPI service with LanceDB backend."""

from fastapi import FastAPI, Depends
import lancedb

app = FastAPI(title="Vector Search API")

# Initialize database on startup
db = None

@app.on_event("startup")
async def startup():
    global db
    db = lancedb.connect("{db_path}")

def get_db():
    """Dependency to get database connection."""
    return db

@app.get("/health")
def health_check(db = Depends(get_db)):
    """Health check endpoint."""
    tables = db.table_names()
    return {{"status": "healthy", "tables": len(tables)}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    print("FastAPI service ready")
'''
        elif name == "config_based":
            main_content = f'''"""Configurable vector database application."""

import os
import lancedb

# Read configuration from environment
DEFAULT_PATH = "./default_lancedb"

def get_db_path():
    """Get database path from configuration."""
    return os.environ.get("LANCEDB_PATH", DEFAULT_PATH)

def initialize_database():
    """Initialize database with configuration."""
    path = get_db_path()
    return lancedb.connect(path)

# Initialize with config
db = initialize_database()

def main():
    """Main entry point."""
    path = get_db_path()
    tables = db.table_names()
    print(f"Connected to {{path}} with {{len(tables)}} tables")
    print("Configurable app started")

if __name__ == "__main__":
    main()
'''
        elif name == "memory_mode":
            main_content = f'''"""In-memory LanceDB for testing."""

import lancedb

def create_test_db():
    """Create in-memory database for testing."""
    return lancedb.connect("{db_path}")

def setup_test_data(db):
    """Set up test data in database."""
    # Create a simple test table
    data = [{{"text": "test", "vector": [0.1] * 384}}]
    db.create_table("test_table", data, mode="overwrite")

# Initialize test database
db = create_test_db()

def main():
    """Test main."""
    setup_test_data(db)
    tables = db.table_names()
    print(f"Test database ready with {{len(tables)}} tables")

if __name__ == "__main__":
    main()
'''
        elif name == "async_init":
            main_content = f'''"""Async LanceDB initialization."""

import asyncio
import lancedb

async def init_database():
    """Async database initialization."""
    # LanceDB connect is sync, but we wrap for async context
    db = lancedb.connect("{db_path}")
    return db

db = None

async def main():
    """Async main entry point."""
    global db
    db = await init_database()
    tables = db.table_names()
    print(f"Async connected with {{len(tables)}} tables")
    print("Async app started")

if __name__ == "__main__":
    asyncio.run(main())
'''
        elif name == "multi_tenant":
            main_content = f'''"""Multi-tenant LanceDB setup."""

import os
import lancedb
from pathlib import Path

BASE_PATH = "./tenants"

def get_tenant_db(tenant_id: str):
    """Get database for specific tenant."""
    tenant_path = f"{{BASE_PATH}}/{{tenant_id}}/db"
    Path(tenant_path).parent.mkdir(parents=True, exist_ok=True)
    return lancedb.connect(tenant_path)

def create_tenant(tenant_id: str):
    """Create new tenant database."""
    db = get_tenant_db(tenant_id)
    # Initialize with default table
    data = [{{"text": "welcome", "vector": [0.0] * 384}}]
    db.create_table("documents", data, mode="overwrite")
    return db

def main():
    """Multi-tenant main."""
    # Example: create tenant
    tenant_db = create_tenant("tenant_001")
    print(f"Tenant database ready with {{len(tenant_db.table_names())}} tables")
    print("Multi-tenant system ready")

if __name__ == "__main__":
    main()
'''
        elif name == "with_schema":
            main_content = f'''"""LanceDB with predefined schema."""

import lancedb
from lancedb.pydantic import LanceModel, Vector
from typing import Optional

# Define document schema
class Document(LanceModel):
    text: str
    vector: Vector(384)
    category: Optional[str] = None
    timestamp: Optional[str] = None

# Initialize database
db = lancedb.connect("{db_path}")

def create_typed_table(table_name: str):
    """Create table with predefined schema."""
    # Create empty table with schema
    data = [Document(text="init", vector=[0.0] * 384)]
    table = db.create_table(table_name, data, mode="overwrite")
    return table

def main():
    """Schema-based main."""
    table = create_typed_table("documents")
    print(f"Created typed table with schema: {{Document.__fields__.keys()}}")
    print("Schema-based app ready")

if __name__ == "__main__":
    main()
'''
        elif name == "embedding_ready":
            main_content = f'''"""LanceDB with embedding model integration."""

import lancedb
from sentence_transformers import SentenceTransformer

# Initialize embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize database
db = lancedb.connect("{db_path}")

def get_embedding_model():
    """Get sentence transformer model."""
    return model

def init_embedding_db():
    """Initialize database ready for embeddings."""
    return db, model

def embed_text(text: str):
    """Generate embedding for text."""
    return model.encode(text).tolist()

def main():
    """Embedding-ready main."""
    db, model = init_embedding_db()
    # Test embedding
    test_vec = embed_text("test")
    print(f"Model dimension: {{len(test_vec)}}")
    print(f"Database tables: {{db.table_names()}}")
    print("Embedding pipeline ready")

if __name__ == "__main__":
    main()
'''
        elif name == "cli_tool":
            main_content = f'''"""CLI tool with LanceDB backend."""

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
    print(f"CLI connected, {{len(tables)}} tables available")
    print("CLI tool ready")

if __name__ == "__main__":
    main()
'''
        else:
            # Generic template for remaining scenarios
            main_content = f'''"""{scenario["description"]} - {use_case}."""

import lancedb

def initialize():
    """Initialize database connection."""
    return lancedb.connect("{db_path}")

def verify_connection(db):
    """Verify database is accessible."""
    tables = db.table_names()
    return len(tables) >= 0

# Initialize database
db = initialize()

def main():
    """Main entry point."""
    if verify_connection(db):
        print(f"Connected to {{db_path}}")
    print("{use_case} ready")

if __name__ == "__main__":
    main()
'''

        with open(expected_dir / "app.py", "w") as f:
            f.write(main_content)

        # Create requirements.txt with lancedb
        extra_deps = ""
        if name == "streamlit_app":
            extra_deps = "streamlit>=1.28.0\n"
        elif name == "fastapi_service":
            extra_deps = "fastapi>=0.104.0\nuvicorn>=0.24.0\n"
        elif name in ["with_schema", "embedding_ready"]:
            extra_deps = "sentence-transformers>=2.2.0\n"

        requirements = f'''lancedb==0.5.0
pandas==2.0.3
numpy==1.24.3
{extra_deps}'''
        with open(expected_dir / "requirements.txt", "w") as f:
            f.write(requirements)

    def _create_test_init(self, tests_dir: Path, scenario: Dict):
        """Create test file for initialization."""
        test_content = '''"""Tests for LanceDB initialization."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_lancedb_connection():
    """Test that LanceDB connection is established."""
    from expected import app

    # Check that db is initialized
    assert app.db is not None

    # Check connection method was called
    assert hasattr(app.db, 'table_names')

def test_main_function():
    """Test main function runs without errors."""
    from expected import app

    # Should run without raising exceptions
    app.main()
'''
        with open(tests_dir / "test_init.py", "w") as f:
            f.write(test_content)

    def _create_metadata_init(self, sample_id: str, scenario: Dict) -> Dict:
        """Create metadata for initialization task."""
        return {
            "sample_id": sample_id,
            "task_type": 1,
            "task_name": "initialization",
            "sdk": "lancedb",
            "lancedb_version": "0.5.0",
            "framework": "python",
            "difficulty": "easy" if scenario["name"] in ["basic_connection", "memory_mode"] else "medium",
            "estimated_lines": 15,
            "description": scenario["description"],
            "scenario": scenario["name"],
            "use_case": scenario["use_case"],
            "ground_truth": {
                "ingredients": {
                    "initialization": {
                        "location": "app.py",
                        "pattern": "lancedb.connect",
                        "imports": ["lancedb"]
                    },
                    "configuration": {
                        "db_path": scenario["db_path"],
                        "connection_method": "lancedb.connect"
                    }
                }
            },
            "evaluation_targets": {
                "i_acc": {
                    "correct_file": "app.py",
                    "correct_pattern": "lancedb.connect",
                    "correct_imports": ["import lancedb"]
                },
                "c_comp": {
                    "required_components": 2,
                    "components": ["import", "connection"]
                },
                "ipa": {
                    "integration_points": ["lancedb.connect", "table_names"]
                },
                "f_corr": {
                    "test_command": "pytest tests/test_init.py",
                    "expected_pass": True
                }
            }
        }

    # ==================== Task Type 2: Data Operations ====================

    def _build_data_ops_sample(self, sample_id: str, input_dir: Path, expected_dir: Path, tests_dir: Path, index: int):
        """Build Task 2 (Data Operations) sample."""
        # Vary table names
        table_names = ["documents", "embeddings", "vectors", "items", "records"]
        table_name = table_names[index % len(table_names)]

        # Create input/expected files
        self._create_input_data_ops(input_dir)
        self._create_expected_data_ops(expected_dir, table_name)
        self._create_test_data_ops(tests_dir, table_name)

        # Create metadata
        metadata = self._create_metadata_data_ops(sample_id, table_name)
        with open(expected_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def _create_input_data_ops(self, input_dir: Path):
        """Create input files for data operations task."""
        content = '''"""Data management for vector database."""

import pandas as pd
import numpy as np

# TODO: Connect to database

def create_sample_data():
    """Create sample data for testing."""
    data = [
        {"id": 1, "text": "Hello world", "category": "greeting"},
        {"id": 2, "text": "Python programming", "category": "tech"},
        {"id": 3, "text": "Machine learning", "category": "tech"}
    ]
    return pd.DataFrame(data)

def store_data(df):
    """Store data in vector database."""
    # TODO: Create table and add data
    pass

def main():
    """Main function."""
    df = create_sample_data()
    # TODO: Add vector column
    store_data(df)
    print(f"Stored {len(df)} records")

if __name__ == "__main__":
    main()
'''
        with open(input_dir / "data_ops.py", "w") as f:
            f.write(content)

    def _create_expected_data_ops(self, expected_dir: Path, table_name: str):
        """Create expected files with data operations."""
        content = f'''"""Data management for vector database."""

import pandas as pd
import numpy as np
import lancedb
from lancedb.pydantic import LanceModel, Vector

# Connect to database
db = lancedb.connect("./my_lancedb")

class Document(LanceModel):
    """Document schema with vector."""
    id: int
    text: str
    category: str
    vector: Vector(384)  # 384-dimensional vector

def create_sample_data():
    """Create sample data for testing."""
    data = [
        {{"id": 1, "text": "Hello world", "category": "greeting"}},
        {{"id": 2, "text": "Python programming", "category": "tech"}},
        {{"id": 3, "text": "Machine learning", "category": "tech"}}
    ]
    return pd.DataFrame(data)

def store_data(df):
    """Store data in vector database."""
    # Add random vectors for demo (in production, use real embeddings)
    df["vector"] = [np.random.randn(384).tolist() for _ in range(len(df))]

    # Create or open table
    table = db.create_table(
        "{table_name}",
        data=df,
        mode="overwrite"
    )

    return table

def main():
    """Main function."""
    df = create_sample_data()
    table = store_data(df)
    print(f"Stored {{len(df)}} records in '{{table.name}}' table")

if __name__ == "__main__":
    main()
'''
        with open(expected_dir / "data_ops.py", "w") as f:
            f.write(content)

        # Add requirements
        requirements = '''lancedb==0.5.0
pandas==2.0.3
numpy==1.24.3
pydantic==2.0.0
'''
        with open(expected_dir / "requirements.txt", "w") as f:
            f.write(requirements)

    def _create_test_data_ops(self, tests_dir: Path, table_name: str):
        """Create test for data operations."""
        test_content = f'''"""Tests for data operations."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_table_creation():
    """Test that table is created."""
    from expected import data_ops

    # Run main to create table
    data_ops.main()

    # Check table exists
    tables = data_ops.db.table_names()
    assert "{table_name}" in tables

def test_schema_definition():
    """Test Document schema is defined."""
    from expected.data_ops import Document

    # Check schema has required fields
    assert hasattr(Document, "__fields__")
'''
        with open(tests_dir / "test_data_ops.py", "w") as f:
            f.write(test_content)

    def _create_metadata_data_ops(self, sample_id: str, table_name: str) -> Dict:
        """Create metadata for data operations task."""
        return {
            "sample_id": sample_id,
            "task_type": 2,
            "task_name": "data_operations",
            "sdk": "lancedb",
            "lancedb_version": "0.5.0",
            "framework": "python",
            "difficulty": "medium",
            "estimated_lines": 40,
            "description": "Create table schema and store data with vectors in LanceDB",
            "ground_truth": {
                "ingredients": {
                    "table_operations": {
                        "table_name": table_name,
                        "operations": ["create_table", "add"],
                        "schema": "LanceModel"
                    },
                    "vector_config": {
                        "dimension": 384,
                        "field_name": "vector"
                    }
                }
            },
            "evaluation_targets": {
                "i_acc": {
                    "correct_pattern": "create_table",
                    "correct_imports": ["import lancedb", "from lancedb.pydantic"]
                },
                "c_comp": {
                    "required_components": 4,
                    "components": ["schema", "connection", "table_creation", "vectors"]
                }
            }
        }

    # ==================== Task Type 3: Vector Search ====================

    def _build_search_sample(self, sample_id: str, input_dir: Path, expected_dir: Path, tests_dir: Path, index: int):
        """Build Task 3 (Vector Search) sample."""
        # Vary search parameters
        limits = [5, 10, 20]
        limit = limits[index % len(limits)]

        self._create_input_search(input_dir)
        self._create_expected_search(expected_dir, limit)
        self._create_test_search(tests_dir)

        metadata = self._create_metadata_search(sample_id, limit)
        with open(expected_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def _create_input_search(self, input_dir: Path):
        """Create input files for search task."""
        content = '''"""Vector similarity search implementation."""

# TODO: Import necessary libraries

def search_similar(query_text, k=5):
    """Search for similar documents."""
    # TODO: Implement vector search
    pass

def main():
    """Test search functionality."""
    results = search_similar("machine learning", k=10)
    print(f"Found results")

if __name__ == "__main__":
    main()
'''
        with open(input_dir / "search.py", "w") as f:
            f.write(content)

    def _create_expected_search(self, expected_dir: Path, limit: int):
        """Create expected search implementation."""
        content = f'''"""Vector similarity search implementation."""

import lancedb
import numpy as np
from sentence_transformers import SentenceTransformer

# Initialize
db = lancedb.connect("./my_lancedb")
model = SentenceTransformer("all-MiniLM-L6-v2")

def search_similar(query_text, k={limit}):
    """Search for similar documents."""
    # Open table
    table = db.open_table("documents")

    # Generate query embedding
    query_vector = model.encode(query_text).tolist()

    # Perform vector search
    results = table.search(query_vector).limit(k).to_pandas()

    return results

def main():
    """Test search functionality."""
    results = search_similar("machine learning", k={limit})
    print(f"Found {{len(results)}} similar documents")
    for idx, row in results.iterrows():
        print(f"  - {{row['text'][:50]}}... (score: {{row['_distance']:.3f}})")

if __name__ == "__main__":
    main()
'''
        with open(expected_dir / "search.py", "w") as f:
            f.write(content)

    def _create_test_search(self, tests_dir: Path):
        """Create test for search."""
        test_content = '''"""Tests for vector search."""

import pytest

def test_search_function():
    """Test search returns results."""
    from expected import search

    # Mock search should return pandas DataFrame
    # In real test, would use mock data
    pass
'''
        with open(tests_dir / "test_search.py", "w") as f:
            f.write(test_content)

    def _create_metadata_search(self, sample_id: str, limit: int) -> Dict:
        """Create metadata for search task."""
        return {
            "sample_id": sample_id,
            "task_type": 3,
            "task_name": "vector_search",
            "sdk": "lancedb",
            "description": "Implement vector similarity search using LanceDB",
            "ground_truth": {
                "ingredients": {
                    "search_operations": {
                        "method": "table.search",
                        "limit": limit,
                        "embedding_model": "all-MiniLM-L6-v2"
                    }
                }
            }
        }

    # ==================== Task Type 4: Complete RAG Pipeline ====================

    def _build_pipeline_sample(self, sample_id: str, input_dir: Path, expected_dir: Path, tests_dir: Path, index: int):
        """Build Task 4 (Complete RAG Pipeline) sample."""
        # Vary pipeline types
        pipeline_types = [
            ("document_qa", "Document Q&A"),
            ("semantic_search", "Semantic Search API"),
            ("chatbot", "RAG Chatbot"),
            ("multimodal", "Multi-modal Search"),
            ("streaming", "Streaming RAG"),
            ("hybrid", "Hybrid Search"),
            ("reranking", "Search with Reranking")
        ]
        pipeline_type, pipeline_name = pipeline_types[index % len(pipeline_types)]

        self._create_input_pipeline(input_dir, pipeline_type, pipeline_name)
        self._create_expected_pipeline(expected_dir, pipeline_type, pipeline_name)
        self._create_test_pipeline(tests_dir, pipeline_type)

        metadata = self._create_metadata_pipeline(sample_id, pipeline_type, pipeline_name)
        with open(expected_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def _create_input_pipeline(self, input_dir: Path, pipeline_type: str, pipeline_name: str):
        """Create input files for pipeline task."""
        content = f'''"""{pipeline_name} Pipeline.

Build a complete {pipeline_name.lower()} system using LanceDB for vector storage.
"""

# TODO: Import required libraries (lancedb, sentence_transformers, etc.)

# TODO: Define document schema with vector field

# TODO: Initialize database connection

def ingest_documents(documents: list):
    """Ingest documents into the vector database.

    Args:
        documents: List of document dictionaries with 'text' field

    TODO:
        1. Generate embeddings for each document
        2. Create or update table with documents
        3. Return number of documents ingested
    """
    pass

def search(query: str, k: int = 5):
    """Search for relevant documents.

    Args:
        query: Search query text
        k: Number of results to return

    TODO:
        1. Generate query embedding
        2. Perform vector similarity search
        3. Return top-k results
    """
    pass

def generate_response(query: str, context: list):
    """Generate response using retrieved context.

    Args:
        query: User query
        context: Retrieved documents

    TODO:
        1. Format context for prompt
        2. Return formatted response (mock LLM call)
    """
    pass

def run_pipeline(query: str):
    """Run the complete RAG pipeline.

    TODO:
        1. Search for relevant documents
        2. Generate response with context
        3. Return final answer
    """
    pass

def main():
    """Example usage of the pipeline."""
    # Sample documents
    sample_docs = [
        {{"text": "LanceDB is a vector database for AI applications."}},
        {{"text": "Vector search enables semantic similarity matching."}},
        {{"text": "RAG combines retrieval with generation for better answers."}}
    ]

    # TODO: Ingest documents
    # TODO: Run query through pipeline
    # TODO: Print results

    print("Pipeline ready")

if __name__ == "__main__":
    main()
'''
        with open(input_dir / "pipeline.py", "w") as f:
            f.write(content)

        # Requirements
        with open(input_dir / "requirements.txt", "w") as f:
            f.write("lancedb>=0.5.0\nsentence-transformers>=2.2.0\npandas>=2.0.0\n")

    def _create_expected_pipeline(self, expected_dir: Path, pipeline_type: str, pipeline_name: str):
        """Create expected pipeline implementation."""
        content = f'''"""{pipeline_name} Pipeline.

Complete {pipeline_name.lower()} system using LanceDB for vector storage.
"""

import lancedb
import pandas as pd
from lancedb.pydantic import LanceModel, Vector
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

# Initialize embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Define document schema
class Document(LanceModel):
    text: str
    vector: Vector(384)  # Dimension for all-MiniLM-L6-v2
    metadata: str = ""

# Initialize database
db = lancedb.connect("./rag_pipeline_db")

def ingest_documents(documents: List[Dict[str, Any]]) -> int:
    """Ingest documents into the vector database.

    Args:
        documents: List of document dictionaries with 'text' field

    Returns:
        Number of documents ingested
    """
    # Generate embeddings
    texts = [doc["text"] for doc in documents]
    embeddings = model.encode(texts).tolist()

    # Prepare data for insertion
    data = [
        Document(
            text=doc["text"],
            vector=emb,
            metadata=doc.get("metadata", "")
        )
        for doc, emb in zip(documents, embeddings)
    ]

    # Create or overwrite table
    table = db.create_table("documents", data, mode="overwrite")

    return len(data)

def search(query: str, k: int = 5) -> pd.DataFrame:
    """Search for relevant documents.

    Args:
        query: Search query text
        k: Number of results to return

    Returns:
        DataFrame with search results
    """
    # Generate query embedding
    query_vector = model.encode(query).tolist()

    # Open table and search
    table = db.open_table("documents")
    results = table.search(query_vector).limit(k).to_pandas()

    return results

def generate_response(query: str, context: List[Dict]) -> str:
    """Generate response using retrieved context.

    Args:
        query: User query
        context: Retrieved documents

    Returns:
        Generated response string
    """
    # Format context
    context_text = "\\n".join([f"- {{doc['text']}}" for doc in context])

    # Mock LLM response (in production, call actual LLM)
    response = f"Based on the retrieved information:\\n{{context_text}}\\n\\nAnswer: This is a response to '{{query}}' using the above context."

    return response

def run_pipeline(query: str, k: int = 3) -> str:
    """Run the complete RAG pipeline.

    Args:
        query: User query
        k: Number of documents to retrieve

    Returns:
        Generated response
    """
    # Step 1: Retrieve relevant documents
    results = search(query, k=k)

    # Step 2: Convert to list of dicts
    context = results.to_dict('records')

    # Step 3: Generate response
    response = generate_response(query, context)

    return response

def main():
    """Example usage of the pipeline."""
    # Sample documents
    sample_docs = [
        {{"text": "LanceDB is a vector database for AI applications.", "metadata": "overview"}},
        {{"text": "Vector search enables semantic similarity matching.", "metadata": "feature"}},
        {{"text": "RAG combines retrieval with generation for better answers.", "metadata": "concept"}},
        {{"text": "Embeddings convert text into numerical vectors.", "metadata": "concept"}},
        {{"text": "LanceDB supports multiple embedding models.", "metadata": "feature"}}
    ]

    # Ingest documents
    count = ingest_documents(sample_docs)
    print(f"Ingested {{count}} documents")

    # Run query through pipeline
    query = "What is LanceDB?"
    response = run_pipeline(query)

    print(f"\\nQuery: {{query}}")
    print(f"\\nResponse:\\n{{response}}")

if __name__ == "__main__":
    main()
'''
        with open(expected_dir / "pipeline.py", "w") as f:
            f.write(content)

        # Requirements
        with open(expected_dir / "requirements.txt", "w") as f:
            f.write("lancedb>=0.5.0\nsentence-transformers>=2.2.0\npandas>=2.0.0\npydantic>=2.0.0\n")

    def _create_test_pipeline(self, tests_dir: Path, pipeline_type: str):
        """Create test for pipeline."""
        content = '''"""Tests for RAG pipeline."""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_document_ingestion():
    """Test document ingestion."""
    from expected import pipeline

    docs = [{"text": "Test document"}]
    count = pipeline.ingest_documents(docs)
    assert count == 1

def test_search_returns_results():
    """Test search functionality."""
    from expected import pipeline

    # Ingest first
    docs = [{"text": "LanceDB is great"}]
    pipeline.ingest_documents(docs)

    # Search
    results = pipeline.search("LanceDB", k=1)
    assert len(results) > 0

def test_pipeline_end_to_end():
    """Test complete pipeline."""
    from expected import pipeline

    # Ingest
    docs = [{"text": "Test content for pipeline"}]
    pipeline.ingest_documents(docs)

    # Run pipeline
    response = pipeline.run_pipeline("test query")
    assert isinstance(response, str)
    assert len(response) > 0
'''
        with open(tests_dir / "test_pipeline.py", "w") as f:
            f.write(content)

    def _create_metadata_pipeline(self, sample_id: str, pipeline_type: str, pipeline_name: str) -> Dict:
        """Create metadata for pipeline task."""
        return {
            "sample_id": sample_id,
            "task_type": 4,
            "task_name": "complete_pipeline",
            "sdk": "lancedb",
            "lancedb_version": "0.5.0",
            "framework": "python",
            "difficulty": "hard",
            "estimated_lines": 100,
            "description": f"Build a complete {pipeline_name} using LanceDB",
            "pipeline_type": pipeline_type,
            "ground_truth": {
                "ingredients": {
                    "database_operations": ["connect", "create_table", "open_table", "search"],
                    "embedding_model": "sentence-transformers",
                    "schema_definition": True,
                    "functions": ["ingest_documents", "search", "generate_response", "run_pipeline"]
                }
            },
            "evaluation_targets": {
                "i_acc": {
                    "correct_pattern": "complete_pipeline",
                    "correct_imports": ["import lancedb", "from sentence_transformers", "from lancedb.pydantic"]
                },
                "c_comp": {
                    "required_components": 6,
                    "components": ["imports", "schema", "connection", "ingestion", "search", "pipeline"]
                }
            }
        }

    # ==================== Task Type 5: Schema Migration ====================

    def _build_migration_sample(self, sample_id: str, input_dir: Path, expected_dir: Path, tests_dir: Path, index: int):
        """Build Task 5 (Schema Migration) sample."""
        # Vary migration scenarios
        migration_types = [
            ("add_field", "Add new field to schema"),
            ("change_dimension", "Change vector dimension"),
            ("rename_table", "Rename table with data preservation")
        ]
        migration_type, migration_name = migration_types[index % len(migration_types)]

        self._create_input_migration(input_dir, migration_type, migration_name)
        self._create_expected_migration(expected_dir, migration_type, migration_name)
        self._create_test_migration(tests_dir, migration_type)

        metadata = self._create_metadata_migration(sample_id, migration_type, migration_name)
        with open(expected_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def _create_input_migration(self, input_dir: Path, migration_type: str, migration_name: str):
        """Create input files for migration task."""
        content = f'''"""Schema Migration: {migration_name}.

Migrate existing LanceDB table to new schema while preserving data.
"""

# TODO: Import required libraries

# Old schema (before migration)
# class OldDocument:
#     text: str
#     vector: Vector(384)

# TODO: Define new schema with changes

def connect_database():
    """Connect to existing database.

    TODO: Establish connection to LanceDB
    """
    pass

def backup_data(table_name: str):
    """Backup existing table data.

    TODO:
        1. Open existing table
        2. Read all data to DataFrame
        3. Return backup data
    """
    pass

def migrate_data(old_data, new_schema):
    """Transform data to match new schema.

    TODO:
        1. Transform each record to new schema
        2. Handle missing fields with defaults
        3. Return transformed data
    """
    pass

def create_new_table(table_name: str, data):
    """Create new table with migrated data.

    TODO:
        1. Drop old table if exists
        2. Create table with new schema
        3. Insert migrated data
    """
    pass

def verify_migration(table_name: str, expected_count: int):
    """Verify migration was successful.

    TODO:
        1. Check table exists
        2. Verify record count matches
        3. Verify new schema fields
    """
    pass

def run_migration():
    """Execute the complete migration.

    TODO:
        1. Backup existing data
        2. Transform to new schema
        3. Create new table
        4. Verify migration
    """
    pass

if __name__ == "__main__":
    run_migration()
'''
        with open(input_dir / "migration.py", "w") as f:
            f.write(content)

        with open(input_dir / "requirements.txt", "w") as f:
            f.write("lancedb>=0.5.0\npandas>=2.0.0\n")

    def _create_expected_migration(self, expected_dir: Path, migration_type: str, migration_name: str):
        """Create expected migration implementation."""
        # Different implementations based on migration type
        if migration_type == "add_field":
            new_field = "category: str = 'uncategorized'"
            transform_logic = '''# Add default category field
        transformed.append({
            "text": record["text"],
            "vector": record["vector"],
            "category": "migrated"  # Default value for new field
        })'''
        elif migration_type == "change_dimension":
            new_field = "vector: Vector(768)  # Changed from 384"
            transform_logic = '''# Pad or truncate vector to new dimension
        old_vector = record["vector"]
        if len(old_vector) < 768:
            new_vector = old_vector + [0.0] * (768 - len(old_vector))
        else:
            new_vector = old_vector[:768]
        transformed.append({
            "text": record["text"],
            "vector": new_vector
        })'''
        else:  # rename_table
            new_field = "content: str  # Renamed from 'text'"
            transform_logic = '''# Rename text field to content
        transformed.append({
            "content": record["text"],
            "vector": record["vector"]
        })'''

        content = f'''"""Schema Migration: {migration_name}.

Migrate existing LanceDB table to new schema while preserving data.
"""

import lancedb
import pandas as pd
from lancedb.pydantic import LanceModel, Vector
from typing import List, Dict, Any

# New schema (after migration)
class NewDocument(LanceModel):
    {"content" if migration_type == "rename_table" else "text"}: str
    {new_field}

# Database connection
db = lancedb.connect("./migration_db")

def connect_database():
    """Connect to existing database."""
    return db

def backup_data(table_name: str) -> pd.DataFrame:
    """Backup existing table data.

    Args:
        table_name: Name of table to backup

    Returns:
        DataFrame with all table data
    """
    try:
        table = db.open_table(table_name)
        backup = table.to_pandas()
        print(f"Backed up {{len(backup)}} records from {{table_name}}")
        return backup
    except Exception as e:
        print(f"No existing table to backup: {{e}}")
        return pd.DataFrame()

def migrate_data(old_data: pd.DataFrame) -> List[Dict[str, Any]]:
    """Transform data to match new schema.

    Args:
        old_data: DataFrame with old schema data

    Returns:
        List of records matching new schema
    """
    transformed = []

    for _, record in old_data.iterrows():
        {transform_logic}

    print(f"Transformed {{len(transformed)}} records")
    return transformed

def create_new_table(table_name: str, data: List[Dict[str, Any]]):
    """Create new table with migrated data.

    Args:
        table_name: Name for new table
        data: Migrated data records
    """
    # Convert to LanceModel instances
    documents = [NewDocument(**d) for d in data]

    # Create table (overwrite if exists)
    table = db.create_table(table_name, documents, mode="overwrite")
    print(f"Created table {{table_name}} with {{len(documents)}} records")
    return table

def verify_migration(table_name: str, expected_count: int) -> bool:
    """Verify migration was successful.

    Args:
        table_name: Name of migrated table
        expected_count: Expected number of records

    Returns:
        True if verification passes
    """
    table = db.open_table(table_name)
    actual_count = len(table.to_pandas())

    if actual_count != expected_count:
        print(f"Count mismatch: expected {{expected_count}}, got {{actual_count}}")
        return False

    print(f"Migration verified: {{actual_count}} records")
    return True

def run_migration():
    """Execute the complete migration."""
    table_name = "documents"

    print("Starting migration...")

    # Step 1: Backup existing data
    old_data = backup_data(table_name)

    if old_data.empty:
        # Create sample data for demonstration
        print("Creating sample data for migration demo...")
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")

        sample_texts = ["Sample document 1", "Sample document 2", "Sample document 3"]
        embeddings = model.encode(sample_texts).tolist()

        old_data = pd.DataFrame({{
            "text": sample_texts,
            "vector": embeddings
        }})

    expected_count = len(old_data)

    # Step 2: Transform to new schema
    migrated_data = migrate_data(old_data)

    # Step 3: Create new table
    create_new_table(table_name, migrated_data)

    # Step 4: Verify migration
    success = verify_migration(table_name, expected_count)

    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed verification!")

    return success

if __name__ == "__main__":
    run_migration()
'''
        with open(expected_dir / "migration.py", "w") as f:
            f.write(content)

        with open(expected_dir / "requirements.txt", "w") as f:
            f.write("lancedb>=0.5.0\npandas>=2.0.0\nsentence-transformers>=2.2.0\n")

    def _create_test_migration(self, tests_dir: Path, migration_type: str):
        """Create test for migration."""
        content = '''"""Tests for schema migration."""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_backup_returns_dataframe():
    """Test backup function."""
    from expected import migration
    import pandas as pd

    backup = migration.backup_data("nonexistent_table")
    assert isinstance(backup, pd.DataFrame)

def test_migrate_data_transforms():
    """Test data transformation."""
    from expected import migration
    import pandas as pd

    # Create test data
    test_data = pd.DataFrame({
        "text": ["test"],
        "vector": [[0.1] * 384]
    })

    result = migration.migrate_data(test_data)
    assert len(result) == 1

def test_full_migration():
    """Test complete migration process."""
    from expected import migration

    success = migration.run_migration()
    assert success is True
'''
        with open(tests_dir / "test_migration.py", "w") as f:
            f.write(content)

    def _create_metadata_migration(self, sample_id: str, migration_type: str, migration_name: str) -> Dict:
        """Create metadata for migration task."""
        return {
            "sample_id": sample_id,
            "task_type": 5,
            "task_name": "schema_migration",
            "sdk": "lancedb",
            "lancedb_version": "0.5.0",
            "framework": "python",
            "difficulty": "hard",
            "estimated_lines": 80,
            "description": migration_name,
            "migration_type": migration_type,
            "ground_truth": {
                "ingredients": {
                    "database_operations": ["connect", "open_table", "create_table", "to_pandas"],
                    "migration_steps": ["backup", "transform", "create", "verify"],
                    "error_handling": True
                }
            },
            "evaluation_targets": {
                "i_acc": {
                    "correct_pattern": "schema_migration",
                    "correct_imports": ["import lancedb", "import pandas"]
                },
                "c_comp": {
                    "required_components": 5,
                    "components": ["backup", "transform", "create", "verify", "run"]
                }
            }
        }


@click.command()
@click.option(
    "--patterns-file",
    default="data/lancedb/patterns.json",
    help="Path to patterns JSON file",
)
@click.option(
    "--mined-repos",
    default="data/lancedb/mined-repos.json",
    help="Path to mined repositories JSON",
)
@click.option(
    "--output-dir",
    default="samples/lancedb",
    help="Output directory for samples",
)
def main(patterns_file: str, mined_repos: str, output_dir: str):
    """Build LanceDB SDK-Bench samples."""
    builder = LanceDBSampleBuilder(
        Path(patterns_file),
        Path(mined_repos),
        Path(output_dir)
    )
    builder.build_all_samples()


if __name__ == "__main__":
    main()