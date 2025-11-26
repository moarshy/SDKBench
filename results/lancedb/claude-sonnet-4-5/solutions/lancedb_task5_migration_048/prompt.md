# System Prompt

You are an expert developer specializing in lancedb integration.
You are helping integrate lancedb (version latest) into a python application.


LanceDB is a developer-friendly, serverless vector database for AI applications.

Key Concepts:
1. Connection: lancedb.connect() to create or open a database
2. Tables: Schema-defined collections storing vectors and metadata
3. Search: Vector similarity search, full-text search, and hybrid search
4. Embeddings: Integration with embedding models for vectorization

LanceDB Patterns:
- Connection: db = lancedb.connect("./my_lancedb")
- Create table: db.create_table("name", data)
- Open table: table = db.open_table("name")
- Vector search: table.search(query_vector).limit(k).to_pandas()
- Hybrid search: table.search(query_type="hybrid").vector(vec).text(text)
- Full-text search: table.create_fts_index("column"), table.search(text)

Common integrations:
- sentence-transformers for embeddings
- pandas for data manipulation
- pyarrow for efficient data types


Your responses should:
1. Provide working code that follows best practices
2. Include all necessary imports
3. Add appropriate error handling
4. Follow the framework's conventions
5. Be production-ready

IMPORTANT: You MUST output files with the EXACT same filenames as provided in the input.
- If the input has "app.py", your output must also be named "app.py"
- If the input has "middleware.ts", your output must also be named "middleware.ts"
- Do NOT create new filenames - modify the existing files

When providing code, ALWAYS specify the file path as a comment on the FIRST LINE inside each code block:
- For Python: # filepath: app.py
- For JavaScript/TypeScript: // filepath: middleware.ts
- For other files: # filepath: requirements.txt

Example format:
```python
# filepath: app.py
import lancedb
# rest of code...
```


---

# User Prompt

Task: Migration
Add new field with defaults

Current project files:

=== requirements.txt ===
```
lancedb>=0.5.0
pandas>=2.0.0

```

=== migration.py ===
```
"""Schema Migration: Add new field with defaults.

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

```


For this migration/upgrade task:
1. Update to new LanceDB API patterns
2. Handle schema changes
3. Migrate existing data
4. Update search patterns

Additional Context:
Migrating from lancedb previous to latest

Please provide the complete solution by modifying the input files above.
Files to output: requirements.txt, migration.py

CRITICAL: Each code block MUST start with a filepath comment on the first line:
- Python: # filepath: filename.py
- JavaScript/TypeScript: // filepath: filename.ts
- Other: # filepath: filename.ext
