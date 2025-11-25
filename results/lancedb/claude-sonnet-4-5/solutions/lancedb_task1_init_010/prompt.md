# System Prompt

You are an expert developer specializing in lancedb integration.
You are helping integrate lancedb (version 0.5.0) into a python application.


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

Task: Initialization
Schema with auto-embedding fields

Current project files:

=== requirements.txt ===
```
pandas>=2.0.0
numpy>=1.24.0

```

=== app.py ===
```
"""LanceDB with SourceField/VectorField auto-embedding schema."""

# TODO: Import lancedb
# TODO: Import EmbeddingFunctionRegistry from lancedb.embeddings
# TODO: Import LanceModel, Vector from lancedb.pydantic
# TODO: Import Optional from typing

# TODO: Initialize embedding model via registry
# registry = EmbeddingFunctionRegistry.get_instance()
# model = registry.get("sentence-transformers").create()

# TODO: Define schema with auto-embedding
# class Document(LanceModel):
#     text: str = model.SourceField()  # Text to embed
#     vector: Vector(model.ndims()) = model.VectorField()  # Auto-generated
#     metadata: Optional[str] = None

def create_table_with_schema(db, table_name: str):
    """Create table with auto-embedding schema.

    TODO:
        1. Create table with Document schema
        2. Data will auto-embed on insert
        3. Return table
    """
    pass

def main():
    # TODO: Connect to database
    # TODO: Create table with schema
    print("Schema with auto-embedding ready")

if __name__ == "__main__":
    main()

```


For this initialization task:
1. Import lancedb library
2. Create database connection with lancedb.connect()
3. Handle connection path appropriately
4. Verify connection is working

Please provide the complete solution by modifying the input files above.
Files to output: requirements.txt, app.py

CRITICAL: Each code block MUST start with a filepath comment on the first line:
- Python: # filepath: filename.py
- JavaScript/TypeScript: // filepath: filename.ts
- Other: # filepath: filename.ext
